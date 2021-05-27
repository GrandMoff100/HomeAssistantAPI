import os
from homeassistant_api import Client


url = os.getenv('HOMEASSISTANT_API_ENDPOINT') # http://localhost:8123/api/
token = os.getenv('HOMEASSISTANT_TOKEN') # ey816najgfjassf...


client = Client(url, token) # Creates the object uses to interact with the api
# In init it checks to see if the api is running by sending a check request
# If successful it also validates that the configuration.yml on you rhomeasistant is formatted correctly

servicedomains = client.get_services()

servicedomains.light.services.turn_off.trigger(entity_id='light.living_room')
