"""File for Service and Domain data models"""
import gc
import inspect
from typing import TYPE_CHECKING, Any, Coroutine, Dict, Optional, Tuple, Union, cast

from pydantic import Field, validator

from .base import BaseModel
from .states import State

if TYPE_CHECKING:
    from homeassistant_api import Client


class Domain(BaseModel):
    """Model representing the domain that services belong to."""

    domain_id: str = Field(
        ...,
        description="The name of the domain that services belong to. "
        "(e.g. :code:`frontend` in :code:`frontend.reload_themes`",
    )
    _client: "Client"
    services: Dict[str, "Service"] = Field(
        {},
        description="A dictionary of all services belonging to the domain indexed by their names",
    )

    @classmethod
    def from_json(cls, json: Dict[str, Any], client: "Client") -> "Domain":
        """Constructs Domain and Service models from json data."""
        domain = cls(domain_id=cast(str, json.get("domain")), _client=client)
        services = json.get("services")
        if services is None:
            raise ValueError("Missing services attribute in passed json argument.")
        for service_id, data in services.items():
            domain._add_service(service_id, **data)
        return domain

    def _add_service(self, service_id: str, **data) -> None:
        """Registers services into a domain to be used or accessed. Used internally."""
        self.services.update(
            {
                service_id: Service(
                    service_id=service_id,
                    domain=self,
                    **data,
                )
            }
        )

    def get_service(self, service_id: str) -> Optional["Service"]:
        """Return a Service with the given service_id, returns None if no such service exists"""
        return self.services.get(service_id)

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
    domain: Domain = Field(exclude=True, repr=False)
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[Dict[str, ServiceField]] = None
    target: Optional[Dict[str, Dict[str, Any]]] = None

    @classmethod
    @validator("domain")
    def validate_domain(cls, domain: Domain) -> Domain:
        """
        Explicitly do nothing to validate the parent domain.
        Elimintates recursive validation errors.
        """
        return domain

    def trigger(self, **service_data) -> Tuple[State, ...]:
        """Triggers the service associated with this object."""
        return self.domain._client.trigger_service(
            self.domain.domain_id,
            self.service_id,
            **service_data,
        )

    async def async_trigger(self, **service_data) -> Tuple[State, ...]:
        """Triggers the service associated with this object."""
        return await self.domain._client.async_trigger_service(
            self.domain.domain_id,
            self.service_id,
            **service_data,
        )

    def __call__(
        self, **service_data
    ) -> Union[Tuple[State, ...], Coroutine[Any, Any, Tuple[State, ...]]]:
        """Triggers the service associated with this object."""
        assert (frame := inspect.currentframe()) is not None
        assert (caller := frame.f_back) is not None
        if inspect.iscoroutinefunction(gc.get_referrers(caller.f_code)[0]):
            return self.async_trigger(**service_data)
        return self.trigger(**service_data)
