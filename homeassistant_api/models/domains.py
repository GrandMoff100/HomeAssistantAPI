"""File for Service and Domain data models"""
import gc
import inspect
from typing import TYPE_CHECKING, Any, Coroutine, Dict, Optional, Tuple, Union, cast

from pydantic import Field

from .base import BaseModel
from .states import State

if TYPE_CHECKING:
    from homeassistant_api import Client


class Domain(BaseModel):
    """Model representing the domain that services belong to."""

    def __init__(self, *args, _client: Optional["Client"] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if _client is None:
            raise ValueError("No client passed.")
        object.__setattr__(self, "_client", _client)

    _client: "Client"
    domain_id: str = Field(
        ...,
        description="The name of the domain that services belong to. "
        "(e.g. :code:`frontend` in :code:`frontend.reload_themes`",
    )
    services: Dict[str, "Service"] = Field(
        {},
        description="A dictionary of all services belonging to the domain indexed by their names",
    )

    @classmethod
    def from_json(cls, json: Dict[str, Any], client: "Client") -> "Domain":
        """Constructs Domain and Service models from json data."""
        if "domain" not in json or "services" not in json:
            raise ValueError(
                "Missing services or attribute attribute in json argument."
            )
        domain = cls(domain_id=cast(str, json.get("domain")), _client=client)
        services = json.get("services")
        assert isinstance(services, dict)
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
        if attr in self.services:
            return self.get_service(attr)
        return super().__getattribute__(attr)


class ServiceField(BaseModel):
    """Model for service parameters/fields."""

    description: Optional[str] = None
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
        assert (parent_frame := frame.f_back) is not None
        try:
            if inspect.iscoroutinefunction(
                caller := gc.get_referrers(parent_frame.f_code)[0]
            ) or inspect.iscoroutine(caller):
                return self.async_trigger(**service_data)
        except IndexError:  # pragma: no cover
            pass
        return self.trigger(**service_data)
