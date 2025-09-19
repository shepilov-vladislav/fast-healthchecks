from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from examples.probes import (
    LIVENESS_CHECKS,
    READINESS_CHECKS,
    READINESS_CHECKS_FAIL,
    READINESS_CHECKS_SUCCESS,
    STARTUP_CHECKS,
    custom_handler,
)
from fast_healthchecks.integrations.base import Probe
from fast_healthchecks.integrations.litestar import health

app_integration = Litestar(
    route_handlers=[
        *health(
            Probe(name="liveness", checks=LIVENESS_CHECKS),
            Probe(name="readiness", checks=READINESS_CHECKS),
            Probe(name="startup", checks=STARTUP_CHECKS),
            debug=False,
            prefix="/health",
        ),
    ],
)

app_success = Litestar(
    route_handlers=[
        *health(
            Probe(name="liveness", checks=[]),
            Probe(name="readiness", checks=READINESS_CHECKS_SUCCESS),
            Probe(name="startup", checks=[]),
            debug=False,
            prefix="/health",
        ),
    ],
)

app_fail = Litestar(
    route_handlers=[
        *health(
            Probe(name="liveness", checks=[]),
            Probe(name="readiness", checks=READINESS_CHECKS_FAIL),
            Probe(name="startup", checks=[]),
            debug=False,
            prefix="/health",
        ),
    ],
)

app_custom = Litestar(
    route_handlers=[
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
            success_status=HTTP_200_OK,
            failure_status=HTTP_503_SERVICE_UNAVAILABLE,
            debug=True,
            prefix="/custom_health",
        ),
    ],
)
