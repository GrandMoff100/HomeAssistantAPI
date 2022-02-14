"""Module for processing JSON data from homeassistant."""
from typing import cast

from ._async.models import AsyncDomain, AsyncEvent
from .models import Domain, Event, State


class JsonProcessingMixin:
    """Converts different JSON model types from homeassistant."""

    def process_services_json(self, json: dict) -> Domain:
        """Constructs Domain and Service models from json data"""
        domain = Domain(cast(str, json.get("domain")), self)
        services = json.get("services")
        if services is None:
            raise ValueError("Missing services atrribute in passed json argument.")
        for service_id, data in services.items():
            domain.add_service(service_id, **data)
        return domain

    @staticmethod
    def process_state_json(json: dict) -> State:
        """Constructs State model from json data"""
        return State(**json)

    def process_event_json(self, json: dict) -> Event:
        """Constructs Event model from json data"""
        return Event(**json, client=self)

    async def async_process_services_json(self, json: dict) -> AsyncDomain:
        """Constructs Domain and Service models from json data"""
        domain = AsyncDomain(cast(str, json.get("domain")), self)
        services = json.get("services")
        if services is None:
            raise ValueError("Missing services atrribute in passed json argument.")
        for service_id, data in services.items():
            domain.add_service(service_id, **data)
        return domain

    @staticmethod
    async def async_process_state_json(json: dict) -> State:
        """Constructs State model from json data"""
        return State(**json)

    async def async_process_event_json(self, json: dict) -> AsyncEvent:
        """Constructs Event model from json data"""
        return AsyncEvent(**json, client=self)
