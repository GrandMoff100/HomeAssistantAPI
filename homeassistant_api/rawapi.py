"""Module for parent RawWrapper class"""

import os
import json
import simplejson
import requests
from typing import Union

from .errors import MalformedDataError, ResponseError


class RawWrapper:
    global_request_kwargs = {}

    """Builds, and makes requests to the API"""

    def __init__(self, api_url: str, token: str) -> None:
        """Prepares and stores API URL and Love Lived Access Token token"""
        self.api_url = api_url
        if not self.api_url.endswith('/'):
            self.api_url += '/'
        self._token = token

    def endpoint(self, path: str) -> str:
        """Joins the api base url with a local path to an absolute url"""
        url = os.path.join(self.api_url, path)
        return url

    @property
    def _headers(self) -> dict:
        """Constructs the headers to send to the api for every request"""
        return {
            "Authorization": f"Bearer {self._token}",
            "content-type": "application/json",
        }

    def request(
        self,
        path,
        method='GET',
        headers: dict = None,
        return_text=False,
        **kwargs
    ) -> Union[dict, list, str]:
        """Base method for making requests to the api"""
        if headers is None:
            headers = {}
        if isinstance(headers, dict):
            headers.update(self._headers)
        else:
            raise ValueError(f'headers must be dict or dict subclass, not type "{type(headers).__name__}"')
        try:
            resp = requests.request(
                method,
                self.endpoint(path),
                headers=headers,
                **kwargs,
                **self.global_request_kwargs
            )
        except requests.exceptions.TimeoutError:
            raise ResponseError(f'Homeassistant did not respond in time (timeout: {kwargs.get("timeout", 300)} sec)')    
        return self.response_logic(resp, return_text)

    def response_logic(self, response: requests.Response, return_text=False) -> Union[dict, list, str]:
        """Processes reponses from the api and formats them"""
        if return_text:
            return response.text
        try:
            return response.json()
        except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError):
            raise MalformedDataError(f'Homeassistant responded with non-json response: {repr(response.text)}')

    def construct_params(self, params: dict) -> str:
        """Custom method for constructing non-standard query strings"""
        return '&'.join([
            k if v is None
            else f"{k}={v}"
            for k, v in params.items()
        ])
