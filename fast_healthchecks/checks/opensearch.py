"""This module provides a health check class for OpenSearch.

Classes:
    OpenSearchHealthCheck: A class to perform health checks on OpenSearch.

Usage:
    The OpenSearchHealthCheck class can be used to perform health checks on OpenSearch by calling it.

Example:
    health_check = OpenSearchHealthCheck(
        hosts=["localhost:9200"],
        http_auth=("username", "password"),
        use_ssl=True,
        verify_certs=True,
        ssl_show_warn=False,
        ca_certs="/path/to/ca.pem",
    )
    result = await health_check()
    print(result.healthy)
"""

from traceback import format_exc
from typing import Any

from fast_healthchecks.checks._base import DEFAULT_HC_TIMEOUT, HealthCheck
from fast_healthchecks.models import HealthCheckResult

IMPORT_ERROR_MSG = "opensearch-py is not installed. Install it with `pip install opensearch-py`."

try:
    from opensearchpy import AsyncOpenSearch
except ImportError as exc:
    raise ImportError(IMPORT_ERROR_MSG) from exc


class OpenSearchHealthCheck(HealthCheck[HealthCheckResult]):
    """A class to perform health checks on OpenSearch.

    Attributes:
        _hosts: The OpenSearch hosts.
        _name: The name of the health check.
        _http_auth: The HTTP authentication.
        _use_ssl: Whether to use SSL or not.
        _verify_certs: Whether to verify certificates or not.
        _ssl_show_warn: Whether to show SSL warnings or not.
        _ca_certs: The CA certificates.
        _timeout: The timeout for the health check.
    """

    __slots__ = (
        "_ca_certs",
        "_hosts",
        "_http_auth",
        "_name",
        "_ssl_show_warn",
        "_timeout",
        "_use_ssl",
        "_verify_certs",
    )

    _hosts: list[str]
    _http_auth: tuple[str, str] | None
    _use_ssl: bool
    _verify_certs: bool
    _ssl_show_warn: bool
    _ca_certs: str | None
    _timeout: float
    _name: str

    def __init__(  # noqa: PLR0913
        self,
        *,
        hosts: list[str],
        http_auth: tuple[str, str] | None = None,
        use_ssl: bool = False,
        verify_certs: bool = False,
        ssl_show_warn: bool = False,
        ca_certs: str | None = None,
        timeout: float = DEFAULT_HC_TIMEOUT,
        name: str = "OpenSearch",
    ) -> None:
        """Initializes the OpenSearchHealthCheck object.

        Args:
            hosts: The OpenSearch hosts.
            http_auth: The HTTP authentication.
            use_ssl: Whether to use SSL or not.
            verify_certs: Whether to verify certificates or not.
            ssl_show_warn: Whether to show SSL warnings or not.
            ca_certs: The CA certificates.
            timeout: The timeout for the health check.
            name: The name of the health check.
        """
        self._hosts = hosts
        self._http_auth = http_auth
        self._use_ssl = use_ssl
        self._verify_certs = verify_certs
        self._ssl_show_warn = ssl_show_warn
        self._ca_certs = ca_certs
        self._timeout = timeout
        self._name = name

    async def __call__(self) -> HealthCheckResult:
        """Performs the health check on OpenSearch.

        Returns:
            A HealthCheckResult object.
        """
        client = AsyncOpenSearch(
            hosts=self._hosts,
            http_auth=self._http_auth,
            use_ssl=self._use_ssl,
            verify_certs=self._verify_certs,
            ssl_show_warn=self._ssl_show_warn,
            ca_certs=self._ca_certs,
        )
        try:
            info = await client.info()
            return HealthCheckResult(name=self._name, healthy=info["version"]["number"] is not None)
        except BaseException:  # noqa: BLE001
            return HealthCheckResult(name=self._name, healthy=False, error_details=format_exc())
        finally:
            await client.close()

    def to_dict(self) -> dict[str, Any]:
        """Converts the OpenSearchHealthCheck object to a dictionary.

        Returns:
            A dictionary with the OpenSearchHealthCheck attributes.
        """
        return {
            "hosts": self._hosts,
            "http_auth": self._http_auth,
            "use_ssl": self._use_ssl,
            "verify_certs": self._verify_certs,
            "ssl_show_warn": self._ssl_show_warn,
            "ca_certs": self._ca_certs,
            "timeout": self._timeout,
            "name": self._name,
        }
