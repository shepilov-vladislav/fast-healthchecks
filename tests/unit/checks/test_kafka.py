import ssl
from typing import Any
from unittest.mock import patch

import pytest
from aiokafka import AIOKafkaClient

from fast_healthchecks.checks.kafka import KafkaHealthCheck

pytestmark = pytest.mark.unit

test_ssl_context = ssl.create_default_context()


@pytest.mark.parametrize(
    ("params", "expected", "exception"),
    [
        (
            {},
            "missing 1 required keyword-only argument: 'bootstrap_servers'",
            TypeError,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": None,
                "security_protocol": "PLAINTEXT",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "PLAINTEXT",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "BROKEN",
            },
            "Invalid security protocol: BROKEN",
            ValueError,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SSL",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SSL",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "PLAINTEXT",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "PLAINTEXT",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_PLAINTEXT",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "BROKEN",
            },
            "Invalid SASL mechanism: BROKEN",
            ValueError,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "PLAIN",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "GSSAPI",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "GSSAPI",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "SCRAM-SHA-256",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "SCRAM-SHA-256",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "SCRAM-SHA-512",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
                "sasl_plain_password": None,
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
                "sasl_plain_password": "password",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
                "sasl_plain_password": "password",
                "timeout": 5.0,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
                "sasl_plain_password": "password",
                "timeout": 1.5,
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
                "sasl_plain_password": "password",
                "timeout": 1.5,
                "name": "Kafka",
            },
            None,
        ),
        (
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
                "sasl_plain_password": "password",
                "timeout": 1.5,
                "name": "Test",
            },
            {
                "bootstrap_servers": "localhost:9092",
                "ssl_context": test_ssl_context,
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "OAUTHBEARER",
                "sasl_plain_username": "user",
                "sasl_plain_password": "password",
                "timeout": 1.5,
                "name": "Test",
            },
            None,
        ),
    ],
)
def test__init(params: dict[str, Any], expected: dict[str, Any] | str, exception: type[BaseException] | None) -> None:
    if exception is not None and isinstance(expected, str):
        with pytest.raises(exception, match=expected):
            KafkaHealthCheck(**params)  # ty: ignore[missing-argument]
    else:
        obj = KafkaHealthCheck(**params)  # ty: ignore[missing-argument]
        assert obj.to_dict() == expected


@pytest.mark.asyncio
async def test_AIOKafkaClient_args_kwargs() -> None:  # noqa: N802
    health_check = KafkaHealthCheck(
        bootstrap_servers="localhost:9092",
        ssl_context=test_ssl_context,
        security_protocol="SASL_SSL",
        sasl_mechanism="OAUTHBEARER",
        sasl_plain_username="user",
        sasl_plain_password="password",
        timeout=1.5,
    )
    with patch("fast_healthchecks.checks.kafka.AIOKafkaClient", spec=AIOKafkaClient) as mock:
        await health_check()
        mock.assert_called_once_with(
            bootstrap_servers="localhost:9092",
            client_id="fast_healthchecks",
            request_timeout_ms=1.5 * 1000,
            ssl_context=test_ssl_context,
            security_protocol="SASL_SSL",
            sasl_mechanism="OAUTHBEARER",
            sasl_plain_username="user",
            sasl_plain_password="password",
        )


@pytest.mark.asyncio
async def test__call_success() -> None:
    health_check = KafkaHealthCheck(bootstrap_servers="localhost:9092")
    with (
        patch.object(AIOKafkaClient, "bootstrap", return_value=None) as mock_bootstrap,
        patch.object(AIOKafkaClient, "check_version", return_value=None) as mock_check_version,
        patch.object(AIOKafkaClient, "close", return_value=None) as mock_close,
    ):
        result = await health_check()
        assert result.healthy is True
        assert result.name == "Kafka"
        assert result.error_details is None
        mock_bootstrap.assert_called_once_with()
        mock_bootstrap.assert_awaited_once_with()
        mock_check_version.assert_called_once_with()
        mock_check_version.assert_awaited_once_with()
        mock_close.assert_called_once_with()
        mock_close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test__call_failure() -> None:
    health_check = KafkaHealthCheck(bootstrap_servers="localhost:9092")
    with (
        patch.object(AIOKafkaClient, "bootstrap", side_effect=Exception("Connection error")) as mock_bootstrap,
        patch.object(AIOKafkaClient, "close", return_value=None) as mock_close,
    ):
        result = await health_check()
        assert result.healthy is False
        assert result.name == "Kafka"
        assert "Connection error" in str(result.error_details)
        mock_bootstrap.assert_called_once_with()
        mock_bootstrap.assert_awaited_once_with()
        mock_close.assert_called_once_with()
        mock_close.assert_awaited_once_with()
