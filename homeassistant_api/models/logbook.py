"""Module for the Logbook Entry model."""
from datetime import datetime
from typing import Optional

from .base import BaseModel


class LogbookEntry(BaseModel):
    """Model representing entries in the Logbook."""

    when: datetime
    name: str
    message: Optional[str] = None
    entity_id: Optional[str] = None
    state: Optional[str] = None
    domain: Optional[str] = None
    context_id: Optional[str] = None
    icon: Optional[str] = None
