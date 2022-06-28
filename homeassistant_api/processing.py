"""Module for processing responses from homeassistant."""

import inspect
import json
import logging
import sys
from typing import Any, Callable, ClassVar, Dict, Tuple, Union, cast

import simplejson
from aiohttp import ClientResponse
from aiohttp_client_cache.response import CachedResponse as AsyncCachedResponse
from requests import Response
from requests_cache.models.response import CachedResponse

from .errors import (
    EndpointNotFoundError,
    InternalServerError,
    MalformedDataError,
    MethodNotAllowedError,
    ProcessorNotFoundError,
    RequestError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)


AsyncResponseType = Union[AsyncCachedResponse, ClientResponse]
ResponseType = Union[Response, CachedResponse]
AllResponseType = Union[AsyncResponseType, ResponseType]
ProcessorType = Callable[[ResponseType], Any]


class Processing:
    """Uses to processor functions to convert json data into common python data types."""

    _response: AllResponseType
    _processors: ClassVar[Dict[str, Tuple[ProcessorType, ...]]] = {}

    def __init__(self, response: AllResponseType) -> None:
        self._response = response

    @staticmethod
    def processor(mimetype: str) -> Callable[[ProcessorType], ProcessorType]:
        """A decorator used to register a response converter function."""

        def register_processor(processor: ProcessorType) -> ProcessorType:
            if mimetype not in Processing._processors:
                Processing._processors[mimetype] = tuple()
            Processing._processors[mimetype] += (processor,)
            return processor

        return register_processor

    def process_content(self, *, async_: bool = False) -> Any:
        """
        Looks up processors by their Content-Type header and then
        calls the processor with the response.
        """

        mimetype = self._response.headers.get(  # type: ignore [arg-type]
            "content-type",
            "text/plain",
        )  # type: ignore[arg-type]
        for processor in self._processors.get(mimetype, ()):
            if not async_ ^ inspect.iscoroutinefunction(processor):
                logger.debug("Using processor %r on %r", processor, self._response)
                return processor(self._response)
        raise ProcessorNotFoundError(
            f"No response processor found for mimetype {mimetype!r}."
        )

    def process(self) -> Any:
        """Validates the http status code before starting to process the repsonse content"""
        if async_ := isinstance(self._response, AsyncResponseType):
            status_code = self._response.status
        elif isinstance(self._response, ResponseType):
            status_code = self._response.status_code
        if status_code in (200, 201):
            return self.process_content(async_=async_)
        if status_code == 400:
            raise RequestError(self._response.content)
        if status_code == 401:
            raise UnauthorizedError()
        if status_code == 404:
            raise EndpointNotFoundError(self._response.url)
        if status_code == 405:
            method = (
                self._response.request.method
                if hasattr(self._response, "request")
                else self._response.method
            )
            raise MethodNotAllowedError(
                cast(str, method),
            )
        if status_code >= 500:
            raise InternalServerError(status_code, self._response.content)


# List of default processors
@Processing.processor("application/json")
def process_json(response: ResponseType):
    """Returns the json dict content of the response."""
    try:
        return response.json()
    except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError) as err:
        raise MalformedDataError(
            f"Home Assistant responded with non-json response: {repr(response.text)}"
        ) from err


@Processing.processor("application/octet-stream")
def process_text(response: ResponseType):
    """Returns the plaintext of the reponse."""
    return response.text


@Processing.processor("application/json")
async def async_process_json(response: ResponseType):
    """Returns the json dict content of the response."""
    try:
        return await response.json()
    except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError) as err:
        raise MalformedDataError(
            f"Home Assistant responded with non-json response: {repr(await response.text())}"
        ) from err


@Processing.processor("application/octet-stream")
async def async_process_text(response: ResponseType):
    """Returns the plaintext of the reponse."""
    return await response.text()
