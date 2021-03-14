import os
from homeassistant_api import Client


url = os.getenv('HOMEASSISTANT_API_ENPOINT')
token = os.getenv('HOMEASSISTANT_TOKEN')


client = Client(url, token)

states = client.get_entity_group('script')

print(states)
