"""Module to check compatibility with Pydantic."""

from typing import TypeAlias

PYDANTIC_INSTALLED: bool
PYDANTIC_VERSION: str | None
PYDANTIC_V2: bool
MongoDsn: TypeAlias  # type: ignore[valid-type]

try:
    from pydantic import MongoDsn
    from pydantic.version import VERSION as PYDANTIC_VERSION

    PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")  # type: ignore[union-attr]
    PYDANTIC_INSTALLED = True
    if PYDANTIC_V2:
        from pydantic.networks import MongoDsn
    else:
        MongoDsn = str
except ImportError:
    PYDANTIC_INSTALLED = False
    PYDANTIC_VERSION = None
    PYDANTIC_V2 = False
    MongoDsn = str


__all__ = (
    "PYDANTIC_INSTALLED",
    "PYDANTIC_V2",
    "PYDANTIC_VERSION",
    "MongoDsn",
)
