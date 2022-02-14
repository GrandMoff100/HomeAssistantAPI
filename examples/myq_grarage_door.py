import os

from homeassistant_api import Client

api_url = os.getenv("API_URL")
token = os.getenv("TOKEN")

if api_url is not None and token is not None:
    client = Client(api_url, token)

# Gets open garage service
open_garage = client.get_domains().cover.open_garage

# Triggers the service with a specific garage door
open_garage.trigger(entity_id="cover.my_garage_door")
