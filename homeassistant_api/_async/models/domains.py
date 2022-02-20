"""File for Service and Domain data models"""

from typing import Any, Dict, Tuple, cast

from ...models import Domain, Service, State


class AsyncDomain(Domain):
    """A class representing the domain that services belong to."""

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


class AsyncService(Service):
    """Class representing services from homeassistant"""

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
