"""Module containing the primary Client class."""
from ._async import RawAsyncClient
from .rawclient import RawClient


class Client(RawClient, RawAsyncClient):
    """The all-in-one class to interact with Home Assistant!"""
