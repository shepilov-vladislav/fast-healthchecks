"""The module contains a health check for PostgreSQL using psycopg.

Classes:
    PostgreSQLPsycopgHealthCheck: A class for health checking PostgreSQL using psycopg.

Usage:
    The PostgreSQLPsycopgHealthCheck class can be used to perform health checks on a PostgreSQL database by
    connecting to the database and executing a simple query.

Example:
    health_check = PostgreSQLPsycopgHealthCheck(
        host="localhost",
        port=5432,
        user="username",
        password="password",
        database="dbname"
    )
    # or
    health_check = PostgreSQLPsycopgHealthCheck.from_dsn(
        "postgresql://username:password@localhost:5432/dbname",
    )
    result = await health_check()
    print(result.healthy)
"""

from traceback import format_exc
from typing import TYPE_CHECKING, TypeAlias

from fast_healthchecks.checks._base import DEFAULT_HC_TIMEOUT
from fast_healthchecks.checks.postgresql.base import BasePostgreSQLHealthCheck, SslMode
from fast_healthchecks.compat import PYDANTIC_INSTALLED
from fast_healthchecks.models import HealthCheckResult

IMPORT_ERROR_MSG = "psycopg is not installed. Install it with `pip install psycopg`."

try:
    import psycopg
except ImportError as exc:
    raise ImportError(IMPORT_ERROR_MSG) from exc

if TYPE_CHECKING:
    from psycopg import AsyncConnection


if PYDANTIC_INSTALLED:
    from pydantic import PostgresDsn
else:  # pragma: no cover
    PostgresDsn: TypeAlias = str  # type: ignore[no-redef]


class PostgreSQLPsycopgHealthCheck(BasePostgreSQLHealthCheck[HealthCheckResult]):
    """Health check class for PostgreSQL using psycopg.

    Attributes:
        _name (str): The name of the health check.
        _host (str): The hostname of the PostgreSQL server.
        _port (int): The port number of the PostgreSQL server.
        _user (str | None): The username for authentication.
        _password (str | None): The password for authentication.
        _database (str | None): The database name.
        _sslmode (SslMode | None): The SSL mode to use for the connection.
        _sslcert (str | None): The path to the SSL certificate file.
        _sslkey (str | None): The path to the SSL key file.
        _sslrootcert (str | None): The path to the SSL root certificate file.
        _timeout (float): The timeout for the health check.
    """

    __slots__ = (
        "_database",
        "_host",
        "_name",
        "_password",
        "_port",
        "_sslcert",
        "_sslkey",
        "_sslmode",
        "_sslrootcert",
        "_timeout",
        "_user",
    )

    _host: str
    _port: int
    _user: str | None
    _password: str | None
    _database: str | None
    _sslmode: SslMode | None
    _sslcert: str | None
    _sslkey: str | None
    _sslrootcert: str | None
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
        sslmode: SslMode | None = None,
        sslcert: str | None = None,
        sslkey: str | None = None,
        sslrootcert: str | None = None,
        timeout: float = DEFAULT_HC_TIMEOUT,
        name: str = "PostgreSQL",
    ) -> None:
        """Initializes the PostgreSQLPsycopgHealthCheck instance.

        Args:
            host (str): The hostname of the PostgreSQL server.
            port (int): The port number of the PostgreSQL server.
            user (str | None): The username for authentication.
            password (str | None): The password for authentication.
            database (str | None): The database name.
            timeout (float): The timeout for the health check.
            sslmode (SslMode | None): The SSL mode to use for the connection.
            sslcert (str | None): The path to the SSL certificate file.
            sslkey (str | None): The path to the SSL key file.
            sslrootcert (str | None): The path to the SSL root certificate file.
            name (str): The name of the health check.
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._sslmode = sslmode
        self._sslcert = sslcert
        self._sslkey = sslkey
        self._sslrootcert = sslrootcert
        self._timeout = timeout
        self._name = name

    @classmethod
    def from_dsn(
        cls,
        dsn: "PostgresDsn | str",
        *,
        name: str = "PostgreSQL",
        timeout: float = DEFAULT_HC_TIMEOUT,
    ) -> "PostgreSQLPsycopgHealthCheck":
        """Creates a PostgreSQLPsycopgHealthCheck instance from a DSN.

        Args:
            dsn (PostgresDsn | str): The DSN for the PostgreSQL connection.
            name (str): The name of the health check.
            timeout (float): The timeout for the health check.

        Returns:
            PostgreSQLPsycopgHealthCheck: The health check instance.
        """
        dsn = cls.validate_dsn(dsn, type_=PostgresDsn)
        parsed_dsn = cls.parse_dsn(dsn)
        parse_result = parsed_dsn["parse_result"]
        return cls(
            host=parse_result.hostname or "localhost",
            port=parse_result.port or 5432,
            user=parse_result.username,
            password=parse_result.password,
            database=parse_result.path.lstrip("/"),
            sslmode=parsed_dsn["sslmode"],
            sslcert=parsed_dsn["sslcert"],
            sslkey=parsed_dsn["sslkey"],
            sslrootcert=parsed_dsn["sslrootcert"],
            timeout=timeout,
            name=name,
        )

    async def __call__(self) -> HealthCheckResult:
        """Performs the health check.

        Returns:
            HealthCheckResult: The result of the health check.
        """
        connection: AsyncConnection | None = None
        try:
            connection = await psycopg.AsyncConnection.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                dbname=self._database,
                sslmode=self._sslmode,
                sslcert=self._sslcert,
                sslkey=self._sslkey,
                sslrootcert=self._sslrootcert,
            )
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                healthy: bool = bool(await cursor.fetchone())
                return HealthCheckResult(name=self._name, healthy=healthy)
        except BaseException:  # noqa: BLE001
            return HealthCheckResult(name=self._name, healthy=False, error_details=format_exc())
        finally:
            if connection is not None and not connection.closed:
                await connection.cancel_safe(timeout=self._timeout)
                await connection.close()
