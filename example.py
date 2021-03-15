import os
from homeassistant_api import Client


url = os.getenv('HOMEASSISTANT_API_ENDPOINT') # http://localhost:8123/api/
token = os.getenv('HOMEASSISTANT_TOKEN') # ey816najgfjassf...


client = Client(url, token)

servicedomains = client.get_services()

servicedomains.light.turn_off.trigger(entity_id='light.living_room')
