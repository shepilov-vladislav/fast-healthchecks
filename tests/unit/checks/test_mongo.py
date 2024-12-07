import sys
from typing import Any

import pytest

from fast_healthchecks.checks.mongo import IMPORT_ERROR_MSG, MongoHealthCheck
from tests.utils import patch_import_not_installed


def to_dict(obj: MongoHealthCheck) -> dict[str, Any]:
    return {
        "host": obj._host,
        "port": obj._port,
        "user": obj._user,
        "password": obj._password,
        "database": obj._database,
        "auth_source": obj._auth_source,
    }


def test_import() -> None:
    sys.modules.pop("motor.motor_asyncio", None)
    sys.modules.pop("fast_healthchecks.checks.mongo", None)

    with patch_import_not_installed("motor.motor_asyncio"), pytest.raises(ImportError, match=IMPORT_ERROR_MSG):
        from fast_healthchecks.checks.mongo import MongoHealthCheck  # noqa: PLC0415, F401


@pytest.mark.parametrize(
    ("dsn", "expected", "exception"),
    [
        (
            "mongodb://localhost:27017/",
            {
                "host": "localhost",
                "port": 27017,
                "user": None,
                "password": None,
                "database": None,
                "auth_source": "admin",
            },
            None,
        ),
        (
            "mongodb://localhost:27017/test",
            {
                "host": "localhost",
                "port": 27017,
                "user": None,
                "password": None,
                "database": "test",
                "auth_source": "admin",
            },
            None,
        ),
        (
            "mongodb://user:pass@localhost:27017/test",
            {
                "host": "localhost",
                "port": 27017,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin",
            },
            None,
        ),
        (
            "mongodb://user:pass@localhost:27017/test?authSource=admin2",
            {
                "host": "localhost",
                "port": 27017,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
            },
            None,
        ),
    ],
)
def test_from_dsn(dsn: str, expected: dict[str, Any] | str, exception: type[BaseException] | None) -> None:
    if exception is not None:
        with pytest.raises(exception, match=expected):
            MongoHealthCheck.from_dsn(dsn)
    else:
        obj = MongoHealthCheck.from_dsn(dsn)
        assert to_dict(obj) == expected
