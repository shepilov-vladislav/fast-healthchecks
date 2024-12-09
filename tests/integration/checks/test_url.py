import pytest

from fast_healthchecks.checks.url import UrlHealthCheck
from fast_healthchecks.models import HealthCheckResult

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_url_health_check_success() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/status/200",
    )
    result = await check()
    assert result == HealthCheckResult(name="test_check", healthy=True)


@pytest.mark.asyncio
async def test_url_health_check_failure() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/status/500",
    )
    result = await check()
    assert result.healthy is False
    assert "500 INTERNAL SERVER ERROR" in result.error_details


@pytest.mark.asyncio
async def test_url_health_check_with_basic_auth_success() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/basic-auth/user/passwd",
        username="user",
        password="passwd",
    )
    result = await check()
    assert result == HealthCheckResult(name="test_check", healthy=True)


@pytest.mark.asyncio
async def test_url_health_check_with_basic_auth_failure() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/basic-auth/user/passwd",
        username="user",
        password="wrong_passwd",
    )
    result = await check()
    assert result.healthy is False
    assert "401 UNAUTHORIZED" in result.error_details


@pytest.mark.asyncio
async def test_url_health_check_with_timeout() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/delay/5",
        timeout=1,
    )
    result = await check()
    assert result.healthy is False
    assert "Timeout" in result.error_details
