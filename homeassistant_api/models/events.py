"""Event Model File"""
from os.path import join as path


class Event:
    """
    Event class for Homeassistant Event Triggers

    For attribute information see the Data Science docs on Event models
    https://data.home-assistant.io/docs/events
    """

    def __init__(self, event: str, listener_count: int, client):
        self.event_type = event
        self.listener_count = listener_count
        self.client = client

    def __repr__(self):
        return f'<Event {self.event_type}>'

    def fire(self, **event_data):
        data = self.client.request(
            path(
                'events',
                self.event_type
            ),
            method='POST',
            json=event_data
        )
        return data.get('message', 'No message provided')
