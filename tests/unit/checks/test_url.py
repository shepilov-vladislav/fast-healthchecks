from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient, Response

from fast_healthchecks.checks.url import UrlHealthCheck
from fast_healthchecks.models import HealthCheckResult

pytestmark = pytest.mark.unit


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_url_health_check_success() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/status/200",
    )
    result = await check()
    assert result == HealthCheckResult(name="test_check", healthy=True)


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_url_health_check_failure() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/status/500",
    )
    result = await check()
    assert result.healthy is False
    assert "500 INTERNAL SERVER ERROR" in result.error_details


@pytest.mark.vcr
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


@pytest.mark.vcr
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


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_url_health_check_with_timeout() -> None:
    check = UrlHealthCheck(
        name="test_check",
        url="https://httpbin.org/delay/5",
        timeout=0.1,
    )
    result = await check()
    assert result.healthy is False
    assert "Timeout" in result.error_details


@pytest.mark.asyncio
async def test_AsyncClient_args_kwargs() -> None:  # noqa: N802
    health_check = UrlHealthCheck(
        name="Test",
        url="https://httpbin.org/status/200",
        username="user",
        password="passwd",
        follow_redirects=False,
        timeout=1.0,
    )
    response = Response(
        status_code=200,
        content=b"",
        request=MagicMock(),
        history=[],
    )
    AsyncClient_mock = MagicMock(spec=AsyncClient)  # noqa: N806
    AsyncClient_mock.__aenter__.return_value = AsyncClient_mock
    AsyncClient_mock.get.side_effect = [response]
    with patch("fast_healthchecks.checks.url.AsyncClient", return_value=AsyncClient_mock) as patched_AsyncClient:  # noqa: N806
        result = await health_check()
        assert result == HealthCheckResult(name="Test", healthy=True)
        patched_AsyncClient.assert_called_once_with(
            auth=health_check._auth,
            timeout=1.0,
            transport=health_check._transport,
            follow_redirects=False,
        )
        AsyncClient_mock.get.assert_called_once_with("https://httpbin.org/status/200")
