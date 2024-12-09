from typing import Any, TypedDict

import pytest

from fast_healthchecks.checks.redis import RedisHealthCheck
from fast_healthchecks.models import HealthCheckResult

pytestmark = pytest.mark.integration


class RedisConfig(TypedDict, total=True):
    host: str
    port: int
    user: str | None
    password: str | None
    database: str | int


@pytest.fixture(scope="session", name="redis_config")
def fixture_redis_config(env_config: dict[str, Any]) -> RedisConfig:
    result: RedisConfig = {
        "host": "localhost",
        "port": 6379,
        "user": None,
        "password": None,
        "database": 0,
    }
    for key in ("host", "port", "user", "password", "database"):
        value = env_config.get(f"REDIS_{key.upper()}")
        match key:
            case "port":
                if value is not None:
                    result[key] = int(value)
            case _:
                if value is not None:
                    result[key] = str(value)

    return result


@pytest.mark.asyncio
async def test_redis_check_success(redis_config: RedisConfig) -> None:
    check = RedisHealthCheck(**redis_config)
    result = await check()
    assert result == HealthCheckResult(name="Redis", healthy=True, error_details=None)


@pytest.mark.asyncio
async def test_redis_check_failure(redis_config: RedisConfig) -> None:
    config = {
        **redis_config,
        "host": "localhost2",
    }
    check = RedisHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "nodename nor servname provided, or not known" in result.error_details


@pytest.mark.asyncio
async def test_redis_check_connection_error(redis_config: RedisConfig) -> None:
    config = {
        **redis_config,
        "port": 6380,
    }
    check = RedisHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "Connect call failed" in result.error_details
