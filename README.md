<h1 align="center" style="vertical-align: middle;">
  <img src="https://raw.githubusercontent.com/shepilov-vladislav/fast-healthchecks/refs/heads/main/docs/img/green.svg" width="30"> <strong>FastHealthcheck</strong>
</h1>

<b>Framework agnostic health checks with integrations for most popular ASGI frameworks: [FastAPI](https://github.com/fastapi/fastapi) / [Faststream](https://github.com/airtai/faststream) / [Litestar](https://github.com/litestar-org/litestar) to help you to implement the [Health Check API](https://microservices.io/patterns/observability/health-check-api.html) pattern</b>

---

<p align="center">

  <a href="https://github.com/shepilov-vladislav/fast-healthchecks/actions/workflows/1_test.yml" target="_blank">
    <img src="https://github.com/shepilov-vladislav/fast-healthchecks/actions/workflows/1_test.yml/badge.svg?branch=main" alt="Test Passing"/>
  </a>

  <a href="https://codecov.io/gh/shepilov-vladislav/fast-healthchecks" target="_blank">
    <img src="https://codecov.io/gh/shepilov-vladislav/fast-healthchecks/branch/main/graph/badge.svg?token=ddDOL8qZLp" alt="Coverage"/>
  </a>

  <!-- <a href="https://www.pepy.tech/projects/fast-healthchecks" target="_blank">
    <img src="https://static.pepy.tech/personalized-badge/fast-healthchecks?period=month&units=international_system&left_color=grey&right_color=green&left_text=downloads/month" alt="Downloads"/>
  </a> -->

  <a href="https://pypi.org/project/fast-healthchecks" target="_blank">
    <img src="https://img.shields.io/pypi/v/fast-healthchecks?label=PyPI" alt="Package version"/>
  </a>

  <a href="https://pypi.org/project/fast-healthchecks" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fast-healthchecks.svg" alt="Supported Python versions"/>
  </a>

  <a href="https://github.com/shepilov-vladislav/fast-healthchecks/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/shepilov-vladislav/fast-healthchecks.png" alt="License"/>
  </a>

<p>

---

## Installation

With `pip`:
```bash
pip install fast-healthcheck
```

With `poetry`:
```bash
poetry add fast-healthcheck
```

With `uv`:
```bash
uv add fast-healthcheck
```

## Quick Start

Examples:
- [FastAPI example](./examples/fastapi_example)
- [Faststream example](./examples/faststream_example)
- [Litestar example](./examples/litestar_example)

```python
import asyncio
import os
import time

from fastapi import FastAPI

from fast_healthchecks.checks.function import FunctionHealthCheck
from fast_healthchecks.checks.kafka import KafkaHealthCheck
from fast_healthchecks.checks.mongo import MongoHealthCheck
from fast_healthchecks.checks.postgresql.asyncpg import PostgreSQLAsyncPGHealthCheck
from fast_healthchecks.checks.postgresql.psycopg import PostgreSQLPsycopgHealthCheck
from fast_healthchecks.checks.rabbitmq import RabbitMQHealthCheck
from fast_healthchecks.checks.redis import RedisHealthCheck
from fast_healthchecks.checks.url import UrlHealthCheck
from fast_healthchecks.integrations.fastapi import HealthcheckRouter, Probe


def sync_dummy_check() -> bool:
    time.sleep(0.1)
    return True


async def async_dummy_check() -> bool:
    await asyncio.sleep(0.1)
    return True


app = FastAPI()
app.include_router(
    HealthcheckRouter(
        Probe(
            name="liveness",
            checks=[
                FunctionHealthCheck(func=sync_dummy_check, name="Sync dummy"),
            ],
        ),
        Probe(
            name="readiness",
            checks=[
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
            ],
        ),
        Probe(
            name="startup",
            checks=[
                FunctionHealthCheck(func=async_dummy_check, name="Async dummy"),
            ],
        ),
        debug=True,
        prefix="/health",
    ),
)
```

## Development

### Setup environment

```bash
git clone https://github.com/shepilov-vladislav/fast-healthchecks.git
cd fast-healthchecks
uv sync --group=dev --group=docs --all-extras
```

### Run linters

```bash
make lint
```

### Run all tests

```bash
make tests-all
```

### Serve documentation

```bash
make serve-docs
```

## Known alternatives

- [FastAPI Health](https://github.com/Kludex/fastapi-health)
- [FastAPI Health Monitor](https://github.com/adamkirchberger/fastapi-health-monitor)
- [fastapi_healthz](https://github.com/matteocacciola/fastapi_healthz)
- [fastapi_healthcheck](https://github.com/jtom38/fastapi_healthcheck)

## License

This project is licensed under the terms of the MIT license.
