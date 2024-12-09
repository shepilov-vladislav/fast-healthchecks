import json

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from examples.fastapi_example.main import app_custom, app_fail, app_success

pytestmark = pytest.mark.unit

client = TestClient(app_success)


def test_liveness_probe() -> None:
    response = client.get("/health/liveness")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_readiness_probe() -> None:
    response = client.get("/health/readiness")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_startup_probe() -> None:
    response = client.get("/health/startup")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""


def test_readiness_probe_fail() -> None:
    client_fail = TestClient(app_fail)
    response = client_fail.get("/health/readiness")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.content == b""


def test_custom_handler() -> None:
    client_custom = TestClient(app_custom)
    response = client_custom.get("/custom_health/readiness")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == json.dumps(
        {"results": [{"name": "Async dummy", "healthy": True, "error_details": None}], "allow_partial_failure": False},
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
    ).encode("utf-8")
