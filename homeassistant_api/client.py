"""Module containing the primary Client class."""
from typing import Dict

from ._async import RawAsyncClient
from .rawclient import RawClient
from .rawapi import RawWrapper


class Client(RawClient, RawAsyncClient):
    """The all-in-one class to interact with Home Assistant!"""

    def __init__(
        self,
        api_url: str,
        token: str,
        global_request_kwargs: Dict[str, str] = {},
    ):
        if token is None:
            raise ValueError("Access-Token cannot be None.")
        super(RawWrapper, self).__init__(
            api_url=api_url,
            token=token,
            global_request_kwargs=global_request_kwargs,
        )
