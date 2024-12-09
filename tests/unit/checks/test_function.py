import asyncio
import time

import pytest

from fast_healthchecks.checks.function import FunctionHealthCheck
from fast_healthchecks.models import HealthCheckResult

pytestmark = pytest.mark.unit


def dummy_sync_function(arg: str, kwarg: int = 1) -> None:  # noqa: ARG001
    time.sleep(0.1)


def dummy_sync_function_fail(arg: str, kwarg: int = 1) -> None:  # noqa: ARG001
    time.sleep(0.1)
    msg = "Test exception"
    raise Exception(msg) from None  # noqa: TRY002


async def dummy_async_function(arg: str, kwarg: int = 1) -> None:  # noqa: ARG001
    await asyncio.sleep(0.1)


async def dummy_async_function_fail(arg: str, kwarg: int = 1) -> None:  # noqa: ARG001
    await asyncio.sleep(0.1)
    msg = "Test exception"
    raise Exception(msg) from None  # noqa: TRY002


@pytest.mark.asyncio
async def test_sync_function_success() -> None:
    check = FunctionHealthCheck(func=dummy_sync_function, args=("arg",), kwargs={"kwarg": 2}, timeout=0.2)
    result = await check()
    assert result == HealthCheckResult(name="Function", healthy=True, error_details=None)


@pytest.mark.asyncio
async def test_sync_function_failure() -> None:
    check = FunctionHealthCheck(func=dummy_sync_function_fail, args=("arg",), kwargs={"kwarg": 2}, timeout=0.2)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "Test exception" in result.error_details


@pytest.mark.asyncio
async def test_async_function_success() -> None:
    check = FunctionHealthCheck(func=dummy_async_function, args=("arg",), kwargs={"kwarg": 2}, timeout=0.2)
    result = await check()
    assert result == HealthCheckResult(name="Function", healthy=True, error_details=None)


@pytest.mark.asyncio
async def test_async_function_failure() -> None:
    check = FunctionHealthCheck(func=dummy_async_function_fail, args=("arg",), kwargs={"kwarg": 2}, timeout=0.2)
    result = await check()
    assert result.healthy is False
    assert result.error_details is not None
    assert "Test exception" in result.error_details
