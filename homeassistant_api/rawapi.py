"""Module for parent RawWrapper class"""

import re
from datetime import datetime
from posixpath import join
from typing import Dict, Optional, Tuple, Union
from urllib.parse import quote as url_quote

from .const import DATE_FMT
from .models import Entity


class RawWrapper:
    """Builds, and makes requests to the API"""

    base_url: str
    token: str
    global_request_kwargs: Dict[str, str]

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        global_request_kwargs: Optional[Dict[str, str]] = None,
    ) -> None:
        if global_request_kwargs is None:
            global_request_kwargs = {}
        self.base_url = base_url
        self.token = token
        self.global_request_kwargs = global_request_kwargs

    @property
    def api_url(self) -> str:
        return join(self.base_url, "api/")

    @property
    def auth_url(self) -> str:
        return join(self.base_url, "auth/")
    

    def endpoint(self, path: str) -> str:
        """Joins the api base url with a local path to an absolute url"""
        return join(self.api_url, path)

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

    @staticmethod
    def format_entity_id(entity_id: str) -> str:
        """Takes in a string and formats it into valid snake_case."""
        entity_id = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", entity_id)
        entity_id = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", entity_id)
        entity_id = entity_id.replace("-", "_")
        return entity_id.lower()

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
        return self.format_entity_id(entity_id)

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
            params["end_time"] = url_quote(end_timestamp.strftime(DATE_FMT))
        if minimal_state_data:
            params["minimal_response"] = None
        if significant_changes_only:
            params["significant_changes_only"] = None
        if start_timestamp is not None:
            if isinstance(start_timestamp, datetime):
                formatted_timestamp = start_timestamp.strftime(DATE_FMT)
                url = join("history/period/", formatted_timestamp)
            else:
                raise TypeError(f"timestamp needs to be of type {datetime!r}")
        else:
            url = "history/period"
        return params, url

    @staticmethod
    def prepare_get_logbook_entry_params(
        filter_entity: Optional[Entity] = None,
        start_timestamp: Optional[
            Union[str, datetime]
        ] = None,  # Defaults to 1 day before
        end_timestamp: Optional[Union[str, datetime]] = None,
    ) -> Tuple[Dict[str, str], str]:
        """Prepares the query string and url path for retrieving logbook entries."""
        params: Dict[str, str] = {}
        if filter_entity is not None:
            params.update(entity=filter_entity.entity_id)
        if end_timestamp is not None:
            if isinstance(end_timestamp, datetime):
                end_timestamp = url_quote(end_timestamp.strftime(DATE_FMT))
            params.update(end_time=end_timestamp)
        if start_timestamp is not None:
            if isinstance(start_timestamp, datetime):
                url = join("logbook/", start_timestamp.strftime(DATE_FMT))
        else:
            url = "logbook"
        return params, url
