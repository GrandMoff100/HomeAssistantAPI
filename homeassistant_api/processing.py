"""Module for processing responses from homeassistant."""

import inspect
import json
from typing import Callable, Dict, Tuple, Union

import simplejson
from aiohttp import ClientResponse
from aiohttp_client_cache.response import CachedResponse as AsyncCachedResponse
from pydantic import BaseModel
from requests import Response
from requests_cache import CachedResponse

from .errors import (
    EndpointNotFoundError,
    MalformedDataError,
    MethodNotAllowedError,
    ProcessorNotFoundError,
    RequestError,
    UnauthorizedError,
    UnexpectedStatusCodeError,
)

SyncResponse = Union[Response, CachedResponse]
AsyncResponse = Union[ClientResponse, AsyncCachedResponse]


class Processing(BaseModel):
    """Uses to processor functions to convert json data into common python data types."""

    response: Union[SyncResponse, AsyncResponse]
    _processors: Dict[str, Tuple[Callable, ...]] = {}

    class Config:  # pylint: disable=too-few-public-methods
        """A pydantic config class."""

        arbitrary_types_allowed: bool = True

    @staticmethod
    def processor(mimetype: str):
        """A decorator used to register a response converter function."""

        def register_processor(processor):
            if mimetype not in Processing._processors:
                Processing._processors[mimetype] = tuple()
            Processing._processors[mimetype] += (processor,)
            return processor

        return register_processor

    def process_content(self, _async: bool):
        """Looks up processors by content-type and then calls the processor with the response."""
        mimetype = self.response.headers.get("content-type", "text/plain")
        for processor in self._processors.get(mimetype, ()):
            if not _async ^ inspect.iscoroutinefunction(processor):
                return processor(self.response)
        if _async:
            raise ProcessorNotFoundError(
                f"No async response processor registered for mimetype {mimetype!r}"
            )
        raise ProcessorNotFoundError(
            f"No non-async response processor found for mimetype {mimetype!r}"
        )

    def process(self):
        """Validates the http status code before starting to process the repsonse content"""
        if _async := isinstance(self.response, ClientResponse):
            status_code = self.response.status
        elif _async := isinstance(self.response, AsyncCachedResponse):
            status_code = self.response.status
        elif (_async := not isinstance(self.response, Response)) is False:
            status_code = self.response.status_code
        else:
            raise ValueError(
                f"Only expected a response object from requests or aiohttp. Got {self.response!r}"
            )
        if status_code in (200, 201):
            return self.process_content(_async)
        if status_code == 400:
            raise RequestError(self.response.content)
        if status_code == 401:
            raise UnauthorizedError()
        if status_code == 404:
            raise EndpointNotFoundError(self.response.url)
        if status_code == 405:
            raise MethodNotAllowedError(self.response.request.method)
        print(
            "If this happened, "
            "please report it at https://github.com/GrandMoff100/HomeAssistantAPI/issues "
            "with the request status code and the request content"
        )
        raise UnexpectedStatusCodeError(
            self.response.status_code,
            self.response.content,
        )


# List of default processors
@Processing.processor("application/json")
def process_json(response):
    """Returns the json dict content of the response."""
    try:
        return response.json()
    except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError) as err:
        raise MalformedDataError(
            f"Homeassistant responded with non-json response: {repr(response.text)}"
        ) from err


@Processing.processor("application/octet-stream")
def process_text(response):
    """Returns the plaintext of the reponse."""
    return response.text


@Processing.processor("application/json")
async def async_process_json(response):
    """Returns the json dict content of the response."""
    try:
        return await response.json()
    except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError) as err:
        raise MalformedDataError(
            f"Homeassistant responded with non-json response: {repr(await response.text())}"
        ) from err


@Processing.processor("application/octet-stream")
async def async_process_text(response):
    """Returns the plaintext of the reponse."""
    return await response.text()
