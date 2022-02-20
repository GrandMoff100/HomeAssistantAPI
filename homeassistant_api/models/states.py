"""Module for the Entity State model."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class State(BaseModel):
    """A model representing a state of an entity."""

    entity_id: str
    state: str
    attributes: Dict[str, Any] = {}
    last_changed: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    context: Dict[str, str] = {}
