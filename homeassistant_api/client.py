"""Module containing the primary Client class."""
from typing import Dict, Optional

from ._async import RawAsyncClient
from .rawapi import RawWrapper
from .rawclient import RawClient


class Client(RawClient, RawAsyncClient):
    """The all-in-one class to interact with Home Assistant!"""

    def __init__(
        self,
        api_url: str,
        token: str,
        global_request_kwargs: Optional[Dict[str, str]] = None,
    ):
        if token is None:
            raise ValueError("Access-Token cannot be None.")
        if global_request_kwargs is None:
            global_request_kwargs = {}
        super(RawWrapper, self).__init__(  # pylint: disable=bad-super-call
            api_url=api_url,
            token=token,
            global_request_kwargs=global_request_kwargs,
        )
