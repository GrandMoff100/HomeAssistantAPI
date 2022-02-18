from typing import Tuple

from pydantic import BaseModel

from .states import State


class History(BaseModel):
    changes: Tuple[State, ...]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.entity_id is not None

    @property
    def entity_id(self) -> str:
        entity_ids = [state.entity_id for state in self.changes]
        result, *others = set(entity_ids)
        assert len(others) == 0
        return result
