"""Module for parent RawWrapper class"""

import os
from datetime import datetime
from typing import Dict, Optional, Tuple

from .const import DATE_FMT
from .errors import MalformedInputError
from .models import Entity


class RawWrapper:
    """Builds, and makes requests to the API"""

    api_url: str
    token: str
    global_request_kwargs: Dict[str, str]

    def __init__(
        self,
        api_url: str,
        token: str,
        global_request_kwargs: Optional[Dict[str, str]] = None,
    ) -> None:
        self.api_url = api_url
        self.token = token
        if global_request_kwargs is None:
            global_request_kwargs = {}
        self.global_request_kwargs = global_request_kwargs
        if not self.api_url.endswith("/"):
            self.api_url += "/"

    def endpoint(self, path: str) -> str:
        """Joins the api base url with a local path to an absolute url"""
        return os.path.join(self.api_url, path)

    @property
    def _headers(self) -> Dict[str, str]:
        """Constructs the headers to send to the api for every request"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def prepare_headers(
        self,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Prepares and verifies dictionary headers."""
        if headers is None:
            headers = {}
        if isinstance(headers, dict):
            headers.update(self._headers)
        else:
            raise ValueError(
                f"headers must be dict or dict subclass, not type {type(headers).__name__!r}"
            )
        return headers

    @staticmethod
    def construct_params(params: Dict[str, Optional[str]]) -> str:
        """Custom method for constructing non-standard query strings"""
        return "&".join([k if v is None else f"{k}={v}" for k, v in params.items()])

    @classmethod
    def malformed_id(cls, entity_id: str) -> bool:
        """Checks whether or not a given entity_id is formatted correctly"""
        checks = [
            " " in entity_id,
            "." not in entity_id,
            "-" in entity_id,
            entity_id.lower() == entity_id,
        ]
        return True in checks

    def prepare_entity_id(
        self,
        *,
        group: Optional[str] = None,
        slug: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> str:
        """Combines optional `group` and `slug` into `entity_id` only if provided."""
        if (group is None or slug is None) and entity_id is None:
            raise ValueError(
                "To use group or slug you need to pass both not just one. "
                "Make sure you are using keyword arguments."
            )
        if group is not None and slug is not None:
            entity_id = group + "." + slug
        elif entity_id is None:
            raise ValueError("Neither group and slug or entity_id provided.")
        if self.malformed_id(entity_id):
            raise MalformedInputError(f"The entity_id, {entity_id!r}, is malformed")
        return entity_id

    @staticmethod
    def prepare_get_entity_histories_params(
        entities: Optional[Tuple[Entity, ...]] = None,
        start_timestamp: Optional[datetime] = None,
        # Defaults to 1 day before. https://developers.home-assistant.io/docs/api/rest/
        end_timestamp: Optional[datetime] = None,
        minimal_state_data: bool = False,
        significant_changes_only: bool = False,
    ) -> Tuple[Dict[str, Optional[str]], str]:

        """Pre-logic for `Client.get_entity_histories` and `Client.async_get_entity_histories`."""
        params: Dict[str, Optional[str]] = {}
        if entities is not None:
            params["filter_entity_id"] = ",".join([ent.entity_id for ent in entities])
        if end_timestamp is not None:
            params["end_time"] = end_timestamp.strftime(DATE_FMT)
        if minimal_state_data:
            params["minimal_response"] = None
        if significant_changes_only:
            params["significant_changes_only"] = None
        if start_timestamp is not None:
            if isinstance(start_timestamp, datetime):
                formatted_timestamp = start_timestamp.strftime(DATE_FMT)
                url = os.path.join("history/period", formatted_timestamp)
            else:
                raise TypeError(f"timestamp needs to be of type {datetime!r}")
        else:
            url = "history/period"
        return params, url
