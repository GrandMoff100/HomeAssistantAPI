"""Event Model File"""
from typing import TYPE_CHECKING, Dict, cast

from pydantic import Field

from ...models import BaseModel

if TYPE_CHECKING:
    from homeassistant_api import Client


class AsyncEvent(BaseModel):
    """
    Event class for Home Assistant Event Triggers

    For attribute information see the Data Science docs on Event models.
    https://data.home-assistant.io/docs/events
    """

    event_type: str
    listener_count: int
    client: "Client" = Field(exclude=True, repr=False)

    async def async_fire(self, **event_data) -> str:
        """Fires the event type in homeassistant. Ex. `on_startup`"""
        data = await self.client.async_fire_event(self.event_type, **event_data)
        return cast(Dict[str, str], data).get("message", "No message provided")
