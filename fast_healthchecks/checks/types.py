"""Module containing all the health checks."""

from typing import Any, TypeAlias

from fast_healthchecks.checks._base import HealthCheck, HealthCheckDSN

try:
    from fast_healthchecks.checks.function import FunctionHealthCheck
except ImportError:
    FunctionHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.kafka import KafkaHealthCheck
except ImportError:
    KafkaHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.mongo import MongoHealthCheck
except ImportError:
    MongoHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.opensearch import OpenSearchHealthCheck
except ImportError:
    OpenSearchHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.postgresql.asyncpg import PostgreSQLAsyncPGHealthCheck
except ImportError:
    PostgreSQLAsyncPGHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.postgresql.psycopg import PostgreSQLPsycopgHealthCheck
except ImportError:
    PostgreSQLPsycopgHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck
except ImportError:
    RabbitMQHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck
except ImportError:
    RabbitMQHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.redis import RedisHealthCheck
except ImportError:
    RedisHealthCheck = Any  # ty: ignore[invalid-assignment]
try:
    from fast_healthchecks.checks.url import UrlHealthCheck
except ImportError:
    UrlHealthCheck = Any  # ty: ignore[invalid-assignment]

Check: TypeAlias = (
    FunctionHealthCheck
    | KafkaHealthCheck
    | MongoHealthCheck
    | OpenSearchHealthCheck
    | PostgreSQLAsyncPGHealthCheck
    | PostgreSQLPsycopgHealthCheck
    | RabbitMQHealthCheck
    | RedisHealthCheck
    | UrlHealthCheck
)

__all__ = (
    "Check",
    "HealthCheck",
    "HealthCheckDSN",
)
