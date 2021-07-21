"""File for Service and Domain data models"""

from os.path import join as path
from typing import List

from ...models import Domain, Service
from .states import AsyncState


class AsyncDomain(Domain):
    """A class representing the domain that services belong to."""

    async def __new__(cls):
        return cls

    async def __init__(*args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<AsyncDomain {self.domain_id}>'

    def add_service(self, service_id: str, **data) -> None:
        """Registers services into a domain to be used or accessed"""
        self.services.update({
            service_id: AsyncService(service_id, self, **data)
        })

    def get_service(self, service_id: str):
        """Return a Service with the given service_id, returns None if no such service exists"""
        return self.services.get(service_id, None)


class AsyncService(Service):
    """Class representing services from homeassistant"""

    def __repr__(self):
        return f'<AsyncService {self.id} domain="{self.domain.domain_id}">'

    async def trigger(self, **service_data) -> List[AsyncState]:
        """Triggers the service associated with this object."""

        data = await self.domain.client.request(
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
