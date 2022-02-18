"""Module for the Entity State model."""
from typing import Any, Dict, Optional

from pydantic import BaseModel


class State(BaseModel):
    """A model representing a state of an entity."""

    entity_id: str
    state: str
    attributes: Dict[str, Any] = {}
    last_changed: Optional[str] = None
    last_updated: Optional[str] = None
    context: Dict[str, str] = {}
