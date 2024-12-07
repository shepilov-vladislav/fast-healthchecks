import sys
from typing import Any

import pytest

from fast_healthchecks.checks.redis import IMPORT_ERROR_MSG, RedisHealthCheck
from tests.utils import patch_import_not_installed


def to_dict(obj: RedisHealthCheck) -> dict[str, Any]:
    return {
        "host": obj._host,
        "port": obj._port,
        "database": obj._database,
        "user": obj._user,
        "password": obj._password,
    }


def test_import() -> None:
    sys.modules.pop("redis.asyncio", None)
    sys.modules.pop("fast_healthchecks.checks.redis", None)

    with patch_import_not_installed("redis.asyncio"), pytest.raises(ImportError, match=IMPORT_ERROR_MSG):
        from fast_healthchecks.checks.redis import RedisHealthCheck  # noqa: PLC0415, F401


@pytest.mark.parametrize(
    ("dsn", "expected", "exception"),
    [
        (
            "redis://localhost:6379/",
            {
                "host": "localhost",
                "port": 6379,
                "database": 0,
                "user": None,
                "password": None,
            },
            None,
        ),
        (
            "redis://localhost:6379/1",
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": None,
                "password": None,
            },
            None,
        ),
        (
            "redis://user@localhost:6379/1",
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": "user",
                "password": None,
            },
            None,
        ),
        (
            "redis://user:pass@localhost:6379/1",
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": "user",
                "password": "pass",
            },
            None,
        ),
    ],
)
def test_from_dsn(dsn: str, expected: dict[str, Any] | str, exception: type[BaseException] | None) -> None:
    if exception is not None:
        with pytest.raises(exception, match=expected):
            RedisHealthCheck.from_dsn(dsn)
    else:
        obj = RedisHealthCheck.from_dsn(dsn)
        assert to_dict(obj) == expected
