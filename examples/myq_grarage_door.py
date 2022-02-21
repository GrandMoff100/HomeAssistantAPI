import os

from homeassistant_api import Client

api_url = os.getenv("API_URL")
token = os.getenv("TOKEN")


if api_url is not None and token is not None:
    # Intitializes the main Client
    client = Client(api_url, token)
    # Verifies the extistence of the specified server and opens efficient ClientSessions.
    with client:
        # Gets the cover service domain
        light = client.get_domain("light")
        # Triggers the service with a specific garage door
        print(light.toggle(entity_id="light.light_bulb_1"))
