"""This module contains the base classes for all health checks."""

from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeAlias, TypeVar

from fast_healthchecks.compat import PYDANTIC_INSTALLED, PYDANTIC_V2
from fast_healthchecks.models import HealthCheckResult

if TYPE_CHECKING:
    from pydantic import AmqpDsn, KafkaDsn, MongoDsn, PostgresDsn, RedisDsn
else:
    AmqpDsn: TypeAlias = str
    KafkaDsn: TypeAlias = str
    MongoDsn: TypeAlias = str
    PostgresDsn: TypeAlias = str
    RedisDsn: TypeAlias = str

if PYDANTIC_INSTALLED:
    if PYDANTIC_V2:
        from pydantic import TypeAdapter
    else:  # pragma: no cover
        from pydantic import parse_obj_as

SupportedDsns: TypeAlias = AmqpDsn | KafkaDsn | MongoDsn | PostgresDsn | RedisDsn

T_co = TypeVar("T_co", bound=HealthCheckResult, covariant=True)

__all__ = (
    "DEFAULT_HC_TIMEOUT",
    "HealthCheck",
    "HealthCheckDSN",
)


DEFAULT_HC_TIMEOUT: float = 5.0


class HealthCheck(Protocol[T_co]):
    """Base class for health checks."""

    async def __call__(self) -> T_co: ...


class HealthCheckDSN(HealthCheck[T_co], Generic[T_co]):
    """Base class for health checks that can be created from a DSN."""

    @classmethod
    def from_dsn(
        cls,
        dsn: Any,  # noqa: ANN401
        *,
        name: str = "Service",
        timeout: float = DEFAULT_HC_TIMEOUT,
    ) -> "HealthCheckDSN[T_co]":
        raise NotImplementedError

    @classmethod
    def check_pydantinc_installed(cls) -> None:
        """Check if Pydantic is installed."""
        if not PYDANTIC_INSTALLED:
            msg = "Pydantic is not installed"
            raise RuntimeError(msg) from None

    @classmethod
    def validate_dsn(cls, dsn: str | SupportedDsns, type_: type[SupportedDsns]) -> str:
        """Validate the DSN."""
        if not PYDANTIC_INSTALLED:
            type_(dsn)  # type: ignore[arg-type]
            return str(dsn)

        if PYDANTIC_V2:
            return str(TypeAdapter(type_).validate_python(dsn))
        return str(parse_obj_as(type_, dsn))  # pragma: no cover
