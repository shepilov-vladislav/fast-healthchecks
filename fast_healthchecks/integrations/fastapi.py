"""FastAPI integration for health checks."""

from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import Response

from fast_healthchecks.integrations.base import HandlerType, Probe, default_handler, make_probe_asgi


class HealthcheckRouter(APIRouter):
    """A router for health checks.

    Args:
        probes: An iterable of probes to run.
        debug: Whether to include the probes in the schema. Defaults to False.
    """

    def __init__(  # noqa: PLR0913
        self,
        *probes: Probe,
        success_handler: HandlerType = default_handler,
        failure_handler: HandlerType = default_handler,
        success_status: int = status.HTTP_204_NO_CONTENT,
        failure_status: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        debug: bool = False,
        prefix: str = "/health",
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize the router."""
        kwargs["prefix"] = prefix  # type: ignore[assignment]
        kwargs["tags"] = ["Healthchecks"]  # type: ignore[assignment]
        super().__init__(**kwargs)  # type: ignore[arg-type]
        for probe in probes:
            self._add_probe_route(
                probe,
                success_handler=success_handler,
                failure_handler=failure_handler,
                success_status=success_status,
                failure_status=failure_status,
                debug=debug,
            )

    def _add_probe_route(  # noqa: PLR0913
        self,
        probe: Probe,
        *,
        success_handler: HandlerType = default_handler,
        failure_handler: HandlerType = default_handler,
        success_status: int = status.HTTP_204_NO_CONTENT,
        failure_status: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        debug: bool = False,
    ) -> None:
        probe_handler = make_probe_asgi(
            probe,
            success_handler=success_handler,
            failure_handler=failure_handler,
            success_status=success_status,
            failure_status=failure_status,
            debug=debug,
        )

        async def handle_request() -> Response:
            content, headers, status_code = await probe_handler()
            return Response(content=content, status_code=status_code, headers=headers)

        self.add_api_route(
            path=f"/{probe.name}",
            endpoint=handle_request,
            status_code=success_status,
            summary=probe.endpoint_summary,
            include_in_schema=debug,
        )
