"""Module for processing responses from homeassistant."""

import requests
import dataclasses
import asyncio


from .errors import (
    UnexpectedStatusCodeError,
    UnauthorizedError,
    EndpointNotFoundError,
    MethodNotAllowedError,
    RequestError
)


@dataclasses.dataclass()
class Processing:
    response: requests.Response

    _processors: dict = {}

    _async_processors: dict = {}

    def processor(self, mimetype: str):
        def register_processor(processor):
            if asyncio.iscoroutine(processor):
                self._async_processors.update((mimetype, processor))
            else:
                self._processors.update((mimetype, processor))
        return register_processor

    def process_content(self, _async: bool):
        mimetype = self.response.headers.get('content-type')
        if _async:
            processor = self._processors.get(mimetype)
        else:
            processor = self._async_processors.get(mimetype)
        return processor(self)

    def process(self, _async=False):
        if self.response.status_code in (200, 201):
            return self.process_content(_async)
        elif self.response.status_code == 400:
            raise RequestError(self.request.content)
        elif self.response.status_code == 401:
            raise UnauthorizedError()
        elif self.response.status_code == 404:
            raise EndpointNotFoundError(self.response.url)
        elif self.response.status_code == 405:
            raise MethodNotAllowedError(self.response.request.method)
        else:
            print("If this happened, please report it at https://github.com/GrandMoff100/HomeAssistantAPI/issues with the request status code and the request content")
            print(self.response.content)
            raise UnexpectedStatusCodeError(self.response.status_code)

