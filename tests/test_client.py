import os

import aiohttp_client_cache
import requests_cache

from homeassistant_api import Client


def test_custom_cached_session() -> None:
    with Client(
        os.environ["HOMEASSISTANTAPI_URL"],
        os.environ["HOMEASSISTANTAPI_TOKEN"],
        cache_session=requests_cache.CachedSession(),
    ):
        pass


def test_default_session() -> None:
    with Client(
        os.environ["HOMEASSISTANTAPI_URL"],
        os.environ["HOMEASSISTANTAPI_TOKEN"],
        cache_session=False,
    ):
        pass


async def test_custom_async_cached_session() -> None:
    async with Client(
        os.environ["HOMEASSISTANTAPI_URL"],
        os.environ["HOMEASSISTANTAPI_TOKEN"],
        async_cache_session=aiohttp_client_cache.CachedSession(
            cache=aiohttp_client_cache.SQLiteBackend(
                cache_name="test_custom_async_cached_session.sqlite",
                expire_after=10,
            ),
        ),
        use_async=True,
    ):
        pass


async def test_default_async_session() -> None:
    async with Client(
        os.environ["HOMEASSISTANTAPI_URL"],
        os.environ["HOMEASSISTANTAPI_TOKEN"],
        async_cache_session=False,
        use_async=True,
    ):
        pass
