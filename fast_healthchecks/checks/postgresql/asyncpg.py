"""This module provides a health check class for PostgreSQL using asyncpg.

Classes:
    PostgreSQLAsyncPGHealthCheck: A class to perform health checks on a PostgreSQL database using asyncpg.

Usage:
    The PostgreSQLAsyncPGHealthCheck class can be used to perform health checks on a PostgreSQL database by
    connecting to the database and executing a simple query.

Example:
    health_check = PostgreSQLAsyncPGHealthCheck(
        host="localhost",
        port=5432,
        user="username",
        password="password",
        database="dbname"
    )
    # or
    health_check = PostgreSQLAsyncPGHealthCheck.from_dsn(
        "postgresql://username:password@localhost:5432/dbname",
    )
    result = await health_check()
    print(result.healthy)
"""

import ssl
from traceback import format_exc
from typing import TYPE_CHECKING, TypeAlias

from fast_healthchecks.checks._base import DEFAULT_HC_TIMEOUT
from fast_healthchecks.checks.postgresql.base import BasePostgreSQLHealthCheck
from fast_healthchecks.compat import PYDANTIC_INSTALLED
from fast_healthchecks.models import HealthCheckResult

IMPORT_ERROR_MSG = "asyncpg is not installed. Install it with `pip install asyncpg`."

try:
    import asyncpg
except ImportError as exc:
    raise ImportError(IMPORT_ERROR_MSG) from exc

if TYPE_CHECKING:
    from asyncpg.connection import Connection


if PYDANTIC_INSTALLED:
    from pydantic import PostgresDsn
else:  # pragma: no cover
    PostgresDsn: TypeAlias = str  # type: ignore[no-redef]


class PostgreSQLAsyncPGHealthCheck(BasePostgreSQLHealthCheck[HealthCheckResult]):
    """Health check class for PostgreSQL using asyncpg.

    Attributes:
        _name (str): The name of the health check.
        _host (str): The hostname of the PostgreSQL server.
        _port (int): The port number of the PostgreSQL server.
        _user (str | None): The username for authentication.
        _password (str | None): The password for authentication.
        _database (str | None): The database name.
        _ssl (ssl.SSLContext | None): The SSL context for secure connections.
        _direct_tls (bool): Whether to use direct TLS.
        _timeout (float): The timeout for the connection.
    """

    __slots__ = (
        "_database",
        "_direct_tls",
        "_host",
        "_name",
        "_password",
        "_port",
        "_ssl",
        "_timeout",
        "_user",
    )

    _host: str
    _port: int
    _user: str | None
    _password: str | None
    _database: str | None
    _ssl: ssl.SSLContext | None
    _direct_tls: bool
    _timeout: float
    _name: str

    def __init__(  # noqa: PLR0913
        self,
        *,
        host: str,
        port: int,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
        ssl: ssl.SSLContext | None = None,
        direct_tls: bool = False,
        timeout: float = DEFAULT_HC_TIMEOUT,
        name: str = "PostgreSQL",
    ) -> None:
        """Initializes the PostgreSQLAsyncPGHealthCheck instance.

        Args:
            host (str): The hostname of the PostgreSQL server.
            port (int): The port number of the PostgreSQL server.
            user (str | None): The username for authentication.
            password (str | None): The password for authentication.
            database (str | None): The database name.
            timeout (float): The timeout for the connection.
            ssl (ssl.SSLContext | None): The SSL context for secure connections.
            direct_tls (bool): Whether to use direct TLS.
            name (str): The name of the health check.
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._ssl = ssl
        self._direct_tls = direct_tls
        self._timeout = timeout
        self._name = name

    @classmethod
    def from_dsn(
        cls,
        dsn: "PostgresDsn | str",
        *,
        name: str = "PostgreSQL",
        timeout: float = DEFAULT_HC_TIMEOUT,
    ) -> "PostgreSQLAsyncPGHealthCheck":
        """Creates a PostgreSQLAsyncPGHealthCheck instance from a DSN.

        Args:
            dsn (PostgresDsn | str): The DSN for the PostgreSQL database.
            name (str): The name of the health check.
            timeout (float): The timeout for the connection.

        Returns:
            PostgreSQLAsyncPGHealthCheck: The health check instance.
        """
        dsn = cls.validate_dsn(dsn, type_=PostgresDsn)
        parsed_dsn = cls.parse_dsn(dsn)
        parse_result = parsed_dsn["parse_result"]
        sslctx = parsed_dsn["sslctx"]
        return cls(
            host=parse_result.hostname or "localhost",
            port=parse_result.port or 5432,
            user=parse_result.username,
            password=parse_result.password,
            database=parse_result.path.lstrip("/"),
            ssl=sslctx,
            timeout=timeout,
            name=name,
        )

    async def __call__(self) -> HealthCheckResult:
        """Performs the health check.

        Returns:
            HealthCheckResult: The result of the health check.
        """
        connection: Connection | None = None
        try:
            connection = await asyncpg.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                database=self._database,
                timeout=self._timeout,
                ssl=self._ssl,
                direct_tls=self._direct_tls,
            )
            async with connection.transaction(readonly=True):
                healthy: bool = bool(await connection.fetchval("SELECT 1"))
                return HealthCheckResult(name=self._name, healthy=healthy)
        except BaseException:  # noqa: BLE001
            return HealthCheckResult(name=self._name, healthy=False, error_details=format_exc())
        finally:
            if connection is not None and not connection.is_closed():
                await connection.close(timeout=self._timeout)
