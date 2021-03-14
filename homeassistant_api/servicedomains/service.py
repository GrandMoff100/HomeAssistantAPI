from ..models import JsonModel


class BaseService(JsonModel):
    def __init__(self, json):
        self.description = None
        self.fields = {}
        super().__init__(json)


class Service(BaseService):
    def __init__(self, group, service_id, json, client):
        super().__init__(json)
        self.client = client
        self.group = group
        self.service_id = service_id
        self.name = ' '.join([x.capitalize() for x in service_id.split('_')])

    def __str__(self):
        return self.name

    def trigger(self, **fields):
        res = self.client.request(f'services/{self.group}/{self.service_id}', method='POST', json=fields)
        entities = [self.client._process_entity_json(j) for j in res]
        return entities
