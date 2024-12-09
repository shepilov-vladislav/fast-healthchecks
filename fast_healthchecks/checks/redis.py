"""This module provides a health check class for Redis.

Classes:
    RedisHealthCheck: A class to perform health checks on Redis.

Usage:
    The RedisHealthCheck class can be used to perform health checks on Redis by calling it.

Example:
    health_check = RedisHealthCheck(
        host="localhost",
        port=6379,
    )
    result = await health_check()
    print(result.healthy)
"""

from traceback import format_exc
from typing import TYPE_CHECKING, TypeAlias, TypedDict

from fast_healthchecks.checks._base import DEFAULT_HC_TIMEOUT, HealthCheckDSN
from fast_healthchecks.compat import PYDANTIC_INSTALLED
from fast_healthchecks.models import HealthCheckResult

IMPORT_ERROR_MSG = "redis is not installed. Install it with `pip install redis`."

try:
    from redis.asyncio import Redis
    from redis.asyncio.connection import parse_url
except ImportError as exc:
    raise ImportError(IMPORT_ERROR_MSG) from exc

if TYPE_CHECKING:
    from redis.asyncio.connection import ConnectKwargs


if PYDANTIC_INSTALLED:
    from pydantic import RedisDsn
else:  # pragma: no cover
    RedisDsn: TypeAlias = str  # type: ignore[no-redef]


class ParseDSNResult(TypedDict, total=True):
    """A dictionary containing the results of parsing a DSN."""

    parse_result: "ConnectKwargs"


class RedisHealthCheck(HealthCheckDSN[HealthCheckResult]):
    """A class to perform health checks on Redis.

    Attributes:
        _database: The database to connect to.
        _host: The host to connect to.
        _name: The name of the health check.
        _password: The password to authenticate with.
        _port: The port to connect to.
        _timeout: The timeout for the connection.
        _user: The user to authenticate with.
    """

    __slots__ = (
        "_database",
        "_host",
        "_name",
        "_password",
        "_port",
        "_timeout",
        "_user",
    )

    _host: str
    _port: int
    _database: str | int
    _user: str | None
    _password: str | None
    _timeout: float | None
    _name: str

    def __init__(  # noqa: PLR0913
        self,
        *,
        host: str = "localhost",
        port: int = 6379,
        database: str | int = 0,
        user: str | None = None,
        password: str | None = None,
        timeout: float | None = DEFAULT_HC_TIMEOUT,
        name: str = "Redis",
    ) -> None:
        """Initialize the RedisHealthCheck class.

        Args:
            host: The host to connect to.
            port: The port to connect to.
            database: The database to connect to.
            user: The user to authenticate with.
            password: The password to authenticate with.
            timeout: The timeout for the connection.
            name: The name of the health check.
        """
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password
        self._timeout = timeout
        self._name = name

    @classmethod
    def parse_dsn(cls, dsn: str) -> ParseDSNResult:
        """Parse the DSN and return the results.

        Args:
            dsn (str): The DSN to parse.

        Returns:
            ParseDSNResult: The results of parsing the DSN.
        """
        parse_result: "ConnectKwargs" = parse_url(str(dsn))  # noqa: UP037
        return {"parse_result": parse_result}

    @classmethod
    def from_dsn(
        cls,
        dsn: "RedisDsn | str",
        *,
        name: str = "Redis",
        timeout: float = DEFAULT_HC_TIMEOUT,
    ) -> "RedisHealthCheck":
        """Create a RedisHealthCheck instance from a DSN.

        Args:
            dsn: The DSN to connect to.
            name: The name of the health check.
            timeout: The timeout for the connection.

        Returns:
            A RedisHealthCheck instance.
        """
        dsn = cls.validate_dsn(dsn, type_=RedisDsn)
        parsed_dsn = cls.parse_dsn(dsn)
        parse_result = parsed_dsn["parse_result"]
        return RedisHealthCheck(
            host=parse_result.get("host", "localhost"),
            port=parse_result.get("port", 6379),
            database=parse_result.get("db", 0),
            user=parse_result.get("username"),
            password=parse_result.get("password"),
            timeout=timeout,
            name=name,
        )

    async def __call__(self) -> HealthCheckResult:
        """Perform a health check on Redis.

        Returns:
            A HealthCheckResult instance.
        """
        try:
            async with Redis(
                host=self._host,
                port=self._port,
                db=self._database,
                username=self._user,
                password=self._password,
                socket_timeout=self._timeout,
                single_connection_client=True,
            ) as redis:
                healthy: bool = await redis.ping()
                return HealthCheckResult(name=self._name, healthy=healthy)
        except BaseException:  # noqa: BLE001
            return HealthCheckResult(name=self._name, healthy=False, error_details=format_exc())
