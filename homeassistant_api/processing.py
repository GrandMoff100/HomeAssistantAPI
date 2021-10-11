import json
import simplejson
import requests
import dataclasses

from .errors import (
    MalformedDataError,
    UnrecognizedStatusCodeError
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
        pass

    def process(self):
        if self.response.status_code in (200, 201):
            pass
        elif self.response.status_code == 400:
            pass
        elif self.response.status_code == 401:
            pass
        elif self.response.status_code == 403:
            pass
        elif self.response.status_code == 404:
            pass
        else:
            raise UnrecognizedStatusCodeError(self.response.status_code)

