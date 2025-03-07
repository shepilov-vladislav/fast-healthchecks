from unittest.mock import patch

import pytest
from pydantic import AmqpDsn, KafkaDsn, PostgresDsn, RedisDsn, ValidationError

from fast_healthchecks.checks._base import HealthCheckDSN, SupportedDsns  # noqa: PLC2701
from fast_healthchecks.compat import PYDANTIC_V2, MongoDsn
from fast_healthchecks.models import HealthCheckResult

pytestmark = pytest.mark.unit


class DummyCheck(HealthCheckDSN[HealthCheckResult]):
    async def __call__(self) -> HealthCheckResult:
        return HealthCheckResult(name="dummy", healthy=True)


def test_check_pydantinc_installed() -> None:
    assert DummyCheck.check_pydantinc_installed() is None

    with (
        patch("fast_healthchecks.checks._base.PYDANTIC_INSTALLED", new=False),
        pytest.raises(RuntimeError, match="Pydantic is not installed"),
    ):
        DummyCheck.check_pydantinc_installed()


@pytest.mark.parametrize(
    ("dsn", "dsn_type", "expected", "pydantic_installed", "exception"),
    [
        ("amqp://user:pass@host:10000/vhost", AmqpDsn, "amqp://user:pass@host:10000/vhost", True, None),
        ("kafka://user:pass@host:10000/topic", KafkaDsn, "kafka://user:pass@host:10000/topic", True, None),
        ("mongodb://user:pass@host:10000/db", MongoDsn, "mongodb://user:pass@host:10000/db", True, None),
        ("postgresql://user:pass@host:10000/db", PostgresDsn, "postgresql://user:pass@host:10000/db", True, None),
        ("redis://user:pass@host:10000/0", RedisDsn, "redis://user:pass@host:10000/0", True, None),
        ("1", int, "1", True, None),
        (
            "a",
            int,
            "validation error for int" if PYDANTIC_V2 else "value is not a valid integer",
            True,
            ValidationError,
        ),
        ("a", int, "invalid literal for int()", False, ValueError),
        (1, int, "1", True, None),
    ],
)
def test_validate_dsn(
    dsn: str,
    dsn_type: SupportedDsns,
    expected: str,
    pydantic_installed: bool,  # noqa: FBT001
    exception: type[BaseException] | None,
) -> None:
    with patch("fast_healthchecks.checks._base.PYDANTIC_INSTALLED", new=pydantic_installed):
        if exception is not None:
            with pytest.raises(exception, match=expected):
                DummyCheck.validate_dsn(dsn, dsn_type)
        else:
            assert DummyCheck.validate_dsn(dsn, dsn_type) == expected


def test_validate_dsn_without_pydantic() -> None:
    with patch("fast_healthchecks.checks._base.PYDANTIC_INSTALLED", new=False):
        AmqpDsn = str  # noqa: N806
        assert (
            DummyCheck.validate_dsn("amqp://user:pass@host:10000/vhost", AmqpDsn) == "amqp://user:pass@host:10000/vhost"
        )


def test_from_dsn_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        DummyCheck.from_dsn("amqp://user:pass@host:10000/vhost")
