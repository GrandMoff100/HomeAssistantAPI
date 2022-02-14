"""Module for Entity and entity Group data models"""
from os.path import join

from ...models import Entity, Group, State


class AsyncGroup(Group):
    """Represents the groups that entities belong to"""

    def __repr__(self):
        return f"<AsyncGroup {self.group_id}>"

    def add_entity(self, entity_slug: str, state: State) -> None:
        """Registers entities to this Group object"""
        self.entities.update({entity_slug: AsyncEntity(entity_slug, state, self)})

    def get_entity(self, entity_slug: str):
        """Returns Entity with the given name if it exists. Otherwise returns None"""
        return self.entities.get(entity_slug, None)


class AsyncEntity(Entity):
    """Represents entities inside of homeassistant"""

    def __repr__(self) -> str:
        """Returns a readable string indentifying each Entity"""
        return f'<AsyncEntity entity_id="{self.entity_id}" state="{self.state.state}">'

    async def async_get_state(self) -> State:
        """Returns the state last fetched from the api."""
        return self.state

    async def async_fetch_state(self) -> State:
        """Asks homeassistant for the state of the entity and sets it locally"""
        state_data = self.group.client.async_request(join("states", self.entity_id))
        self.state = self.group.client.process_state_json(state_data)
        return self.state

    async def async_set_state(self, state: State) -> State:
        """Tells homeassistant to set the given State object."""
        return await self.group.client.async_set_state(
            self.entity_id,
            group=self.group.group_id,
            slug=self.id,
            **state,
        )

    @property
    def entity_id(self):
        """Constructs the entity_id string from its group and slug"""
        return self.group.group_id + "." + self.id
