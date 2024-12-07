import sys
from typing import Any

import pytest

from fast_healthchecks.checks.rabbitmq import IMPORT_ERROR_MSG, RabbitMQHealthCheck
from tests.utils import patch_import_not_installed


def to_dict(obj: RabbitMQHealthCheck) -> dict[str, Any]:
    return {
        "host": obj._host,
        "user": obj._user,
        "password": obj._password,
        "port": obj._port,
        "vhost": obj._vhost,
        "secure": obj._secure,
    }


def test_import() -> None:
    sys.modules.pop("aio_pika", None)
    sys.modules.pop("fast_healthchecks.checks.rabbitmq", None)

    with patch_import_not_installed("aio_pika"), pytest.raises(ImportError, match=IMPORT_ERROR_MSG):
        from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck  # noqa: PLC0415, F401


@pytest.mark.parametrize(
    ("dsn", "expected", "exception"),
    [
        (
            "amqp://user:password@localhost/",
            {
                "host": "localhost",
                "user": "user",
                "password": "password",
                "port": 5672,
                "vhost": "/",
                "secure": False,
            },
            None,
        ),
        (
            "amqp://user:password@localhost/test",
            {
                "host": "localhost",
                "user": "user",
                "password": "password",
                "port": 5672,
                "vhost": "test",
                "secure": False,
            },
            None,
        ),
        (
            "amqp://user:password@localhost:5673/test",
            {
                "host": "localhost",
                "user": "user",
                "password": "password",
                "port": 5673,
                "vhost": "test",
                "secure": False,
            },
            None,
        ),
        (
            "amqps://user:password@localhost:5673/test",
            {
                "host": "localhost",
                "user": "user",
                "password": "password",
                "port": 5673,
                "vhost": "test",
                "secure": True,
            },
            None,
        ),
    ],
)
def test_from_dsn(dsn: str, expected: dict[str, Any] | str, exception: type[BaseException] | None) -> None:
    if exception is not None:
        with pytest.raises(exception, match=expected):
            RabbitMQHealthCheck.from_dsn(dsn)
    else:
        obj = RabbitMQHealthCheck.from_dsn(dsn)
        assert to_dict(obj) == expected
