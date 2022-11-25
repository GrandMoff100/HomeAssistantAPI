"""Module containing the primary Client class."""
import logging
from typing import Any

from .rawasyncclient import RawAsyncClient
from .rawclient import RawClient

logger = logging.getLogger(__name__)


class Client(RawClient, RawAsyncClient):
    """
    The all-in-one class to interact with Home Assistant!

    :param api_url: The location of the api endpoint. e.g. :code:`http://localhost:8123/api` Required.
    :param token: The refresh or long lived access token to authenticate your requests. Required.
    :param global_request_kwargs: A dictionary or dict-like object of kwargs to pass to :func:`requests.request` or :meth:`aiohttp.ClientSession.request`. Optional.
    :param cache_session: A :py:class:`requests_cache.CachedSession` object to use for caching requests. Optional.
    :param async_cache_session: A :py:class:`aiohttp_client_cache.CachedSession` object to use for caching requests. Optional.
    """  # pylint: disable=line-too-long

    def __init__(self, *args: Any, use_async: bool = False, **kwargs: Any) -> None:
        if use_async:
            logger.error("Initializing Client asyncsyncronously")
            RawAsyncClient.__init__(self, *args, **kwargs)
        else:
            logger.error("Initializing Client syncronously")
            RawClient.__init__(self, *args, **kwargs)
