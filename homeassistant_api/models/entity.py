"""Module for Entity and entity Group data models"""

from os.path import join as path
from .states import State
from .base import JsonModel


class Group:
    """Represents the groups that entities belong to"""

    def __init__(self, group_id: str, client) -> None:
        """Initializes object with needed attributes"""
        self.client = client
        self.group_id = group_id
        self.entities = JsonModel()

    def __repr__(self):
        """Returns a readable string identifying each entity group."""
        return f'<Group {self.group_id}>'

    def add_entity(self, entity_slug: str, state: State) -> None:
        """Registers entities to this Group object"""
        self.entities.update({
            entity_slug: Entity(entity_slug, state, self)
        })

    def get_entity(self, entity_slug: str):
        """Returns Entity with the given name if it exists. Otherwise returns None"""
        return self.entities.get(entity_slug, None)


class Entity:
    """Represents entities inside of homeassistant"""

    def __init__(self, slug: str, state: State, group: Group) -> None:
        """Initializes object with needed attributes"""
        self.id = slug
        self.state = state
        self.group = group

    def __repr__(self) -> str:
        """Returns a readable string indentifying each Entity"""
        return f'<Entity entity_id="{self.entity_id}" state="{self.state.state}">'

    def get_state(self) -> State:
        """Returns the state last fetched from the api."""
        # TODO: add caching
        return self.state

    def fetch_state(self) -> State:
        """Asks homeassistant for the state of the entity and sets it locally"""
        state_data = self.group.client.request(path(
            'states',
            self.entity_id
        ))
        self.state = self.group.client.process_state_json(state_data)
        return self.state

    def set_state(self, state: State) -> State:
        """Tells homeassistant to set the given State object (you can construct the state object yourself)"""
        state_data = self.group.client.request(
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
