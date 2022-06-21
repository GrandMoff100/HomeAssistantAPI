import os
from homeassistant_api import Client


CLIENT = Client(
    "http://localhost:8123/api",
    os.environ["HOMEASSISTANTAPI_TOKEN"]
)


def test_check_running() -> None:
    pass
