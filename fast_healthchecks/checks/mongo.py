"""This module provides a health check class for MongoDB.

Classes:
    MongoHealthCheck: A class to perform health checks on MongoDB.

Usage:
    The MongoHealthCheck class can be used to perform health checks on MongoDB by calling it.

Example:
    health_check = MongoHealthCheck(
        host="localhost",
        port=27017
    )
    result = await health_check()
    print(result.healthy)
"""

import logging
from traceback import format_exc
from typing import TYPE_CHECKING, Any, TypeAlias, TypedDict
from urllib.parse import ParseResult, unquote, urlparse

from fast_healthchecks.checks._base import DEFAULT_HC_TIMEOUT, HealthCheckDSN
from fast_healthchecks.compat import PYDANTIC_INSTALLED
from fast_healthchecks.models import HealthCheckResult

IMPORT_ERROR_MSG = "motor is not installed. Install it with `pip install motor`."

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as exc:
    raise ImportError(IMPORT_ERROR_MSG) from exc

if TYPE_CHECKING:
    from collections.abc import Mapping


if PYDANTIC_INSTALLED:
    from pydantic import MongoDsn
else:  # pragma: no cover
    MongoDsn: TypeAlias = str  # type: ignore[no-redef]

logger = logging.getLogger(__name__)


class ParseDSNResult(TypedDict, total=True):
    """A dictionary containing the results of parsing a DSN."""

    parse_result: ParseResult
    authSource: str


class MongoHealthCheck(HealthCheckDSN[HealthCheckResult]):
    """A class to perform health checks on MongoDB.

    Attributes:
        _auth_source: The MongoDB authentication source.
        _database: The MongoDB database to use.
        _host: The MongoDB host.
        _name: The name of the health check.
        _password: The MongoDB password.
        _port: The MongoDB port.
        _timeout: The timeout for the health check.
        _user: The MongoDB user.
    """

    __slots__ = (
        "_auth_source",
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
    _user: str | None
    _password: str | None
    _database: str | None
    _auth_source: str
    _timeout: float
    _name: str

    def __init__(  # noqa: PLR0913
        self,
        *,
        host: str = "localhost",
        port: int = 27017,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
        auth_source: str = "admin",
        timeout: float = DEFAULT_HC_TIMEOUT,
        name: str = "MongoDB",
    ) -> None:
        """Initializes the MongoHealthCheck class.

        Args:
            host: The MongoDB host.
            port: The MongoDB port
            user: The MongoDB user.
            password: The MongoDB password.
            database: The MongoDB database to use.
            auth_source: The MongoDB authentication source.
            timeout: The timeout for the health check.
            name: The name of the health check.
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._auth_source = auth_source
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
        parse_result: ParseResult = urlparse(dsn)
        query = (
            {k: unquote(v) for k, v in (q.split("=") for q in parse_result.query.split("&"))}
            if parse_result.query
            else {}
        )
        return {"parse_result": parse_result, "authSource": query.get("authSource", "admin")}

    @classmethod
    def from_dsn(
        cls,
        dsn: "MongoDsn | str",
        *,
        name: str = "MongoDB",
        timeout: float = DEFAULT_HC_TIMEOUT,
    ) -> "MongoHealthCheck":
        """Creates a MongoHealthCheck instance from a DSN.

        Args:
            dsn (MongoDsn | str): The DSN for the PostgreSQL database.
            name (str): The name of the health check.
            timeout (float): The timeout for the connection.

        Returns:
            MongoHealthCheck: The health check instance.
        """
        dsn = cls.validate_dsn(dsn, type_=MongoDsn)
        parsed_dsn = cls.parse_dsn(dsn)
        parse_result = parsed_dsn["parse_result"]
        return cls(
            host=parse_result.hostname or "localhost",
            port=parse_result.port or 27017,
            user=parse_result.username,
            password=parse_result.password,
            database=parse_result.path.lstrip("/") or None,
            auth_source=parsed_dsn["authSource"],
            timeout=timeout,
            name=name,
        )

    async def __call__(self) -> HealthCheckResult:
        """Performs the health check on MongoDB.

        Returns:
            A HealthCheckResult object.
        """
        client: AsyncIOMotorClient[Mapping[str, Any]] = AsyncIOMotorClient(
            host=self._host,
            port=self._port,
            username=self._user,
            password=self._password,
            authSource=self._auth_source,
            serverSelectionTimeoutMS=int(self._timeout * 1000),
        )
        database = client[self._database] if self._database else client[self._auth_source]
        try:
            res = await database.command("ping")
            return HealthCheckResult(name=self._name, healthy=res == {"ok": 1.0})
        except BaseException:  # noqa: BLE001
            return HealthCheckResult(name=self._name, healthy=False, error_details=format_exc())
        finally:
            client.close()
