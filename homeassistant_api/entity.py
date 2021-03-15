class Entity:
    def __init__(self, id, group='group'):
        self.id = id
        self.group = group
        self._client = None
    
    @property
    def entity_id(self):
        return '.'.join([self.group, self.id])
    
    def get_state(self):
        return self._client.get_entity(self.entity_id)

    