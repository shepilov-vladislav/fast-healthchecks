"""Module to check compatibility with Pydantic."""

from typing import TYPE_CHECKING, TypeAlias

try:
    from pydantic.version import VERSION as PYDANTIC_VERSION

    PYDANTIC_INSTALLED = True
    PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")
except ImportError:
    PYDANTIC_INSTALLED = False
    PYDANTIC_VERSION = None
    PYDANTIC_V2 = False


# MongoDsn: in Pydantic v2 it's in pydantic.networks, in v1 it's in the root module
if TYPE_CHECKING:
    try:
        from pydantic.networks import MongoDsn as _RawMongoDsn
    except ImportError:
        from pydantic import MongoDsn as _RawMongoDsn
else:
    _RawMongoDsn = str
MongoDsn: TypeAlias = _RawMongoDsn

# AmqpDsn
if TYPE_CHECKING:
    from pydantic import AmqpDsn as _RawAmqpDsn
else:
    _RawAmqpDsn = str
AmqpDsn: TypeAlias = _RawAmqpDsn

# KafkaDsn
if TYPE_CHECKING:
    from pydantic import KafkaDsn as _RawKafkaDsn
else:
    _RawKafkaDsn = str
KafkaDsn: TypeAlias = _RawKafkaDsn

# PostgresDsn
if TYPE_CHECKING:
    from pydantic import PostgresDsn as _RawPostgresDsn
else:
    _RawPostgresDsn = str
PostgresDsn: TypeAlias = _RawPostgresDsn

# RedisDsn
if TYPE_CHECKING:
    from pydantic import RedisDsn as _RawRedisDsn
else:
    _RawRedisDsn = str
RedisDsn: TypeAlias = _RawRedisDsn

SupportedDsns: TypeAlias = AmqpDsn | KafkaDsn | MongoDsn | PostgresDsn | RedisDsn

__all__ = (
    "PYDANTIC_INSTALLED",
    "PYDANTIC_V2",
    "PYDANTIC_VERSION",
    "AmqpDsn",
    "KafkaDsn",
    "MongoDsn",
    "PostgresDsn",
    "RedisDsn",
    "SupportedDsns",
)
