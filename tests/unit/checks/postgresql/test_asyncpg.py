import ssl
import sys
from typing import Any
from urllib.parse import ParseResult, unquote, urlparse

import pytest

from fast_healthchecks.checks.postgresql.asyncpg import IMPORT_ERROR_MSG, PostgreSQLAsyncPGHealthCheck
from fast_healthchecks.checks.postgresql.base import create_ssl_context
from tests.utils import (
    TEST_SSLCERT,
    TEST_SSLKEY,
    TEST_SSLROOTCERT,
    create_temp_files,
    patch_import_not_installed,
)


def to_dict(obj: PostgreSQLAsyncPGHealthCheck) -> dict[str, Any]:
    return {
        "host": obj._host,
        "port": obj._port,
        "user": obj._user,
        "password": obj._password,
        "database": obj._database,
        "ssl": obj._ssl,
        "direct_tls": obj._direct_tls,
    }


def test_import() -> None:
    sys.modules.pop("asyncpg", None)
    sys.modules.pop("fast_healthchecks.checks.postgresql.asyncpg", None)

    with patch_import_not_installed("asyncpg"), pytest.raises(ImportError, match=IMPORT_ERROR_MSG):
        from fast_healthchecks.checks.postgresql.asyncpg import PostgreSQLAsyncPGHealthCheck  # noqa: PLC0415, F401


@pytest.mark.parametrize(
    ("dsn", "expected", "exception"),
    [
        (
            "postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=broken",
            "Invalid sslmode: broken",
            ValueError,
        ),
        (
            "postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=disable",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=disable&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=disable&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=disable&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=allow",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=allow&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=allow&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=allow&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": None,
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=prefer",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("prefer", None, None, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=prefer&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("prefer", TEST_SSLCERT, None, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=prefer&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("prefer", TEST_SSLCERT, TEST_SSLKEY, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=prefer&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("prefer", TEST_SSLCERT, TEST_SSLKEY, TEST_SSLROOTCERT),
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=require",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("require", None, None, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=require&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("require", TEST_SSLCERT, None, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=require&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("require", TEST_SSLCERT, TEST_SSLKEY, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=require&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("require", TEST_SSLCERT, TEST_SSLKEY, TEST_SSLROOTCERT),
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-ca",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("verify-ca", None, None, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-ca&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("verify-ca", TEST_SSLCERT, None, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-ca&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("verify-ca", TEST_SSLCERT, TEST_SSLKEY, None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-ca&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("verify-ca", TEST_SSLCERT, TEST_SSLKEY, TEST_SSLROOTCERT),
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-full",
            "sslcert is required for verify-full",
            ValueError,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-full&sslcert={TEST_SSLCERT}",
            "\\[SSL\\] PEM lib \\(_ssl.c:\\d+\\)",
            ssl.SSLError,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-full&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("verify-full", unquote(TEST_SSLCERT), unquote(TEST_SSLKEY), None),
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+asyncpg://postgres:pass@localhost:5432/db?sslmode=verify-full&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "direct_tls": False,
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "ssl": ("verify-full", unquote(TEST_SSLCERT), unquote(TEST_SSLKEY), unquote(TEST_SSLROOTCERT)),
                "user": "postgres",
            },
            None,
        ),
    ],
)
def test_from_dsn(dsn: str, expected: dict[str, Any] | str, exception: type[BaseException] | None) -> None:
    parse_result: ParseResult = urlparse(dsn)
    query = {k: unquote(v) for k, v in (q.split("=") for q in parse_result.query.split("&"))}
    files = [y for x, y in query.items() if x in {"sslcert", "sslkey", "sslrootcert"}]

    if exception is not None:
        with pytest.raises(exception, match=expected), create_temp_files(files):
            PostgreSQLAsyncPGHealthCheck.from_dsn(dsn=dsn)
    else:
        with create_temp_files(files):
            check = PostgreSQLAsyncPGHealthCheck.from_dsn(dsn=dsn)
            if "ssl" in expected and expected["ssl"] is not None:
                expected["ssl"] = create_ssl_context(*expected["ssl"])
            assert to_dict(check) == expected
