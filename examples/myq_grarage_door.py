import os

from homeassistant_api import Client

client = Client(os.getenv("API_URL"), os.getenv("TOKEN"))

# Gets open garage service
open_garage = client.get_domains().cover.open_garage

# Triggers the service with a specific garage door
open_garage.trigger(entity_id="cover.my_garage_door")
