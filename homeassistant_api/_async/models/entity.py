"""Module for Entity and entity Group data models"""

from os.path import join as path
from .states import AsyncState

from ...models import Group, Entity


class AsyncGroup(Group):
    """Represents the groups that entities belong to"""
    def __repr__(self):
        return f'<AsyncGroup {self.group_id}>'

    def add_entity(self, entity_slug: str, state: AsyncState) -> None:
        """Registers entities to this Group object"""
        self.entities.update({
            entity_slug: AsyncEntity(entity_slug, state, self)
        })

    def get_entity(self, entity_slug: str):
        """Returns Entity with the given name if it exists. Otherwise returns None"""
        return self.entities.get(entity_slug, None)


class AsyncEntity(Entity):
    """Represents entities inside of homeassistant"""

    def __repr__(self) -> str:
        """Returns a readable string indentifying each Entity"""
        return f'<AsyncEntity entity_id="{self.entity_id}" state="{self.state.state}">'

    async def get_state(self) -> AsyncState:
        """Returns the state last fetched from the api."""
        # TODO: add caching
        return self.state

    async def fetch_state(self) -> AsyncState:
        """Asks homeassistant for the state of the entity and sets it locally"""
        state_data = self.group.client.request(path(
            'states',
            self.entity_id
        ))
        self.state = self.group.client.process_state_json(state_data)
        return self.state

    async def set_state(self, state: AsyncState) -> AsyncState:
        """Tells homeassistant to set the given State object (you can construct the state object yourself)"""
        state_data = await self.group.client.request(
            path(
                'states',
                self.group.group_id + '.' + self.id
            ),
            method='POST',
            json=state
        )
        self.state = self.group.client.process_state_json(state_data)
        return self.state

    @property
    def entity_id(self):
        """Constructs the entity_id string from its group and slug"""
        return self.group.group_id + '.' + self.id
