import sys

import pytest
from pytest_httpx import HTTPXMock

from fast_healthchecks.checks.url import IMPORT_ERROR_MSG, UrlHealthCheck
from fast_healthchecks.models import HealthCheckResult
from tests.utils import patch_import_not_installed


def test_import() -> None:
    sys.modules.pop("httpx", None)
    sys.modules.pop("fast_healthchecks.checks.url", None)

    with patch_import_not_installed("httpx"), pytest.raises(ImportError, match=IMPORT_ERROR_MSG):
        from fast_healthchecks.checks.url import UrlHealthCheck  # noqa: PLC0415, F401


@pytest.mark.asyncio
async def test_url_health_check_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://test.com", status_code=200)
    check = UrlHealthCheck(
        name="test_check",
        url="https://test.com",
    )
    result = await check()
    assert result == HealthCheckResult(name="test_check", healthy=True)


@pytest.mark.asyncio
async def test_url_health_check_failure(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://test.com", status_code=500)
    check = UrlHealthCheck(
        name="test_check",
        url="https://test.com",
    )
    result = await check()
    assert result.healthy is False
    assert "500 Internal Server Error" in result.error_details
