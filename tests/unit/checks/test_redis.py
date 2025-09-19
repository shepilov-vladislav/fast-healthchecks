from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.asyncio import Redis

from fast_healthchecks.checks.redis import RedisHealthCheck

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("params", "expected", "exception"),
    [
        (
            {},
            {
                "host": "localhost",
                "port": 6379,
                "database": 0,
                "user": None,
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
            },
            {
                "host": "localhost2",
                "port": 6379,
                "database": 0,
                "user": None,
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
                "port": 6380,
            },
            {
                "host": "localhost2",
                "port": 6380,
                "database": 0,
                "user": None,
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
                "port": 6380,
                "database": 1,
            },
            {
                "host": "localhost2",
                "port": 6380,
                "database": 1,
                "user": None,
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
            },
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": None,
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
            },
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
                "password": "pass",
            },
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
                "password": "pass",
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
                "password": "pass",
                "timeout": 10.0,
            },
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
                "password": "pass",
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 10.0,
                "name": "Redis",
            },
            None,
        ),
        (
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
                "password": "pass",
                "timeout": 10.0,
                "name": "test",
            },
            {
                "host": "localhost2",
                "port": 6380,
                "database": "test",
                "user": "user",
                "password": "pass",
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 10.0,
                "name": "test",
            },
            None,
        ),
    ],
)
def test_init(params: dict[str, Any], expected: dict[str, Any], exception: type[BaseException] | None) -> None:
    if exception is not None:
        with pytest.raises(exception, match=str(expected)):
            RedisHealthCheck(**params)
    else:
        obj = RedisHealthCheck(**params)
        assert obj.to_dict() == expected


@pytest.mark.parametrize(
    ("args", "kwargs", "expected", "exception"),
    [
        (
            ("redis://localhost:6379/",),
            {},
            {
                "host": "localhost",
                "port": 6379,
                "database": 0,
                "user": None,
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            ("redis://localhost:6379/1",),
            {},
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": None,
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            ("redis://user@localhost:6379/1",),
            {},
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": "user",
                "password": None,
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            ("redis://user:pass@localhost:6379/1",),
            {},
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": "user",
                "password": "pass",
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 5.0,
                "name": "Redis",
            },
            None,
        ),
        (
            ("redis://user:pass@localhost:6379/1",),
            {
                "timeout": 10.0,
            },
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": "user",
                "password": "pass",
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 10.0,
                "name": "Redis",
            },
            None,
        ),
        (
            ("redis://user:pass@localhost:6379/1",),
            {
                "timeout": 10.0,
                "name": "test",
            },
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": "user",
                "password": "pass",
                "ssl": False,
                "ssl_ca_certs": None,
                "timeout": 10.0,
                "name": "test",
            },
            None,
        ),
        (
            ("redis://user:pass@localhost:6379/1?ssl_ca_certs=/root.crt",),
            {
                "timeout": 10.0,
                "name": "test",
            },
            {
                "host": "localhost",
                "port": 6379,
                "database": 1,
                "user": "user",
                "password": "pass",
                "ssl": True,
                "ssl_ca_certs": "/root.crt",
                "timeout": 10.0,
                "name": "test",
            },
            None,
        ),
    ],
)
def test_from_dsn(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    expected: dict[str, Any] | str,
    exception: type[BaseException] | None,
) -> None:
    if exception is not None and isinstance(expected, str):
        with pytest.raises(exception, match=expected):
            RedisHealthCheck.from_dsn(*args, **kwargs)
    else:
        obj = RedisHealthCheck.from_dsn(*args, **kwargs)
        assert obj.to_dict() == expected


@pytest.mark.asyncio
async def test_call_success() -> None:
    health_check = RedisHealthCheck(
        host="localhost2",
        port=6380,
        database="test",
        user="user",
        password="pass",
        timeout=10.0,
        name="Test",
    )
    redis_mock = MagicMock(spec=Redis)
    redis_mock.__aenter__.return_value = redis_mock
    redis_mock.ping = AsyncMock(return_value=True)
    with patch("fast_healthchecks.checks.redis.Redis", return_value=redis_mock) as patched_Redis:  # noqa: N806
        result = await health_check()
        assert result.healthy is True
        assert result.name == "Test"
        patched_Redis.assert_called_once_with(
            host="localhost2",
            port=6380,
            db="test",
            username="user",
            password="pass",
            ssl=False,
            ssl_ca_certs=None,
            socket_timeout=10.0,
            single_connection_client=True,
        )


@pytest.mark.asyncio
async def test_call_exception() -> None:
    health_check = RedisHealthCheck(
        host="localhost",
        port=6379,
        database=0,
        user=None,
        password=None,
        timeout=5.0,
        name="Redis",
    )
    with patch("fast_healthchecks.checks.redis.Redis") as patched_Redis:  # noqa: N806
        patched_Redis.return_value.__aenter__.side_effect = Exception("Connection error")
        result = await health_check()
        assert result.name == "Redis"
        assert result.healthy is False
        assert "Connection error" in str(result.error_details)
        patched_Redis.assert_called_once_with(
            host="localhost",
            port=6379,
            db=0,
            username=None,
            password=None,
            ssl=False,
            ssl_ca_certs=None,
            socket_timeout=5.0,
            single_connection_client=True,
        )
