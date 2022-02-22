"""Module for the History model."""
from typing import Tuple

from .base import BaseModel
from .states import State


class History(BaseModel):
    """Model representing past :code:`State`'s of an entity."""

    states: Tuple[State, ...]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.entity_id is not None

    @property
    def entity_id(self) -> str:
        """Returns the shared :code:`entity_id` of states."""
        entity_ids = [state.entity_id for state in self.states]
        result, *others = set(entity_ids)
        assert len(others) == 0
        return result
