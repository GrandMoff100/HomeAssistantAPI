"""Module for the Entity State model."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from .base import BaseModel


class State(BaseModel):
    """A model representing a state of an entity."""

    entity_id: str = Field(..., description="")
    state: str
    attributes: Dict[str, Any] = {}
    last_changed: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    context: Dict[str, Optional[str]] = {}

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> "State":
        """Constructs State model from json data"""
        return cls.parse_obj(json)
