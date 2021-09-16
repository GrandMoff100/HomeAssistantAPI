"""File for Service and Domain data models"""

from os.path import join as path
from typing import List

from .base import JsonModel
from .states import State


class Domain:
    """A class representing the domain that services belong to."""

    def __init__(self, domain: str, client) -> None:
        """Initializes needed attributes"""
        self.domain_id = domain
        self.client = client
        self.services = JsonModel()

    def __repr__(self) -> str:
        """Returns readable string indentifying each Domain class"""
        return f'<Domain {self.domain_id}>'

    def add_service(self, service_id: str, **data) -> None:
        """Registers services into a domain to be used or accessed"""
        self.services.update({
            service_id: Service(service_id, self, **data)
        })

    def get_service(self, service_id: str):
        """Return a Service with the given service_id, returns None if no such service exists"""
        return self.services.get(service_id, None)

    def __getattr__(self, attr: str):
        """Allows services accessible as attributes"""
        if attr in self.__dict__:
            return super().__getattribute__(attr)
        if attr in self.services:
            return self.get_service(attr)
        return super().__getattribute__(attr)


class Service:
    """Class representing services from homeassistant"""

    def __init__(
        self,
        service_id: str,
        domain: Domain,
        name: str = None,
        description: str = None,
        fields: dict = None,
        target: dict = None
    ) -> None:
        self.id = service_id
        self.domain = domain
        self.name = name
        self.description = description
        self.fields = fields
        self.target = target

    def __repr__(self):
        """Returns a readable string indentifying each Service"""
        return f'<Service {self.id} domain="{self.domain.domain_id}">'

    def trigger(self, **service_data) -> List[State]:
        """Triggers the service associated with this object."""

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
