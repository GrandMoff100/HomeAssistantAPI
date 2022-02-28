"""File for Service and Domain data models"""
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from pydantic import Field

from .base import BaseModel
from .states import State

if TYPE_CHECKING:
    from homeassistant_api import Client


class Domain(BaseModel):
    """Model representing the domain that services belong to."""

    domain_id: str
    client: "Client" = Field(exclude=True, repr=False)
    services: Dict[str, "Service"] = {}

    def add_service(self, service_id: str, **data) -> None:
        """Registers services into a domain to be used or accessed"""
        self.services.update(
            {
                service_id: Service(
                    service_id=service_id,
                    domain=self,
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


class ServiceField(BaseModel):
    """Model for service parameters/fields."""

    description: str
    example: Any
    selector: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    required: Optional[bool] = None


class Service(BaseModel):
    """Model representing services from homeassistant"""

    service_id: str
    domain: Domain
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[Dict[str, ServiceField]] = None
    target: Optional[Dict[str, dict]] = None

    def trigger(self, **service_data) -> Tuple[State, ...]:
        """Triggers the service associated with this object."""
        return self.domain.client.trigger_service(
            self.domain.domain_id,
            self.service_id,
            **service_data,
        )

    def __call__(self, **service_data) -> Tuple[State, ...]:
        return self.trigger(**service_data)
