from typing import Any, TypedDict

import pytest


class BasePostgreSQLConfig(TypedDict, total=True):
    host: str
    port: int
    user: str | None
    password: str | None
    database: str | None


@pytest.fixture(scope="session", name="base_postgresql_config")
def fixture_base_postgresql_config(env_config: dict[str, Any]) -> BasePostgreSQLConfig:
    result: BasePostgreSQLConfig = {
        "host": "localhost",
        "port": 5432,
        "user": None,
        "password": None,
        "database": None,
    }
    for key in ("host", "port", "user", "password", "database"):
        value = env_config.get(f"POSTGRES_{key.upper()}")
        match key:
            case "port":
                if value is not None:
                    result[key] = int(value)
            case _:
                if value is not None:
                    result[key] = str(value)

    return result
