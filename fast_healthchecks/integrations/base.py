"""Base classes for integrations."""

import asyncio
import json
import re
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import asdict
from http import HTTPStatus
from typing import Any, NamedTuple, TypeAlias

from fast_healthchecks.checks import Check
from fast_healthchecks.models import HealthcheckReport, HealthCheckResult

HandlerType: TypeAlias = Callable[["ProbeAsgiResponse"], Awaitable[dict[str, str]]]


class Probe(NamedTuple):
    """A probe is a collection of health checks that can be run together.

    Args:
        name: The name of the probe.
        checks: An iterable of health checks to run.
        summary: A summary of the probe. If not provided, a default summary will be generated.
    """

    name: str
    checks: Iterable[Check]
    summary: str | None = None

    @property
    def endpoint_summary(self) -> str:
        """Return a summary for the endpoint.

        If a summary is provided, it will be used. Otherwise, a default summary will be generated.
        """
        if self.summary:
            return self.summary
        title = re.sub(
            pattern=r"[^a-z0-9]+",
            repl=" ",
            string=self.name.lower().capitalize(),
            flags=re.IGNORECASE,
        )
        return f"{title} probe"


class ProbeAsgiResponse(NamedTuple):
    """A response from an ASGI probe.

    Args:
        body: The body of the response.
        status_code: The status code of the response.
    """

    data: dict[str, str]
    healthy: bool


async def default_handler(response: ProbeAsgiResponse) -> Any:  # noqa: ANN401
    """Default handler for health check route.

    Args:
        response: The response from the probe.

    Returns:
        The response data.
    """


class ProbeAsgi:
    """An ASGI probe.

    Args:
        probe: The probe to run.
        success_handler: The handler to use for successful responses.
        failure_handler: The handler to use for failed responses.
        success_status: The status code to use for successful responses.
        failure_status: The status code to use for failed responses.
        debug: Whether to include debug information in the response.
    """

    __slots__ = (
        "_debug",
        "_exclude_fields",
        "_failure_handler",
        "_failure_status",
        "_map_handler",
        "_map_status",
        "_probe",
        "_success_handler",
        "_success_status",
    )

    _probe: Probe
    _success_handler: HandlerType
    _failure_handler: HandlerType
    _success_status: int
    _failure_status: int
    _debug: bool
    _exclude_fields: set[str]
    _map_status: dict[bool, int]
    _map_handler: dict[bool, HandlerType]

    def __init__(  # noqa: PLR0913
        self,
        probe: Probe,
        *,
        success_handler: HandlerType = default_handler,
        failure_handler: HandlerType = default_handler,
        success_status: int = HTTPStatus.NO_CONTENT,
        failure_status: int = HTTPStatus.SERVICE_UNAVAILABLE,
        debug: bool = False,
    ) -> None:
        """Initialize the ASGI probe."""
        self._probe = probe
        self._success_handler = success_handler
        self._failure_handler = failure_handler
        self._success_status = success_status
        self._failure_status = failure_status
        self._debug = debug
        self._exclude_fields: set[str] = {"allow_partial_failure", "error_details"} if not debug else set()
        self._map_status: dict[bool, int] = {True: success_status, False: failure_status}
        self._map_handler: dict[bool, HandlerType] = {True: success_handler, False: failure_handler}

    async def __call__(self) -> tuple[bytes, dict[str, str] | None, int]:
        """Run the probe.

        Returns:
            A tuple containing the response body, headers, and status code.
        """
        tasks = [check() for check in self._probe.checks]
        results: list[HealthCheckResult] = await asyncio.gather(*tasks)
        report = HealthcheckReport(results=results)
        response = ProbeAsgiResponse(
            data=asdict(
                report,
                dict_factory=lambda x: {k: v for (k, v) in x if k not in self._exclude_fields},
            ),
            healthy=report.healthy,
        )

        content_needed = not (
            (response.healthy and self._success_status < HTTPStatus.OK)
            or self._success_status
            in {
                HTTPStatus.NO_CONTENT,
                HTTPStatus.NOT_MODIFIED,
            }
        )

        content = b""
        headers = None
        if content_needed:
            handler = self._map_handler[response.healthy]
            content_ = await handler(response)
            content = json.dumps(
                content_,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")
            headers = {
                "content-type": "application/json",
                "content-length": str(len(content)),
            }

        return content, headers, self._map_status[response.healthy]


def make_probe_asgi(  # noqa: PLR0913
    probe: Probe,
    *,
    success_handler: HandlerType = default_handler,
    failure_handler: HandlerType = default_handler,
    success_status: int = HTTPStatus.NO_CONTENT,
    failure_status: int = HTTPStatus.SERVICE_UNAVAILABLE,
    debug: bool = False,
) -> Callable[[], Awaitable[Any]]:
    """Create an ASGI probe from a probe.

    Args:
        probe: The probe to create the ASGI probe from.
        success_handler: The handler to use for successful responses.
        failure_handler: The handler to use for failed responses.
        success_status: The status code to use for successful responses.
        failure_status: The status code to use for failed responses.
        debug: Whether to include debug information in the response.

    Returns:
        An ASGI probe.
    """
    return ProbeAsgi(
        probe,
        success_handler=success_handler,
        failure_handler=failure_handler,
        success_status=success_status,
        failure_status=failure_status,
        debug=debug,
    )
