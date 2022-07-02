"""Module containing the primary Client class."""
from typing import Any

from .rawasyncclient import RawAsyncClient
from .rawclient import RawClient


class Client(RawClient, RawAsyncClient):
    """
    The all-in-one class to interact with Home Assistant!

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: A dictionary or dict-like object of kwargs to pass to :func:`requests.request` or :meth:`aiohttp.ClientSession.request`. Optional.
    :param cache_session: A :py:class:`requests_cache.CachedSession` object to use for caching requests. Optional.
    :param async_cache_session: A :py:class:`aiohttp_client_cache.CachedSession` object to use for caching requests. Optional.
    """  # pylint: disable=line-too-long

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "cache_session" in kwargs:
            RawClient.__init__(self, *args, **kwargs)
        elif "async_cache_session" in kwargs:
            RawAsyncClient.__init__(self, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
