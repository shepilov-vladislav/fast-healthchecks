"""This module provides a health check class for Kafka.

Classes:
    KafkaHealthCheck: A class to perform health checks on Kafka.

Usage:
    The KafkaHealthCheck class can be used to perform health checks on Kafka by calling it.

Example:
    health_check = KafkaHealthCheck(
        bootstrap_servers="localhost:9092",
        security_protocol="PLAINTEXT",
    )
    result = await health_check()
    print(result.healthy)
"""

import ssl
from traceback import format_exc
from typing import Literal, TypeAlias

from fast_healthchecks.checks._base import DEFAULT_HC_TIMEOUT, HealthCheck
from fast_healthchecks.compat import PYDANTIC_INSTALLED
from fast_healthchecks.models import HealthCheckResult

IMPORT_ERROR_MSG = "aiokafka is not installed. Install it with `pip install aiokafka`."

try:
    from aiokafka import AIOKafkaClient
except ImportError as exc:
    raise ImportError(IMPORT_ERROR_MSG) from exc


if PYDANTIC_INSTALLED:
    from pydantic import KafkaDsn
else:
    KafkaDsn: TypeAlias = str  # type: ignore[no-redef]

SecurityProtocol: TypeAlias = Literal["SSL", "PLAINTEXT", "SASL_PLAINTEXT", "SASL_SSL"]
SaslMechanism: TypeAlias = Literal["PLAIN", "GSSAPI", "SCRAM-SHA-256", "SCRAM-SHA-512", "OAUTHBEARER"]


class KafkaHealthCheck(HealthCheck[HealthCheckResult]):
    """A class to perform health checks on Kafka.

    Attributes:
        _bootstrap_servers: The Kafka bootstrap servers.
        _name: The name of the health check.
        _sasl_mechanism: The SASL mechanism to use.
        _sasl_plain_password: The SASL plain password.
        _sasl_plain_username: The SASL plain username.
        _security_protocol: The security protocol to use.
        _ssl_context: The SSL context to use.
        _timeout: The timeout for the health check.
    """

    __slots__ = (
        "_bootstrap_servers",
        "_name",
        "_sasl_mechanism",
        "_sasl_plain_password",
        "_sasl_plain_username",
        "_security_protocol",
        "_ssl_context",
        "_timeout",
    )

    _bootstrap_servers: str
    ssl_context: ssl.SSLContext | None
    security_protocol: SecurityProtocol
    sasl_mechanism: SaslMechanism
    sasl_plain_username: str | None
    sasl_plain_password: str | None
    _timeout: float
    _name: str

    def __init__(  # noqa: PLR0913
        self,
        *,
        bootstrap_servers: str,
        ssl_context: ssl.SSLContext | None = None,
        security_protocol: SecurityProtocol = "PLAINTEXT",
        sasl_mechanism: SaslMechanism = "PLAIN",
        sasl_plain_username: str | None = None,
        sasl_plain_password: str | None = None,
        timeout: float = DEFAULT_HC_TIMEOUT,
        name: str = "Kafka",
    ) -> None:
        """Initializes the KafkaHealthCheck class.

        Args:
            bootstrap_servers: The Kafka bootstrap servers.
            ssl_context: The SSL context to use.
            security_protocol: The security protocol to use.
            sasl_mechanism: The SASL mechanism to use.
            sasl_plain_username: The SASL plain username.
            sasl_plain_password: The SASL plain password.
            timeout: The timeout for the health check.
            name: The name of the health check.
        """
        self._bootstrap_servers = bootstrap_servers
        self._ssl_context = ssl_context
        self._security_protocol = security_protocol
        self._sasl_mechanism = sasl_mechanism
        self._sasl_plain_username = sasl_plain_username
        self._sasl_plain_password = sasl_plain_password
        self._timeout = timeout
        self._name = name

    async def __call__(self) -> HealthCheckResult:
        """Performs the health check on Kafka.

        Returns:
            A HealthCheckResult object.
        """
        client = AIOKafkaClient(
            bootstrap_servers=self._bootstrap_servers,
            client_id="fast_healthchecks",
            request_timeout_ms=int(self._timeout * 1000),
            ssl_context=self._ssl_context,
            security_protocol=self._security_protocol,
            sasl_mechanism=self._sasl_mechanism,
            sasl_plain_username=self._sasl_plain_username,
            sasl_plain_password=self._sasl_plain_password,
        )
        try:
            await client.bootstrap()
            return HealthCheckResult(name=self._name, healthy=True)
        except BaseException:  # noqa: BLE001
            return HealthCheckResult(name=self._name, healthy=False, error_details=format_exc())
        finally:
            await client.close()
