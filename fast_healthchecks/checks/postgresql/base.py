"""This module contains the base class for PostgreSQL health checks."""

import ssl
from functools import lru_cache
from typing import Generic, Literal, TypeAlias, TypedDict, cast
from urllib.parse import ParseResult, unquote, urlparse

from fast_healthchecks.checks._base import HealthCheckDSN, T_co

SslMode: TypeAlias = Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]


class ParseDSNResult(TypedDict, total=True):
    """A dictionary containing the results of parsing a DSN."""

    parse_result: ParseResult
    sslmode: SslMode
    sslcert: str | None
    sslkey: str | None
    sslrootcert: str | None
    sslctx: ssl.SSLContext | None


@lru_cache
def create_ssl_context(
    sslmode: SslMode,
    sslcert: str | None,
    sslkey: str | None,
    sslrootcert: str | None,
) -> ssl.SSLContext | None:
    """Create an SSL context from the query parameters.

    Args:
        sslmode (SslMode): The SSL mode to use.
        sslcert (str | None): The path to the SSL certificate.
        sslkey (str | None): The path to the SSL key.
        sslrootcert (str | None): The path to the SSL root certificate.

    Returns:
        ssl.SSLContext | None: The SSL context.
    """
    sslctx: ssl.SSLContext | None = None
    match sslmode:
        case "disable":
            sslctx = None
        case "allow":
            sslctx = None
        case "prefer":
            sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        case "require":
            sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            sslctx.check_hostname = False
            sslctx.verify_mode = ssl.CERT_NONE
        case "verify-ca":
            sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=sslrootcert)
            sslctx.check_hostname = False
            sslctx.verify_mode = ssl.CERT_REQUIRED
        case "verify-full":
            if sslcert is None:
                msg = "sslcert is required for verify-full"
                raise ValueError(msg) from None
            sslctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=sslrootcert)
            sslctx.check_hostname = True
            sslctx.load_cert_chain(
                certfile=sslcert,
                keyfile=sslkey,
            )
        case _:  # pragma: no cover
            msg = f"Unsupported sslmode: {sslmode}"
            raise ValueError(msg) from None
    return sslctx


class BasePostgreSQLHealthCheck(HealthCheckDSN[T_co], Generic[T_co]):
    """Base class for PostgreSQL health checks."""

    @classmethod
    def create_ssl_context_from_query(
        cls,
        sslmode: SslMode,
        sslcert: str | None,
        sslkey: str | None,
        sslrootcert: str | None,
    ) -> ssl.SSLContext | None:
        """Create an SSL context from the query parameters.

        Args:
            sslmode (SslMode): The SSL mode to use.
            sslcert (str | None): The path to the SSL certificate.
            sslkey (str | None): The path to the SSL key.
            sslrootcert (str | None): The path to the SSL root certificate.

        Returns:
            ssl.SSLContext | None: The SSL context.
        """
        return create_ssl_context(sslmode, sslcert, sslkey, sslrootcert)

    @classmethod
    def validate_sslmode(cls, mode: str) -> SslMode:
        """Validate the SSL mode.

        Args:
            mode (str): The SSL mode to validate.

        Returns:
            SslMode: The validated SSL mode.

        Raises:
            ValueError: If the SSL mode is invalid.
        """
        if mode not in {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}:
            msg = f"Invalid sslmode: {mode}"
            raise ValueError(msg) from None
        return cast("SslMode", mode)

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
        sslmode: SslMode = cls.validate_sslmode(query.get("sslmode", "disable"))
        sslcert: str | None = query.get("sslcert")
        sslkey: str | None = query.get("sslkey")
        sslrootcert: str | None = query.get("sslrootcert")
        sslctx: ssl.SSLContext | None = cls.create_ssl_context_from_query(sslmode, sslcert, sslkey, sslrootcert)
        return {
            "parse_result": parse_result,
            "sslmode": sslmode,
            "sslcert": sslcert,
            "sslkey": sslkey,
            "sslrootcert": sslrootcert,
            "sslctx": sslctx,
        }
