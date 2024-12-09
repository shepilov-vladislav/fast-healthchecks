import pytest

pytestmark = pytest.mark.imports


def test_import_error_PostgreSQLAsyncPGHealthCheck() -> None:  # noqa: N802
    with pytest.raises(ImportError, match="asyncpg is not installed. Install it with `pip install asyncpg`."):
        from fast_healthchecks.checks.postgresql.asyncpg import PostgreSQLAsyncPGHealthCheck  # noqa: PLC0415, F401


def test_import_error_PostgreSQLPsycopgHealthCheck() -> None:  # noqa: N802
    with pytest.raises(ImportError, match="psycopg is not installed. Install it with `pip install psycopg`."):
        from fast_healthchecks.checks.postgresql.psycopg import PostgreSQLPsycopgHealthCheck  # noqa: PLC0415, F401


def test_import_error_KafkaHealthCheck() -> None:  # noqa: N802
    with pytest.raises(ImportError, match="aiokafka is not installed. Install it with `pip install aiokafka`."):
        from fast_healthchecks.checks.kafka import KafkaHealthCheck  # noqa: PLC0415, F401


def test_import_error_MongoHealthCheck() -> None:  # noqa: N802
    with pytest.raises(ImportError, match="motor is not installed. Install it with `pip install motor`."):
        from fast_healthchecks.checks.mongo import MongoHealthCheck  # noqa: PLC0415, F401


def test_import_error_RabbitMQHealthCheck() -> None:  # noqa: N802
    with pytest.raises(ImportError, match="aio-pika is not installed. Install it with `pip install aio-pika`."):
        from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck  # noqa: PLC0415, F401


def test_import_error_RedisHealthCheck() -> None:  # noqa: N802
    with pytest.raises(ImportError, match="redis is not installed. Install it with `pip install redis`."):
        from fast_healthchecks.checks.redis import RedisHealthCheck  # noqa: PLC0415, F401


def test_import_error_UrlHealthCheck() -> None:  # noqa: N802
    with pytest.raises(ImportError, match="httpx is not installed. Install it with `pip install httpx`."):
        from fast_healthchecks.checks.url import UrlHealthCheck  # noqa: PLC0415, F401
