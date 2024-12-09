from typing import Any, TypedDict

import pytest

from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck
from fast_healthchecks.models import HealthCheckResult

pytestmark = pytest.mark.integration


class RabbitMqConfig(TypedDict, total=True):
    host: str
    port: int
    user: str | None
    password: str | None
    vhost: str | None


@pytest.fixture(scope="session", name="rabbitmq_config")
def fixture_rabbitmq_config(env_config: dict[str, Any]) -> RabbitMqConfig:
    result: RabbitMqConfig = {
        "host": "localhost",
        "port": 5672,
        "user": None,
        "password": None,
        "vhost": "/",
    }
    for key in ("host", "port", "user", "password", "vhost"):
        value = env_config.get(f"RABBITMQ_{key.upper()}")
        match key:
            case "port":
                if value is not None:
                    result[key] = int(value)
            case _:
                if value is not None:
                    result[key] = str(value)

    return result


@pytest.mark.asyncio
async def test_rabbitmq_check_success(rabbitmq_config: RabbitMqConfig) -> None:
    check = RabbitMQHealthCheck(**rabbitmq_config)
    result = await check()
    assert result == HealthCheckResult(name="RabbitMQ", healthy=True, error_details=None)


@pytest.mark.asyncio
async def test_rabbitmq_check_failure(rabbitmq_config: RabbitMqConfig) -> None:
    config = {
        **rabbitmq_config,
        "host": "localhost2",
    }
    check = RabbitMQHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "nodename nor servname provided, or not known" in result.error_details


@pytest.mark.asyncio
async def test_rabbitmq_check_connection_error(rabbitmq_config: RabbitMqConfig) -> None:
    config = {
        **rabbitmq_config,
        "port": 5673,
    }
    check = RabbitMQHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "Connect call failed" in result.error_details
