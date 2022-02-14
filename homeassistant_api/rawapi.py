"""Module for parent RawWrapper class"""

import os
from typing import Dict, Optional

from .errors import MalformedInputError


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
    def construct_params(params: dict) -> str:
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
