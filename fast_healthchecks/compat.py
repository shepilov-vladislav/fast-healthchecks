"""Module to check compatibility with Pydantic."""

PYDANTIC_INSTALLED: bool
PYDANTIC_VERSION: str | None
PYDANTIC_V2: bool

try:
    from pydantic.version import VERSION as PYDANTIC_VERSION

    PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")  # type: ignore[union-attr]
    PYDANTIC_INSTALLED = True
except ImportError:
    PYDANTIC_INSTALLED = False
    PYDANTIC_VERSION = None
    PYDANTIC_V2 = False

__all__ = (
    "PYDANTIC_INSTALLED",
    "PYDANTIC_V2",
    "PYDANTIC_VERSION",
)
