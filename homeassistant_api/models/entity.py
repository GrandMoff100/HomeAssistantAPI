"""Module for Entity and entity Group data models"""

from os.path import join
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

from pydantic import Field

from .base import BaseModel
from .history import History
from .states import State

if TYPE_CHECKING:
    from homeassistant_api import Client


class Group(BaseModel):
    """Represents the groups that entities belong to."""

    group_id: str
    client: "Client" = Field(exclude=True, repr=False)
    entities: Dict[str, "Entity"] = {}

    def add_entity(self, entity_slug: str, state: State) -> None:
        """Registers entities to this Group object"""
        self.entities[entity_slug] = Entity(
            slug=entity_slug,
            state=state,
            client=self,
        )

    def get_entity(self, entity_slug: str) -> Optional["Entity"]:
        """Returns Entity with the given name if it exists. Otherwise returns None"""
        return self.entities.get(entity_slug)

    def __getattr__(self, key: str):
        if key in self.entities:
            return self.get_entity(key)
        return super(object, self).__getattribute__(  # type: ignore[misc]  # pylint: disable=bad-super-call
            key
        )


class Entity(BaseModel):
    """Represents entities inside of homeassistant"""

    slug: str
    state: State
    group: Group

    def get_state(self) -> State:
        """Asks Home Assistant for the state of the entity and caches it locally"""
        state_data = self.group.client.request(join("states", self.entity_id))
        self.state = self.group.client.process_state_json(
            cast(Dict[str, Any], state_data)
        )
        return self.state

    def set_state(self, state: State) -> State:
        """
        Tells Home Assistant to set the given State object.
        (You can construct the state object yourself.)
        """
        state_data = self.group.client.request(
            join("states", self.group.group_id + "." + self.slug),
            method="POST",
            json=state,
        )
        self.state = self.group.client.process_state_json(
            cast(Dict[str, Any], state_data)
        )
        return self.state

    @property
    def entity_id(self):
        """Constructs the entity_id string from its group and slug"""
        return self.group.group_id + "." + self.slug

    def get_history(self, *args, **kwargs) -> History:
        """Gets the previous `State`'s of the `Entity`"""
        history = None
        for history in self.group.client.get_entity_histories(
            entities=(self,),
            *args,
            **kwargs,
        ):
            break
        return history
