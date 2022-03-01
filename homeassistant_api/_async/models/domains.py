"""File for Service and Domain data models"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, cast

from pydantic import BaseModel, Field

from ...models import State
from ...models.domains import ServiceField

if TYPE_CHECKING:
    from homeassistant_api import Client


class AsyncDomain(BaseModel):
    """A class representing the domain that services belong to."""

    domain_id: str
    client: "Client" = Field(exclude=True, repr=False)
    services: Dict[str, "AsyncService"] = {}

    def add_service(self, service_id: str, **data) -> None:
        """Registers services into a domain to be used or accessed"""
        self.services.update(
            {
                service_id: AsyncService(
                    service_id=service_id,
                    client=self,
                    **data,
                )
            }
        )

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


class AsyncService(BaseModel):
    """Class representing services from homeassistant"""

    service_id: str
    domain: AsyncDomain
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[Dict[str, ServiceField]] = None
    target: Optional[Dict[str, dict]] = None

    async def async_trigger(self, **service_data) -> Tuple[State, ...]:
        """Triggers the service associated with this object."""
        data = await self.domain.client.async_trigger_service(
            self.domain.domain_id,
            self.service_id,
            **service_data,
        )
        states = map(
            self.domain.client.process_state_json,
            cast(Tuple[Dict[str, Any]], data),
        )
        return tuple(states)
