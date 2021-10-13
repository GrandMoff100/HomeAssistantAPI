"""Module for processing responses from homeassistant."""

import simplejson
import json
import requests


from .errors import (
    UnexpectedStatusCodeError,
    UnauthorizedError,
    EndpointNotFoundError,
    MethodNotAllowedError,
    MalformedDataError,
    RequestError
)


class Processing:
    response: requests.Response = None
    _processors: dict = {}
    _async_processors: dict = {}

    def __init__(self, response):
        self.response = response

    def processor(mimetype: str):
        def register_processor(processor):
            Processing._processors.update({mimetype: processor})
        return register_processor

    def async_processor(mimetype: str):
        def register_async_processor(async_processor):
            Processing._async_processors.update({mimetype: async_processor})
        return register_async_processor

    def process_content(self, _async: bool):
        mimetype = self.response.headers.get('content-type')
        if _async:
            processor = self._async_processors.get(mimetype, async_process_text)
        else:
            processor = self._processors.get(mimetype, process_text)
        return processor(self.response)

    def process(self, _async=False):
        if _async:
            status_code = self.response.status
        else:
            status_code = self.response.status_code
        if status_code in (200, 201):
            return self.process_content(_async)
        elif status_code == 400:
            raise RequestError(self.request.content)
        elif status_code == 401:
            raise UnauthorizedError()
        elif status_code == 404:
            raise EndpointNotFoundError(self.response.url)
        elif status_code == 405:
            raise MethodNotAllowedError(self.response.request.method)
        else:
            print("If this happened, please report it at https://github.com/GrandMoff100/HomeAssistantAPI/issues with the request status code and the request content")
            print(self.response.content)
            raise UnexpectedStatusCodeError(self.response.status_code)


# List of default processors
@Processing.processor("application/json")
def process_json(response):
    try:
        return response.json()
    except (
        json.decoder.JSONDecodeError,
        simplejson.decoder.JSONDecodeError
    ):
        raise MalformedDataError(f'Homeassistant responded with non-json response: {repr(response.text)}')


@Processing.processor("text/plain")
def process_text(response):
    return response.text


@Processing.async_processor("application/json")
async def async_process_json(response):
    try:
        return await response.json()
    except (
        json.decoder.JSONDecodeError,
        simplejson.decoder.JSONDecodeError
    ):
        raise MalformedDataError(f'Homeassistant responded with non-json response: {repr(await response.text())}')


@Processing.async_processor("text/plain")
async def async_process_text(response):
    return await response.text()
