import shutil
import tempfile
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest.mock import patch
from urllib.parse import quote

__all__ = (
    "SSLCERT_NAME",
    "SSLKEY_NAME",
    "SSLROOTCERT_NAME",
    "create_temp_files",
    "patch_import_not_installed",
)


@contextmanager
def patch_import_not_installed(lib: str) -> None:
    original_import = __import__

    def mocked_import(
        name: str,
        globals: Mapping[str, Any] | None = ...,  # noqa: A002
        locals: Mapping[str, Any] | None = ...,  # noqa: A002
        fromlist: Sequence[str] = ...,
        level: int = ...,
    ) -> Any:  # noqa: ANN401
        if name == lib:
            msg = f"{lib} not found"
            raise ImportError(msg) from None
        return original_import(name, globals, locals, fromlist, level)

    with patch("builtins.__import__", side_effect=mocked_import):
        yield


SSLCERT_NAME = "cert.crt"
SSLKEY_NAME = "key.key"
SSLROOTCERT_NAME = "ca.crt"
TEST_CERT_LOCATION = Path(__file__).parent.parent / "certs"

SSL_FILES_MAP = {
    SSLCERT_NAME: TEST_CERT_LOCATION / SSLCERT_NAME,
    SSLKEY_NAME: TEST_CERT_LOCATION / SSLKEY_NAME,
    SSLROOTCERT_NAME: TEST_CERT_LOCATION / SSLROOTCERT_NAME,
}


temp_dir = tempfile.gettempdir()

TEST_SSLCERT = quote(f"{temp_dir}/{SSLCERT_NAME}")
TEST_SSLKEY = quote(f"{temp_dir}/{SSLKEY_NAME}")
TEST_SSLROOTCERT = quote(f"{temp_dir}/{SSLROOTCERT_NAME}")


@contextmanager
def create_temp_files(temp_file_paths: list[str]) -> None:
    paths = [Path(temp_file_path) for temp_file_path in temp_file_paths]
    for path in paths:
        if path.name in SSL_FILES_MAP:
            shutil.copy(SSL_FILES_MAP[path.name], path)
        else:
            with path.open("w") as f:
                f.write("Temporary content.")
                f.flush()

    yield

    for path in paths:
        path.unlink()
