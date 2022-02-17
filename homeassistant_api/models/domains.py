"""File for Service and Domain data models"""

from dataclasses import dataclass
from os.path import join as path
from typing import List, Optional

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
        """Returns readable string identifying each Domain class"""
        return f"<Domain {self.domain_id}>"

    def add_service(self, service_id: str, **data) -> None:
        """Registers services into a domain to be used or accessed"""
        self.services.update({service_id: Service(service_id, self, **data)})

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


@dataclass()
class Service:
    """Class representing services from homeassistant"""

    service_id: str
    domain: Domain
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[dict] = None
    target: Optional[dict] = None

    def __repr__(self):
        """Returns a readable string identifying each Service"""
        return f'<Service {self.service_id} domain="{self.domain.domain_id}">'

    def trigger(self, **service_data) -> List[State]:
        """Triggers the service associated with this object."""

        data = self.domain.client.request(
            path("services", self.domain.domain_id, self.service_id),
            method="POST",
            json=service_data,
        )
        return [
            self.domain.client.process_state_json(state_data) for state_data in data
        ]

    def __call__(self, **service_data):
        return self.trigger(**service_data)
