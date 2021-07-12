from os.path import join as path
from .states import State


class Group:
    def __init__(self, group_id: str, client):
        self.client = client
        self.group_id = group_id
        self.entities = {}
    
    def _add_entity(self, entity_slug: str, state: State):
        self.entities.update(
            entity_slug=Entity(entity_slug, state, self)
        )

    def get_entity(self, entity_slug: str):
        return self.entities.get(entity_slug, None)


class Entity:
    def __init__(self, slug: str, state: State, group: Group):
        self.id = slug
        self.state = state
        self.group = group
    
    def get_state(self):
        return self.state
    
    def fetch_state(self):
        state_data = self.group.client.request(path(
            'states',
            self.group.group_id + '.' + self.id
        ))
        self.state = self.group.client._process_state_json(state_data)
        return self.get_state()
    
    def set_state(self, state: State):
        state_data = self.group.client.request(
            path(
                'states',
                self.group.group_id + '.' + self.id
            ),
            method='POST',
            json=state
        )
        self.state = self.group.client._process_state_json(state_data)
        return self.get_state()
    
        
