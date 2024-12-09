import pytest

from fast_healthchecks.models import HealthcheckReport, HealthCheckResult

pytestmark = pytest.mark.unit


def test_healthcheck_result() -> None:
    hcr1 = HealthCheckResult(
        name="test",
        healthy=True,
    )
    assert str(hcr1) == "test: healthy"
    hcr2 = HealthCheckResult(
        name="test",
        healthy=False,
        error_details="error",
    )
    assert str(hcr2) == "test: unhealthy"


def test_healthcheck_report() -> None:
    hcr = HealthcheckReport(
        results=[
            HealthCheckResult(
                name="test1",
                healthy=True,
            ),
            HealthCheckResult(
                name="test2",
                healthy=False,
                error_details="error",
            ),
        ],
    )
    assert str(hcr) == "test1: healthy\ntest2: unhealthy"
    assert hcr.healthy is False

    hcr = HealthcheckReport(
        results=[
            HealthCheckResult(
                name="test1",
                healthy=True,
            ),
            HealthCheckResult(
                name="test2",
                healthy=False,
                error_details="error",
            ),
        ],
        allow_partial_failure=True,
    )
    assert hcr.healthy is True
