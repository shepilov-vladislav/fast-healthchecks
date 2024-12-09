import os
from typing import Any

import pytest
from dotenv import dotenv_values


@pytest.fixture(scope="session", name="env_config")
def fixture_env_config() -> dict[str, Any]:
    return {
        **dotenv_values(".env"),  # load shared default test environment variables
        **os.environ,  # override loaded values with environment variables
    }
