from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from fast_healthchecks.checks.mongo import MongoHealthCheck

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("params", "expected", "exception"),
    [
        (
            {},
            {
                "hosts": "localhost",
                "port": 27017,
                "user": None,
                "password": None,
                "database": None,
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
            },
            {
                "hosts": "localhost2",
                "port": 27017,
                "user": None,
                "password": None,
                "database": None,
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
                "port": 27018,
            },
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": None,
                "password": None,
                "database": None,
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
            },
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": None,
                "database": None,
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
            },
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": None,
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
            },
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
            },
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
                "timeout": 10.0,
            },
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
                "timeout": 10.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
                "timeout": 10.0,
                "name": "test",
            },
            {
                "hosts": "localhost2",
                "port": 27018,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
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
            MongoHealthCheck(**params)
    else:
        obj = MongoHealthCheck(**params)
        assert obj.to_dict() == expected


@pytest.mark.parametrize(
    ("args", "kwargs", "expected", "exception"),
    [
        (
            (),
            {},
            "missing 1 required positional argument: 'dsn'",
            TypeError,
        ),
        (
            ("mongodb://localhost:27017/",),
            {},
            {
                "hosts": "localhost",
                "port": 27017,
                "user": None,
                "password": None,
                "database": None,
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            ("mongodb://localhost:27017/test",),
            {},
            {
                "hosts": "localhost",
                "port": 27017,
                "user": None,
                "password": None,
                "database": "test",
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            ("mongodb://user:pass@localhost:27017/test",),
            {},
            {
                "hosts": "localhost",
                "port": 27017,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            ("mongodb://user:pass@localhost:27017/test?authSource=admin2",),
            {},
            {
                "hosts": "localhost",
                "port": 27017,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
                "timeout": 5.0,
                "name": "MongoDB",
            },
            None,
        ),
        (
            ("mongodb://user:pass@localhost:27017/test?authSource=admin2",),
            {
                "timeout": 10.0,
                "name": "Test",
            },
            {
                "hosts": "localhost",
                "port": 27017,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
                "timeout": 10.0,
                "name": "Test",
            },
            None,
        ),
        (
            ("mongodb://user:pass@localhost:27017,localhost2:27018/test?authSource=admin2",),
            {
                "timeout": 10.0,
                "name": "Test",
            },
            {
                "hosts": ["localhost:27017", "localhost2:27018"],
                "port": None,
                "user": "user",
                "password": "pass",
                "database": "test",
                "auth_source": "admin2",
                "timeout": 10.0,
                "name": "Test",
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
    if exception is not None:
        with pytest.raises(exception, match=expected):
            MongoHealthCheck.from_dsn(*args, **kwargs)
    else:
        obj = MongoHealthCheck.from_dsn(*args, **kwargs)
        assert obj.to_dict() == expected


@pytest.mark.asyncio
async def test_AsyncIOMotorClient_args_kwargs() -> None:  # noqa: N802
    health_check = MongoHealthCheck(
        hosts="localhost2",
        port=27018,
        user="user",
        password="password",
        database="test",
        auth_source="admin2",
        timeout=1.5,
        name="MongoDB",
    )
    with patch("fast_healthchecks.checks.mongo.AsyncIOMotorClient", spec=AsyncIOMotorClient) as mock:
        await health_check()
        mock.assert_called_once_with(
            host="localhost2",
            port=27018,
            username="user",
            password="password",
            authSource="admin2",
            serverSelectionTimeoutMS=1500,
        )

    health_check2 = MongoHealthCheck(
        hosts="localhost:27017,localhost2:27018",
        port=None,
        user="user",
        password="password",
        database="test",
        auth_source="admin2",
        timeout=1.5,
        name="MongoDB",
    )
    with patch("fast_healthchecks.checks.mongo.AsyncIOMotorClient", spec=AsyncIOMotorClient) as mock:
        await health_check2()
        mock.assert_called_once_with(
            host="localhost:27017,localhost2:27018",
            port=None,
            username="user",
            password="password",
            authSource="admin2",
            serverSelectionTimeoutMS=1500,
        )


@pytest.mark.asyncio
async def test__call_success() -> None:
    health_check = MongoHealthCheck(
        hosts="localhost",
        port=27017,
        user="user",
        password="password",
        database="test",
        auth_source="admin",
        timeout=1.5,
        name="MongoDB",
    )
    mock_client = AsyncMock(spec=AsyncIOMotorClient)
    mock_client["test"].command = AsyncMock()
    mock_client["test"].command.side_effect = [{"ok": 1}]
    with patch("fast_healthchecks.checks.mongo.AsyncIOMotorClient", return_value=mock_client):
        result = await health_check()
        assert result.healthy is True
        assert result.name == "MongoDB"
        assert result.error_details is None
        mock_client["test"].command.assert_called_once_with("ping")
        mock_client["test"].command.assert_awaited_once_with("ping")
        mock_client.close.assert_called_once_with()


@pytest.mark.asyncio
async def test__call_failure() -> None:
    health_check = MongoHealthCheck(
        hosts="localhost",
        port=27017,
        user="user",
        password="password",
        database="test",
        auth_source="admin",
        timeout=1.5,
        name="MongoDB",
    )
    mock_client = AsyncMock(spec=AsyncIOMotorClient)
    mock_client["test"].command = AsyncMock()
    mock_client["test"].command.side_effect = BaseException
    with patch("fast_healthchecks.checks.mongo.AsyncIOMotorClient", return_value=mock_client):
        result = await health_check()
        assert result.healthy is False
        assert result.name == "MongoDB"
        assert result.error_details is not None
        mock_client["test"].command.assert_called_once_with("ping")
        mock_client["test"].command.assert_awaited_once_with("ping")
        mock_client.close.assert_called_once_with()
