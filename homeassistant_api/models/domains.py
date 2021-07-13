from os.path import join as path
from .base import JsonModel


class Domain:
    def __init__(self, domain: str, client):
        self.domain_id = domain
        self.client = client
        self.services = JsonModel()

    def __repr__(self):
        return f'<Domain {self.domain_id}>'

    def add_service(self, service_id: str, **data):
        self.services.update({
            service_id: Service(service_id, self, **data)
        })
        return self.services[service_id]

    def get_service(self, service_id: str):
        return self.services.get(service_id, None)

    def __getattr__(self, attr: str):
        if hasattr(self, attr):
            return super().__getattribute__(attr)
        if attr in self.services:
            return self.get_service(attr)
        return super().__getattribute__(attr)


class Service:
    def __init__(
        self,
        service_id: str,
        domain: Domain,
        name: str = None,
        description: str = None,
        fields: dict = None,
        target: dict = None
    ):
        self.id = service_id
        self.domain = domain
        self.name = name
        self.description = description
        self.fields = fields
        self.target = target

    def __repr__(self):
        return f'<Service {self.id} domain="{self.domain.domain_id}">'

    def trigger(self, **service_data):
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
            self.domain.client.process_state_json(state_data)
            for state_data in data
        ]
