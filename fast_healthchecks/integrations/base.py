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

    async def probe_asgi() -> tuple[bytes, dict[str, str] | None, int]:
        exclude_fields: set[str] = {"allow_partial_failure", "error_details"} if not debug else set()
        map_status: dict[bool, int] = {True: success_status, False: failure_status}
        map_handler: dict[bool, HandlerType] = {True: success_handler, False: failure_handler}

        tasks = [check() for check in probe.checks]
        results: list[HealthCheckResult] = await asyncio.gather(*tasks)
        report = HealthcheckReport(results=results)
        response = ProbeAsgiResponse(
            data=asdict(
                report,
                dict_factory=lambda x: {k: v for (k, v) in x if k not in exclude_fields},
            ),
            healthy=report.healthy,
        )

        content_needed = not (
            (response.healthy and success_status < HTTPStatus.OK)
            or success_status
            in {
                HTTPStatus.NO_CONTENT,
                HTTPStatus.NOT_MODIFIED,
            }
        )

        content = b""
        headers = None
        if content_needed:
            handler = map_handler[response.healthy]
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

        return content, headers, map_status[response.healthy]

    return probe_asgi
