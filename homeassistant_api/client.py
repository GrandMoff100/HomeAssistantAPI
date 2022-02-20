"""Module containing the primary Client class."""
from ._async import RawAsyncClient
from .rawclient import RawClient


class Client(RawClient, RawAsyncClient):  # type: ignore[misc]
    """The all-in-one class to interact with Home Assistant!"""
