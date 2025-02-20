import ssl
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from opensearchpy import AsyncOpenSearch

from fast_healthchecks.checks.opensearch import OpenSearchHealthCheck

pytestmark = pytest.mark.unit

test_ssl_context = ssl.create_default_context()


@pytest.mark.parametrize(
    ("params", "expected", "exception"),
    [
        (
            {},
            "missing 1 required keyword-only argument: 'hosts'",
            TypeError,
        ),
        (
            {
                "hosts": ["localhost:9200"],
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": None,
                "use_ssl": False,
                "verify_certs": False,
                "ssl_show_warn": False,
                "ca_certs": None,
                "timeout": 5.0,
                "name": "OpenSearch",
            },
            None,
        ),
        (
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": False,
                "verify_certs": False,
                "ssl_show_warn": False,
                "ca_certs": None,
                "timeout": 5.0,
                "name": "OpenSearch",
            },
            None,
        ),
        (
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": False,
                "ssl_show_warn": False,
                "ca_certs": None,
                "timeout": 5.0,
                "name": "OpenSearch",
            },
            None,
        ),
        (
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": False,
                "ca_certs": None,
                "timeout": 5.0,
                "name": "OpenSearch",
            },
            None,
        ),
        (
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
                "ca_certs": None,
                "timeout": 5.0,
                "name": "OpenSearch",
            },
            None,
        ),
        (
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
                "ca_certs": "ca_certs",
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
                "ca_certs": "ca_certs",
                "timeout": 5.0,
                "name": "OpenSearch",
            },
            None,
        ),
        (
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
                "ca_certs": "ca_certs",
                "timeout": 1.5,
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
                "ca_certs": "ca_certs",
                "timeout": 1.5,
                "name": "OpenSearch",
            },
            None,
        ),
        (
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
                "ca_certs": "ca_certs",
                "timeout": 1.5,
                "name": "Test",
            },
            {
                "hosts": ["localhost:9200"],
                "http_auth": ("username", "password"),
                "use_ssl": True,
                "verify_certs": True,
                "ssl_show_warn": True,
                "ca_certs": "ca_certs",
                "timeout": 1.5,
                "name": "Test",
            },
            None,
        ),
    ],
)
def test__init(params: dict[str, Any], expected: dict[str, Any] | str, exception: type[BaseException] | None) -> None:
    if exception is not None:
        with pytest.raises(exception, match=expected):
            OpenSearchHealthCheck(**params)
    else:
        obj = OpenSearchHealthCheck(**params)
        assert obj.to_dict() == expected


@pytest.mark.asyncio
async def test_AsyncOpenSearch_args_kwargs() -> None:  # noqa: N802
    health_check = OpenSearchHealthCheck(
        hosts=["localhost:9200"],
        http_auth=("user", "password"),
        use_ssl=True,
        verify_certs=True,
        ssl_show_warn=True,
        ca_certs="ca_certs",
        timeout=1.5,
        name="OpenSearch",
    )
    with patch("fast_healthchecks.checks.opensearch.AsyncOpenSearch", spec=AsyncOpenSearch) as mock:
        await health_check()
        mock.assert_called_once_with(
            hosts=["localhost:9200"],
            http_auth=("user", "password"),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=True,
            ca_certs="ca_certs",
        )


@pytest.mark.asyncio
async def test__call_success() -> None:
    health_check = OpenSearchHealthCheck(hosts=["localhost:9200"])
    mock_client = AsyncMock(spec=AsyncOpenSearch)
    mock_client.info = AsyncMock()
    mock_client.info.side_effect = [
        {
            "name": "b2a910773ffb",
            "cluster_name": "docker-cluster",
            "cluster_uuid": "dIZBX0OeT_qjp0YGVkfe-g",
            "version": {
                "distribution": "opensearch",
                "number": "2.19.0",
                "build_type": "tar",
                "build_hash": "fd9a9d90df25bea1af2c6a85039692e815b894f5",
                "build_date": "2025-02-05T16:13:57.130576800Z",
                "build_snapshot": False,
                "lucene_version": "9.12.1",
                "minimum_wire_compatibility_version": "7.10.0",
                "minimum_index_compatibility_version": "7.0.0",
            },
            "tagline": "The OpenSearch Project: https://opensearch.org/",
        },
    ]
    with patch("fast_healthchecks.checks.opensearch.AsyncOpenSearch", return_value=mock_client):
        result = await health_check()
        assert result.healthy is True
        assert result.name == "OpenSearch"
        assert result.error_details is None
        mock_client.info.assert_called_once_with()
        mock_client.info.assert_awaited_once_with()


@pytest.mark.asyncio
async def test__call_failure() -> None:
    health_check = OpenSearchHealthCheck(hosts=["localhost:9200"])
    mock_client = AsyncMock(spec=AsyncOpenSearch)
    mock_client.info = AsyncMock()
    mock_client.info.side_effect = [Exception("Connection error")]
    with patch("fast_healthchecks.checks.opensearch.AsyncOpenSearch", return_value=mock_client):
        result = await health_check()
        assert result.healthy is False
        assert result.name == "OpenSearch"
        assert "Connection error" in result.error_details
        mock_client.info.assert_called_once_with()
        mock_client.info.assert_awaited_once_with()
        mock_client.close.assert_called_once_with()
        mock_client.close.assert_awaited_once_with()
