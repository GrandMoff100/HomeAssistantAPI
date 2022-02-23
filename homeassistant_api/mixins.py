"""Module for processing JSON data from homeassistant."""
from typing import Any, Dict, cast

from ._async.models import AsyncDomain, AsyncEvent
from .models import Domain, Event, State


class JsonProcessingMixin:
    """Converts different JSON model types from homeassistant."""

    def process_services_json(self, json: Dict[str, Any]) -> Domain:
        """Constructs Domain and Service models from json data"""
        domain = Domain(domain_id=cast(str, json.get("domain")), client=self)
        services = json.get("services")
        if services is None:
            raise ValueError("Missing services attribute in passed json argument.")
        for service_id, data in services.items():
            domain.add_service(service_id, **data)
        return domain

    @staticmethod
    def process_state_json(json: Dict[str, Any]) -> State:
        """Constructs State model from json data"""
        return State.parse_obj(json)

    def process_event_json(self, json: Dict[str, Any]) -> Event:
        """Constructs Event model from json data"""
        return Event(**json, client=self)

    async def async_process_services_json(
        self,
        json: Dict[str, Any],
    ) -> AsyncDomain:
        """Constructs Domain and Service models from json data"""
        domain = AsyncDomain(domain_id=cast(str, json.get("domain")), client=self)
        services = json.get("services")
        if services is None:
            raise ValueError("Missing services atrribute in passed json argument.")
        for service_id, data in services.items():
            domain.add_service(service_id, **data)
        return domain

    @staticmethod
    async def async_process_state_json(json: Dict[str, Any]) -> State:
        """Constructs State model from json data"""
        return State.parse_obj(json)

    async def async_process_event_json(
        self,
        json: Dict[str, Any],
    ) -> AsyncEvent:
        """Constructs Event model from json data."""
        return AsyncEvent(**json, client=self)
