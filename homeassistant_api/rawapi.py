"""Module for parent RawWrapper class"""

import os
from typing import Dict, Union

import requests

from .errors import RequestError
from .processing import Processing


class RawWrapper:
    """Builds, and makes requests to the API"""

    global_request_kwargs: Dict[str, str] = {}

    def __init__(self, api_url: str, token: str) -> None:
        """Prepares and stores API URL and Love Lived Access Token token"""
        self.api_url = api_url
        if not self.api_url.endswith("/"):
            self.api_url += "/"
        self._token = token

    def endpoint(self, path: str) -> str:
        """Joins the api base url with a local path to an absolute url"""
        return os.path.join(self.api_url, path)

    @property
    def _headers(self) -> dict:
        """Constructs the headers to send to the api for every request"""
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def request(
        self,
        path,
        method="GET",
        headers: dict = None,
        **kwargs,
    ) -> Union[dict, list, str]:
        """Base method for making requests to the api"""
        if headers is None:
            headers = {}
        if isinstance(headers, dict):
            headers.update(self._headers)
        else:
            raise ValueError(
                f'headers must be dict or dict subclass, not type "{type(headers).__name__}"'
            )
        try:
            kwargs.update(self.global_request_kwargs)
            resp = requests.request(
                method,
                self.endpoint(path),
                headers=headers,
                **kwargs,
            )
        except requests.exceptions.Timeout:
            raise RequestError(
                f'Homeassistant did not respond in time (timeout: {kwargs.get("timeout", 300)} sec)'
            )
        return self.response_logic(resp)

    def response_logic(self, response: requests.Response) -> Union[dict, list, str]:
        """Processes reponses from the api and formats them"""
        processing = Processing(response)
        return processing.process()

    @staticmethod
    def construct_params(params: dict) -> str:
        """Custom method for constructing non-standard query strings"""
        return "&".join([k if v is None else f"{k}={v}" for k, v in params.items()])
