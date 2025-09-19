import pytest

from fast_healthchecks.checks.postgresql.psycopg import PostgreSQLPsycopgHealthCheck
from fast_healthchecks.models import HealthCheckResult
from tests.integration.checks.postgresql.conftest import BasePostgreSQLConfig

pytestmark = pytest.mark.integration


class PsycopgConfig(BasePostgreSQLConfig, total=True):
    sslmode: str | None
    sslrootcert: str | None


@pytest.fixture(scope="session", name="psycopg_config")
def fixture_psycopg_config(base_postgresql_config: BasePostgreSQLConfig) -> PsycopgConfig:
    return {
        **base_postgresql_config,
        "sslmode": None,
        "sslrootcert": None,
    }


@pytest.mark.asyncio
async def test_postgresql_psycopg_check_success(psycopg_config: PsycopgConfig) -> None:
    check = PostgreSQLPsycopgHealthCheck(**psycopg_config)  # ty: ignore[missing-argument]
    result = await check()
    assert result == HealthCheckResult(name="PostgreSQL", healthy=True, error_details=None)


@pytest.mark.asyncio
async def test_postgresql_psycopg_check_failure(psycopg_config: PsycopgConfig) -> None:
    config = {
        **psycopg_config,
        "host": "localhost2",
    }
    check = PostgreSQLPsycopgHealthCheck(**config)  # ty: ignore[missing-argument]
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "nodename nor servname provided, or not known" in result.error_details


@pytest.mark.asyncio
async def test_postgresql_psycopg_check_connection_error(psycopg_config: PsycopgConfig) -> None:
    config = {
        **psycopg_config,
        "port": 6432,
    }
    check = PostgreSQLPsycopgHealthCheck(**config)  # ty: ignore[missing-argument]
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "connection failed" in result.error_details
