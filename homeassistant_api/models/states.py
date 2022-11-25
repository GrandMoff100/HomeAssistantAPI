"""Module for the Entity State model."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from .base import BaseModel


class Context(BaseModel):
    """Model for entity state contexts."""

    id: str = Field(
        max_length=128,
        description="Unique string identifying the context.",
    )


class State(BaseModel):
    """A model representing a state of an entity."""

    entity_id: str = Field(..., description="The entity_id this state corresponds to.")
    state: str = Field(
        ..., description="The string representation of the state of the entity."
    )
    attributes: Dict[str, Any] = Field(
        {}, description="A dictionary of extra attributes of the state."
    )
    last_changed: datetime = Field(
        default_factory=datetime.utcnow,
        description="The last time the state was changed.",
    )
    last_updated: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="The last time the state updated."
    )
    context: Optional[Context] = Field(
        None, description="Provides information about the context of the state."
    )

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> "State":
        """Constructs State model from json data"""
        return cls.parse_obj(json)
