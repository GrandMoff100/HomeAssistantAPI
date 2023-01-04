import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

from homeassistant_api import Client

import logging

TIMEOUT = 300


@pytest.fixture(name="wait_for_server", scope="session")
def wait_for_server_fixture() -> None:
    """Waits for the server to be ready."""
    client = Client(
        os.environ["HOMEASSISTANTAPI_URL"],
        os.environ["HOMEASSISTANTAPI_TOKEN"],
    )
    logging.info("Waiting for server to be ready...")
    client.request(method="get", path="", timeout=TIMEOUT)
    logging.info("Server is ready.")

@pytest.fixture(name="cached_client", scope="session")
def setup_cached_client(wait_for_server) -> Generator[Client, None, None]:
    """Initializes the Client and enters a cached session."""
    with Client(
        os.environ["HOMEASSISTANTAPI_URL"],
        os.environ["HOMEASSISTANTAPI_TOKEN"],
    ) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Redefines the event loop with a broader scope."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="async_cached_client", scope="session")
async def setup_async_cached_client(wait_for_server) -> AsyncGenerator[Client, None]:
    """Initializes the Client and enters an async cached session."""
    async with Client(
        os.environ["HOMEASSISTANTAPI_URL"],
        os.environ["HOMEASSISTANTAPI_TOKEN"],
        use_async=True,
    ) as client:
        yield client
