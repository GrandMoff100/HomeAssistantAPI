from os.path import join as path


class Domain:
    def __init__(self, id: str, client):
        self.domain_id = id
        self.client = client
        self.services = {}
    
    def _add_service(self, service_id: str):
        self.services.update(
            service_id=Service(service_id)
        )
        return self.services[service_id]
    
    def get_service(self, service_id: str):
        return self.services.get(service_id, None)

    def __getattribute__(self, attr: str):
        if attr in self.services:
            return self.get_service(attr)
        return super().__getattribute__(attr)


class Service:
    def __init__(self, service_id: str, domain: Domain):
        self.id = service_id
        self.domain = domain
    
    def trigger(self, entity_id: str, **service_data):
        service_data.update(entity_id=entity_id)
        data = self.domain.client.request(
            path(
                'services',
                self.domain.domain_id,
                self.id
            ),
            method='POST',
            json=service_data
        )
        return [
            self.domain.client._process_state_json(state_data)
            for stata_data in data
        ]
            


