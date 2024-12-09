import asyncio
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from fast_healthchecks.checks import Check
from fast_healthchecks.checks.function import FunctionHealthCheck
from fast_healthchecks.checks.kafka import KafkaHealthCheck
from fast_healthchecks.checks.mongo import MongoHealthCheck
from fast_healthchecks.checks.postgresql.asyncpg import PostgreSQLAsyncPGHealthCheck
from fast_healthchecks.checks.postgresql.psycopg import PostgreSQLPsycopgHealthCheck
from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck
from fast_healthchecks.checks.redis import RedisHealthCheck
from fast_healthchecks.checks.url import UrlHealthCheck
from fast_healthchecks.integrations.base import ProbeAsgiResponse

load_dotenv(Path(__file__).parent.parent / ".env")


def sync_dummy_check() -> bool:
    time.sleep(0.1)
    return True


async def async_dummy_check() -> bool:
    await asyncio.sleep(0.1)
    return True


async def async_dummy_check_fail() -> bool:
    msg = "Failed"
    raise Exception(msg) from None  # noqa: TRY002
    await asyncio.sleep(0.1)
    return False


LIVENESS_CHECKS: list[Check] = [
    FunctionHealthCheck(func=sync_dummy_check, name="Sync dummy"),
]

READINESS_CHECKS: list[Check] = [
    KafkaHealthCheck(
        bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"],
        name="Kafka",
    ),
    MongoHealthCheck.from_dsn(os.environ["MONGO_DSN"], name="Mongo"),
    PostgreSQLAsyncPGHealthCheck.from_dsn(os.environ["POSTGRES_DSN"], name="PostgreSQL asyncpg"),
    PostgreSQLPsycopgHealthCheck.from_dsn(os.environ["POSTGRES_DSN"], name="PostgreSQL psycopg"),
    RabbitMQHealthCheck.from_dsn(os.environ["RABBITMQ_DSN"], name="RabbitMQ"),
    RedisHealthCheck.from_dsn(os.environ["REDIS_DSN"], name="Redis"),
    UrlHealthCheck(url="https://httpbin.org/status/200", name="URL 200"),
]

STARTUP_CHECKS: list[Check] = [
    FunctionHealthCheck(func=async_dummy_check, name="Async dummy"),
]

READINESS_CHECKS_SUCCESS: list[Check] = [
    FunctionHealthCheck(func=async_dummy_check, name="Async dummy"),
]
READINESS_CHECKS_FAIL: list[Check] = [
    FunctionHealthCheck(func=async_dummy_check_fail, name="Async dummy fail"),
]


async def custom_handler(response: ProbeAsgiResponse) -> Any:  # noqa: ANN401, RUF029
    """Custom handler for probes."""
    return response.data
