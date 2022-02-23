"""Module for the Logbook Entry model."""
from datetime import datetime
from typing import Optional

from .base import BaseModel


class LogbookEntry(BaseModel):
    """Model representing"""

    when: datetime
    name: str
    entity_id: str
    state: Optional[str] = None
    domain: Optional[str] = None
    context_id: Optional[str] = None
    icon: Optional[str] = None
