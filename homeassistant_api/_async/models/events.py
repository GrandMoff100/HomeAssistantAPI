"""Event Model File"""
from os.path import join as path
from ...models import Event


class AsyncEvent(Event):
    """
    Event class for Homeassistant Event Triggers

    For attribute information see the Data Science docs on Event models
    https://data.home-assistant.io/docs/events
    """

    def __repr__(self):
        return f'<AsyncEvent {self.event_type}>'

    async def fire(self, **event_data):
        data = await self.client.request(
            path(
                'events',
                self.event_type
            ),
            method='POST',
            json=event_data
        )
        return data.get('message', 'No message provided')
