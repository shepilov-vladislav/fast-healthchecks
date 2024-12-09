"""This module provides a health check class for URLs.

Classes:
    UrlHealthCheck: A class to perform health checks on URLs.

Usage:
    The UrlHealthCheck class can be used to perform health checks on URLs by calling it.

Example:
    health_check = UrlHealthCheck(
        url="https://www.google.com",
    )
    result = await health_check()
    print(result.healthy)
"""

from http import HTTPStatus
from traceback import format_exc
from typing import TYPE_CHECKING

from fast_healthchecks.checks._base import DEFAULT_HC_TIMEOUT, HealthCheck
from fast_healthchecks.models import HealthCheckResult

IMPORT_ERROR_MSG = "httpx is not installed. Install it with `pip install httpx`."

try:
    from httpx import AsyncClient, AsyncHTTPTransport, BasicAuth, Response
except ImportError as exc:
    raise ImportError(IMPORT_ERROR_MSG) from exc

if TYPE_CHECKING:
    from httpx._types import URLTypes


class UrlHealthCheck(HealthCheck[HealthCheckResult]):
    """A class to perform health checks on URLs.

    Attributes:
        _name: The name of the health check.
        _password: The password to authenticate with.
        _timeout: The timeout for the connection.
        _url: The URL to connect to.
        _username: The user to authenticate with.
        _verify_ssl: Whether to verify the SSL certificate.
    """

    __slots__ = (
        "_auth",
        "_follow_redirects",
        "_name",
        "_password",
        "_timeout",
        "_transport",
        "_url",
        "_username",
        "_verify_ssl",
    )

    _url: "URLTypes"
    _username: str | None
    _password: str | None
    _auth: BasicAuth | None
    _verify_ssl: bool
    _transport: AsyncHTTPTransport | None
    _follow_redirects: bool
    _timeout: float
    _name: str

    def __init__(  # noqa: PLR0913, D417
        self,
        *,
        url: "URLTypes",
        username: str | None = None,
        password: str | None = None,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        timeout: float = DEFAULT_HC_TIMEOUT,
        name: str = "HTTP",
    ) -> None:
        """Initializes the health check.

        Args:
            url: The URL to connect to.
            username: The user to authenticate with.
            password: The password to authenticate with.
            verify_ssl: Whether to verify the SSL certificate.
            timeout: The timeout for the connection.
            name: The name of the health check.
        """
        self._url = url
        self._username = username
        self._password = password
        self._auth = BasicAuth(self._username, self._password or "") if self._username else None
        self._verify_ssl = verify_ssl
        self._transport = AsyncHTTPTransport(verify=self._verify_ssl) if self._verify_ssl else None
        self._follow_redirects = follow_redirects
        self._timeout = timeout
        self._name = name

    async def __call__(self) -> HealthCheckResult:
        """Performs the health check.

        Returns:
            A HealthCheckResult object with the result of the health check.
        """
        try:
            async with AsyncClient(
                auth=self._auth,
                timeout=self._timeout,
                transport=self._transport,
                follow_redirects=self._follow_redirects,
            ) as client:
                response: Response = await client.get(self._url)
                if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR or (
                    self._username and response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}
                ):
                    response.raise_for_status()
                return HealthCheckResult(name=self._name, healthy=response.is_success)
        except BaseException:  # noqa: BLE001
            return HealthCheckResult(name=self._name, healthy=False, error_details=format_exc())
