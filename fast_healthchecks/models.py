"""Models for healthchecks."""

from dataclasses import dataclass

__all__ = (
    "HealthCheckResult",
    "HealthcheckReport",
)


@dataclass
class HealthCheckResult:
    """Result of a healthcheck.

    Attributes:
        name: Name of the healthcheck.
        healthy: Whether the healthcheck passed.
        error_details: Details of the error if the healthcheck failed.
    """

    name: str
    healthy: bool
    error_details: str | None = None

    def __str__(self) -> str:
        """Return a string representation of the result."""
        return f"{self.name}: {'healthy' if self.healthy else 'unhealthy'}"


@dataclass
class HealthcheckReport:
    """Report of healthchecks.

    Attributes:
        healthy: Whether all healthchecks passed.
        results: List of healthcheck results.
    """

    results: list[HealthCheckResult]
    allow_partial_failure: bool = False

    def __str__(self) -> str:
        """Return a string representation of the report."""
        return "\n".join(str(result) for result in self.results)

    @property
    def healthy(self) -> bool:
        """Return whether all healthchecks passed."""
        return all(result.healthy for result in self.results) or self.allow_partial_failure
