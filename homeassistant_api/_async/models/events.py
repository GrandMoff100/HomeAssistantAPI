"""Event Model File"""
from typing import Dict, cast

from ...models import Event


class AsyncEvent(Event):
    """
    Event class for Homeassistant Event Triggers

    For attribute information see the Data Science docs on Event models.
    https://data.home-assistant.io/docs/events
    """

    def __repr__(self):
        return f"<AsyncEvent {self.event_type}>"

    async def async_fire(self, **event_data) -> str:
        """Fires the event type in homeassistant. Ex. `on_startup`"""
        data = await self.client.async_fire_event(self.event_type, **event_data)
        return cast(Dict[str, str], data).get("message", "No message provided")
