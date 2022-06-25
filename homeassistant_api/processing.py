"""Module for processing responses from homeassistant."""

import inspect
import json
import logging
import sys
from typing import Any, Callable, ClassVar, Dict, Tuple, Union, cast

import simplejson
from aiohttp import ClientResponse
from aiohttp_client_cache.response import CachedResponse as AsyncCachedResponse
from pydantic import Field
from requests import Response
from requests_cache.models.response import CachedResponse

from .errors import (
    EndpointNotFoundError,
    MalformedDataError,
    MethodNotAllowedError,
    ProcessorNotFoundError,
    RequestError,
    UnauthorizedError,
    UnexpectedStatusCodeError,
)
from .models import BaseModel

logger = logging.getLogger(__name__)


class Processing(BaseModel):
    """Uses to processor functions to convert json data into common python data types."""

    _response: Union[
        Response,
        CachedResponse,
        ClientResponse,
        AsyncCachedResponse,
    ] = Field(exlucde=True, repr=False)
    _processors: ClassVar[Dict[str, Tuple[Callable, ...]]] = {}

    @staticmethod
    def processor(mimetype: str):
        """A decorator used to register a response converter function."""

        def register_processor(processor):
            if mimetype not in Processing._processors:
                Processing._processors[mimetype] = tuple()
            Processing._processors[mimetype] = (processor,) + Processing._processors[
                mimetype
            ]
            return processor

        return register_processor

    def process_content(self, _async: bool):
        """Looks up processors by content-type and then calls the processor with the response."""

        mimetype = self._response.headers.get("content-type", "text/plain")  # type: ignore[arg-type]
        for processor in self._processors.get(mimetype, ()):
            if not _async ^ inspect.iscoroutinefunction(processor):
                logger.debug("Using processor %r on %r", processor, self._response)
                return processor(self._response)
        if _async:
            raise ProcessorNotFoundError(
                f"No async response processor registered for mimetype {mimetype!r}."
            )
        raise ProcessorNotFoundError(
            f"No non-async response processor found for mimetype {mimetype!r}."
        )

    def process(self) -> Any:
        """Validates the http status code before starting to process the repsonse content"""
        if _async := isinstance(self._response, (ClientResponse, AsyncCachedResponse)):
            status_code = self._response.status
        elif isinstance(self._response, Response):
            status_code = self._response.status_code
        else:
            raise ValueError(
                f"Only expected a response object from requests or aiohttp. Got {self._response!r}"
            )
        if status_code in (200, 201):
            return self.process_content(_async)
        if status_code == 400:
            raise RequestError(self._response.content)
        if status_code == 401:
            raise UnauthorizedError()
        if status_code == 404:
            raise EndpointNotFoundError(self._response.url)
        if status_code == 405:
            raise MethodNotAllowedError(
                cast(str, self._response.request.method),
            )  # type: ignore[union-attr]
        print(
            "If this happened, "
            "please report it at https://github.com/GrandMoff100/HomeAssistantAPI/issues "
            "with the request status code and the request content",
            file=sys.stderr,
        )
        raise UnexpectedStatusCodeError(
            status_code,
            self._response.content,
        )


# List of default processors
@Processing.processor("application/json")
def process_json(response):
    """Returns the json dict content of the response."""
    try:
        return response.json()
    except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError) as err:
        raise MalformedDataError(
            f"Home Assistant responded with non-json response: {repr(response.text)}"
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
            f"Home Assistant responded with non-json response: {repr(await response.text())}"
        ) from err


@Processing.processor("application/octet-stream")
async def async_process_text(response):
    """Returns the plaintext of the reponse."""
    return await response.text()
