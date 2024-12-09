"""Module containing all the health checks."""

from typing import TypeAlias

from fast_healthchecks.checks._base import HealthCheck, HealthCheckDSN
from fast_healthchecks.models import HealthCheckResult

Check: TypeAlias = HealthCheck[HealthCheckResult] | HealthCheckDSN[HealthCheckResult]

__all__ = (
    "Check",
    "HealthCheck",
    "HealthCheckDSN",
)
