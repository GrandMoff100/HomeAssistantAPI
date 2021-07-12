from .base import JsonModel
from ..errors import ParameterMissingError

class State(JsonModel):
    def __init__(self, json: dict = None, **data):
        super().__init__(json, **data)
        if 'entity_id' not in self:
            raise ParameterMissingError('"entity_id" attribute not passed and is a required parameter')
        if 'state' not in self:
            raise ParameterMissingError('"state" attribute not passed and is a required parameter')

        self.update(
            attributes=self.get('attributes', {}),
            last_changed=self.get('last_changed', None),
            last_updated=self.get('last_updated', None)
        )
        
