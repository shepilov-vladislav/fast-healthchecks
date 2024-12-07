import sys

import pytest

from fast_healthchecks.checks.kafka import IMPORT_ERROR_MSG
from tests.utils import patch_import_not_installed


def test_import() -> None:
    sys.modules.pop("aiokafka", None)
    sys.modules.pop("fast_healthchecks.checks.kafka", None)

    with patch_import_not_installed("aiokafka"), pytest.raises(ImportError, match=IMPORT_ERROR_MSG):
        from fast_healthchecks.checks.kafka import KafkaHealthCheck  # noqa: PLC0415, F401
