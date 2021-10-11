"""Module for """

import json
import simplejson
import requests
import dataclasses

from .errors import (
    MalformedDataError,
    UnexpectedStatusCodeError,
    UnauthorizedError,
    EndpointNotFoundError,
    MethodNotAllowedError,
    RequestError
)


@dataclasses.dataclass()
class Processing:
    response: requests.Response

    def process_json(self):
        try:
            return self.response.json()
        except (
            json.decoder.JSONDecodeError,
            simplejson.decoder.JSONDecodeError
        ) as exc:
            raise MalformedDataError(f"Json content could not be parsed correctly: {exc}")

    def process_content(self):
        return self.process_json()

    def process(self):
        if self.response.status_code in (200, 201):
            return self.process_content()
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

