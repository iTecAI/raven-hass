from dotenv import load_dotenv

load_dotenv()

import pytest
import os


@pytest.fixture
def hass_token() -> str:
    return os.environ["HASS_TOKEN"]


@pytest.fixture
def hass_api() -> str:
    return os.environ["HASS_API"]
