from typing import Any, TypedDict

import pytest

from fast_healthchecks.checks.mongo import MongoHealthCheck
from fast_healthchecks.models import HealthCheckResult

pytestmark = pytest.mark.integration


class MongoConfig(TypedDict, total=True):
    host: str
    port: int
    user: str | None
    password: str | None
    database: str | None
    auth_source: str | None


@pytest.fixture(scope="session", name="mongo_config")
def fixture_mongo_config(env_config: dict[str, Any]) -> MongoConfig:
    result: MongoConfig = {
        "host": "localhost",
        "port": 27017,
        "user": None,
        "password": None,
        "database": None,
        "auth_source": "admin",
    }
    for key in ("host", "port", "user", "password", "database", "auth_source"):
        value = env_config.get(f"MONGO_{key.upper()}")
        match key:
            case "port":
                if value is not None:
                    result[key] = int(value)
            case _:
                if value is not None:
                    result[key] = str(value)

    return result


@pytest.mark.asyncio
async def test_mongo_check_success(mongo_config: MongoConfig) -> None:
    check = MongoHealthCheck(**mongo_config)
    result = await check()
    assert result == HealthCheckResult(name="MongoDB", healthy=True, error_details=None)


@pytest.mark.asyncio
async def test_mongo_check_failure(mongo_config: MongoConfig) -> None:
    config = {
        **mongo_config,
        "host": "localhost2",
    }
    check = MongoHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "nodename nor servname provided, or not known" in result.error_details


@pytest.mark.asyncio
async def test_mongo_check_connection_error(mongo_config: MongoConfig) -> None:
    config = {
        **mongo_config,
        "port": 27018,
    }
    check = MongoHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "Connection refused" in result.error_details
