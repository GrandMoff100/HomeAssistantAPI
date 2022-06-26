"""Module for Entity and entity Group data models"""

from datetime import datetime
from posixpath import join
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from pydantic import Field

from .base import BaseModel
from .history import History
from .states import State

if TYPE_CHECKING:
    from homeassistant_api import Client


class Group(BaseModel):
    """Represents the groups that entities belong to."""

    group_id: str = Field(
        ...,
        description="A unique string identifying different types/groups of entities.",
    )
    _client: "Client" = Field(
        exclude=True,
        repr=False,
        description="The client object to modify and retrieve entities with.",
    )
    entities: Dict[str, "Entity"] = Field(
        {},
        description="A dictionary of all entities belonging to the group "
        "indexed by their :code:`entity_id`.",
    )

    def add_entity(self, entity_slug: str, state: State) -> None:
        """Registers entities to this Group object"""
        self.entities[entity_slug] = Entity(
            slug=entity_slug,
            state=state,
            group=self,
        )

    def get_entity(self, entity_slug: str) -> Optional["Entity"]:
        """Returns Entity with the given name if it exists. Otherwise returns None"""
        return self.entities.get(entity_slug)

    def __getattr__(self, key: str):
        if key in self.entities:
            return self.get_entity(key)
        return super().__getattribute__(key)


class Entity(BaseModel):
    """Represents entities inside of homeassistant"""

    slug: str
    state: State
    group: Group = Field(exclude=True, repr=False)

    def get_state(self) -> State:
        """Asks Home Assistant for the state of the entity and caches it locally"""
        state_data = self.group.client.request(join("states", self.entity_id))
        self.state = State.from_json(cast(Dict[str, Any], state_data))
        return self.state

    def set_state(self, state: State) -> State:
        """
        Tells Home Assistant to set the given State object.
        (You can construct the state object yourself.)
        """
        state_data = self.group.client.request(
            join("states", f"{self.group.group_id}.{self.slug}"),
            method="POST",
            json=state,
        )
        self.state = State.from_json(cast(Dict[str, Any], state_data))
        return self.state

    @property
    def entity_id(self) -> str:
        """Constructs the :code:`entity_id` string from its group and slug"""
        return f"{self.group.group_id}.{self.slug}".strip()

    def get_history(
        self,
        start_timestamp: Optional[datetime] = None,
        # Defaults to 1 day before. https://developers.home-assistant.io/docs/api/rest/
        end_timestamp: Optional[datetime] = None,
        minimal_state_data: bool = False,
        significant_changes_only: bool = False,
    ) -> History:
        """Gets the previous :py:class:`State`'s of the :py:class:`Entity`"""
        history = None
        for history in self.group.client.get_entity_histories(
            entities=(self,),
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            minimal_state_data=minimal_state_data,
            significant_changes_only=significant_changes_only,
        ):
            break
        return history

    async def async_get_state(self) -> State:
        """Asks Home Assistant for the state of the entity and sets it locally"""
        state_data = await self.group.client.async_request(
            join("states", self.entity_id)
        )
        self.state = State.from_json(cast(Dict[str, Any], state_data))
        return self.state

    async def async_set_state(self, state: State) -> State:
        """Tells Home Assistant to set the given State object."""
        return await self.group.client.async_set_state(
            self.entity_id,
            group=self.group.group_id,
            slug=self.slug,
            **state.dict(),
        )

    async def async_get_history(
        self,
        start_timestamp: Optional[datetime] = None,
        # Defaults to 1 day before. https://developers.home-assistant.io/docs/api/rest/
        end_timestamp: Optional[datetime] = None,
        minimal_state_data: bool = False,
        significant_changes_only: bool = False,
    ) -> Optional[History]:
        """Gets the previous :py:class:`State`'s of the :py:class:`Entity`."""
        history: Optional[History] = None
        async for history in self.group.client.async_get_entity_histories(
            entities=(self,),
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            minimal_state_data=minimal_state_data,
            significant_changes_only=significant_changes_only,
        ):
            break
        return history
