import os
import json
import simplejson
import requests

from .errors import MalformedDataError


class RawWrapper:
    def __init__(self, api_url, token):
        self.api_url = api_url
        if not self.api_url.endswith('/'):
            self.api_url += '/'
        self._token = token

    def endpoint(self, path):
        url = os.path.join(self.api_url, path)
        return url

    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {self._token}",
            "content-type": "application/json",
        }

    def request(self, path, method='GET', headers: dict = None, return_text_if_fail=False, **kwargs):
        if headers is None:
            headers = {}
        if isinstance(headers, dict):
            headers.update(self._headers)
        else:
            raise ValueError(f'headers must be dict or dict subclass, not type "{type(headers).__name__}"')

        resp = requests.request(
            method,
            self.endpoint(path),
            headers=headers,
            **kwargs
        )
        return self.response_logic(resp, return_text_if_fail)

    def response_logic(self, response, return_text_if_fail=False):
        try:
            res = response.json()
        except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError):
            if return_text_if_fail:
                return response.text
            else:
                raise MalformedDataError(f'Homeassistant responded with non-json response: {repr(response.text)}')
        else:
            return res

    def construct_params(self, params: dict):
        return '&'.join([
            k if v is None
            else f"{k}={v}"
            for k, v in params.items()
        ])
