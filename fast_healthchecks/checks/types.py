"""Module containing all the health checks."""

from typing import TypeAlias

from fast_healthchecks.checks._base import HealthCheck, HealthCheckDSN
from fast_healthchecks.checks.function import FunctionHealthCheck
from fast_healthchecks.checks.kafka import KafkaHealthCheck
from fast_healthchecks.checks.mongo import MongoHealthCheck
from fast_healthchecks.checks.opensearch import OpenSearchHealthCheck
from fast_healthchecks.checks.postgresql.asyncpg import PostgreSQLAsyncPGHealthCheck
from fast_healthchecks.checks.postgresql.psycopg import PostgreSQLPsycopgHealthCheck
from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck
from fast_healthchecks.checks.redis import RedisHealthCheck
from fast_healthchecks.checks.url import UrlHealthCheck

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
