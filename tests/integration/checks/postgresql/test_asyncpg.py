import ssl

import pytest

from fast_healthchecks.checks.postgresql.asyncpg import PostgreSQLAsyncPGHealthCheck
from fast_healthchecks.models import HealthCheckResult
from tests.integration.checks.postgresql.conftest import BasePostgreSQLConfig

pytestmark = pytest.mark.integration


class AsyncPGConfig(BasePostgreSQLConfig, total=True):
    ssl: ssl.SSLContext | None
    direct_tls: bool | None


@pytest.fixture(scope="session", name="asyncpg_config")
def fixture_asyncpg_config(base_postgresql_config: BasePostgreSQLConfig) -> AsyncPGConfig:
    return {
        **base_postgresql_config,
        "ssl": None,
        "direct_tls": None,
    }


@pytest.mark.asyncio
async def test_postgresql_asyncpg_check_success(asyncpg_config: AsyncPGConfig) -> None:
    check = PostgreSQLAsyncPGHealthCheck(**asyncpg_config)
    result = await check()
    assert result == HealthCheckResult(name="PostgreSQL", healthy=True, error_details=None)


@pytest.mark.asyncio
async def test_postgresql_asyncpg_check_failure(asyncpg_config: AsyncPGConfig) -> None:
    config = {
        **asyncpg_config,
        "host": "localhost2",
    }
    check = PostgreSQLAsyncPGHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "nodename nor servname provided, or not known" in result.error_details


@pytest.mark.asyncio
async def test_postgresql_asyncpg_check_connection_error(asyncpg_config: AsyncPGConfig) -> None:
    config = {
        **asyncpg_config,
        "port": 6432,
    }
    check = PostgreSQLAsyncPGHealthCheck(**config)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "Connect call failed" in result.error_details
