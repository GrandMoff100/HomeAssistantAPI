from homeassistant_api import Client


api_url = "<API URL>"  # Something like http://localhost:8123/api
token = "<Long Lived Access Token>"  # Used to aunthenticate yourself with homeassistant
# See the documentation on how to obtain a Long Lived Access Token


client = Client(api_url, token)  # Creates main object


light = client.get_domains().light  # gets the light domain from homeassistant


# Tells homeassistant to trigger the turn_on service on the given entity_id
light.turn_on.trigger(entity_id='light.front_room')
