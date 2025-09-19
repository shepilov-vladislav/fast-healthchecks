import os
from http import HTTPStatus

from faststream.asgi import AsgiFastStream
from faststream.kafka import KafkaBroker

from examples.probes import (
    LIVENESS_CHECKS,
    READINESS_CHECKS,
    READINESS_CHECKS_FAIL,
    READINESS_CHECKS_SUCCESS,
    STARTUP_CHECKS,
    custom_handler,
)
from fast_healthchecks.integrations.base import Probe
from fast_healthchecks.integrations.faststream import health

broker = KafkaBroker(os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(","))
app_integration = AsgiFastStream(
    broker,
    asgi_routes=[
        *health(
            Probe(name="liveness", checks=LIVENESS_CHECKS),
            Probe(name="readiness", checks=READINESS_CHECKS),
            Probe(name="startup", checks=STARTUP_CHECKS),
            debug=False,
            prefix="/health",
        ),
    ],
)

app_success = AsgiFastStream(
    broker,
    asgi_routes=[
        *health(
            Probe(name="liveness", checks=[]),
            Probe(name="readiness", checks=READINESS_CHECKS_SUCCESS),
            Probe(name="startup", checks=[]),
            debug=False,
            prefix="/health",
        ),
    ],
)

app_fail = AsgiFastStream(
    broker,
    asgi_routes=[
        *health(
            Probe(name="liveness", checks=[]),
            Probe(name="readiness", checks=READINESS_CHECKS_FAIL),
            Probe(name="startup", checks=[]),
            debug=False,
            prefix="/health",
        ),
    ],
)

app_custom = AsgiFastStream(
    broker,
    asgi_routes=[
        *health(
            Probe(
                name="liveness",
                checks=[],
                summary="Check if the application is alive",
            ),
            Probe(
                name="readiness",
                checks=READINESS_CHECKS_SUCCESS,
                summary="Check if the application is ready",
            ),
            Probe(
                name="startup",
                checks=[],
                summary="Check if the application is starting up",
            ),
            success_handler=custom_handler,
            failure_handler=custom_handler,
            success_status=HTTPStatus.OK,
            failure_status=HTTPStatus.SERVICE_UNAVAILABLE,
            debug=True,
            prefix="/custom_health",
        ),
    ],
)
