"""Event Model File"""

from typing import TYPE_CHECKING, Any, Dict, cast

from pydantic import Field

from .base import BaseModel

if TYPE_CHECKING:
    from homeassistant_api import Client


class Event(BaseModel):
    """
    Event class for Home Assistant Event Triggers

    For attribute information see the Data Science docs on Event models
    https://data.home-assistant.io/docs/events
    """

    event: str = Field(..., description="The event name/type.")
    listener_count: int = Field(
        ...,
        description="How many listeners are interesting in this event in Home Assistant.",
    )
    _client: "Client" = Field(
        exclude=True,
        repr=False,
        description="The client object to fire events with. (Assigned automatically.)",
    )

    def fire(self, **event_data) -> str:
        """Fires the corresponding event in Home Assistant."""
        data = self._client.fire_event(self.event, **event_data)
        return cast(Dict[str, str], data).get("message", "No message provided")

    async def async_fire(self, **event_data) -> str:
        """Fires the event type in homeassistant. Ex. `on_startup`"""
        data = await self._client.async_fire_event(self.event, **event_data)
        return cast(Dict[str, str], data).get("message", "No message provided")

    @classmethod
    def from_json(cls, json: Dict[str, Any], client: "Client") -> "Event":
        """Constructs Event model from json data"""
        return cls(**json, _client=client)
