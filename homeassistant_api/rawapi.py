import os
import json
import simplejson
import requests

from .errors import HTTPError


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

    def request(self, path, method='GET', headers={}, **kwargs):
        req = getattr(requests, method.lower())

        url = self.endpoint(path)
        headers.update(self._headers)

        resp = req(
            url,
            headers=headers,
            **kwargs
        )

        try:
            res = resp.json()
        except (json.decoder.JSONDecodeError, simplejson.decoder.JSONDecodeError):
            try:
                code, msg = resp.text.split(': ')
            except ValueError:
                return resp.text
            else:
                try:
                    int(code)
                except ValueError:
                    return resp.text
                else:
                    err_msg = ': '.join([code, url, msg, f'with method "{method.upper()}"'])
                    raise HTTPError(err_msg)
        else:
            return res
    
    def construct_params(self, params: dict):
        return '&'.join([
            k if v is None 
            else f"{k}={v}" 
            for k, v in params.items()
        ])
