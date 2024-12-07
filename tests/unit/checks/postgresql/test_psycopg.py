import ssl
import sys
from typing import Any
from urllib.parse import ParseResult, unquote, urlparse

import pytest

from fast_healthchecks.checks.postgresql.base import create_ssl_context
from fast_healthchecks.checks.postgresql.psycopg import IMPORT_ERROR_MSG, PostgreSQLPsycopgHealthCheck
from tests.utils import (
    TEST_SSLCERT,
    TEST_SSLKEY,
    TEST_SSLROOTCERT,
    create_temp_files,
    patch_import_not_installed,
)


def to_dict(obj: PostgreSQLPsycopgHealthCheck) -> dict[str, Any]:
    return {
        "host": obj._host,
        "port": obj._port,
        "user": obj._user,
        "password": obj._password,
        "database": obj._database,
        "sslmode": obj._sslmode,
        "sslcert": obj._sslcert,
        "sslkey": obj._sslkey,
        "sslrootcert": obj._sslrootcert,
    }


def test_import() -> None:
    sys.modules.pop("psycopg", None)
    sys.modules.pop("fast_healthchecks.checks.postgresql.psycopg", None)

    with patch_import_not_installed("psycopg"), pytest.raises(ImportError, match=IMPORT_ERROR_MSG):
        from fast_healthchecks.checks.postgresql.psycopg import PostgreSQLPsycopgHealthCheck  # noqa: PLC0415, F401


@pytest.mark.parametrize(
    ("dsn", "expected", "exception"),
    [
        (
            "postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=broken",
            "Invalid sslmode: broken",
            ValueError,
        ),
        (
            "postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=disable",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": None,
                "sslkey": None,
                "sslmode": "disable",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=disable&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": unquote(TEST_SSLCERT),
                "sslkey": None,
                "sslmode": "disable",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=disable&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": unquote(TEST_SSLCERT),
                "sslkey": unquote(TEST_SSLKEY),
                "sslmode": "disable",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=disable&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": unquote(TEST_SSLCERT),
                "sslkey": unquote(TEST_SSLKEY),
                "sslmode": "disable",
                "sslrootcert": unquote(TEST_SSLROOTCERT),
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=allow",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": None,
                "sslkey": None,
                "sslmode": "allow",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=allow&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": None,
                "sslmode": "allow",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=allow&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": TEST_SSLKEY,
                "sslmode": "allow",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=allow&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": TEST_SSLKEY,
                "sslmode": "allow",
                "sslrootcert": TEST_SSLROOTCERT,
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=prefer",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": None,
                "sslkey": None,
                "sslmode": "prefer",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=prefer&sslcert={TEST_SSLCERT}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": None,
                "sslmode": "prefer",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=prefer&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": TEST_SSLKEY,
                "sslmode": "prefer",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=prefer&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": TEST_SSLKEY,
                "sslmode": "prefer",
                "sslrootcert": TEST_SSLROOTCERT,
                "user": "postgres",
            },
            None,
        ),
        (
            "postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=verify-full",
            "sslcert is required for verify-full",
            ValueError,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=verify-full&sslcert={TEST_SSLCERT}",
            "\\[SSL\\] PEM lib \\(_ssl.c:\\d+\\)",
            ssl.SSLError,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=verify-full&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": TEST_SSLKEY,
                "sslmode": "verify-full",
                "sslrootcert": None,
                "user": "postgres",
            },
            None,
        ),
        (
            f"postgresql+psycopg://postgres:pass@localhost:5432/db?sslmode=verify-full&sslcert={TEST_SSLCERT}&sslkey={TEST_SSLKEY}&sslrootcert={TEST_SSLROOTCERT}",
            {
                "database": "db",
                "host": "localhost",
                "password": "pass",
                "port": 5432,
                "sslcert": TEST_SSLCERT,
                "sslkey": TEST_SSLKEY,
                "sslmode": "verify-full",
                "sslrootcert": TEST_SSLROOTCERT,
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
            PostgreSQLPsycopgHealthCheck.from_dsn(dsn=dsn)
    else:
        with create_temp_files(files):
            check = PostgreSQLPsycopgHealthCheck.from_dsn(dsn=dsn)
            if "ssl" in expected and expected["ssl"] is not None:
                expected["ssl"] = create_ssl_context(*expected["ssl"])
            assert to_dict(check) == expected
