import os
from homeassistant_api import Client


url = os.getenv('HOMEASSISTANT_API_ENDPOINT')  # http://localhost:8123/api/
token = os.getenv('HOMEASSISTANT_API_TOKEN')  # ey816najgfjassf...


client = Client(url, token)  # Creates the object uses to interact with the api
# In init it checks to see if the api is running by sending a check request
# If successful it also validates that the configuration.yml on your homeasistant is formatted correctly


# Service Examples
domains = client.get_domains()
print(domains)

service = domains.cover.services.open_cover # Works the same as domains['cover'].services['open_cover']
print(service)

changed_states = client.trigger_service('cover', 'open_cover', entity_id='cover.garage_door')
# Alternatively (using fetched service from above)
changed_states = service.trigger(entity_id='cover.garage_door')
print(changed_states)


# Entity Examples


# State Examples
states = client.get_states()
# [<EntityState "above_horizon" entity_id="sun.sun">, <EntityState "zoning" entity_id="zone.home">,...]

state = client.get_state('sun.sun')
# <EntityState "above_horizon" entity_id="sun.sun">

new_state = client.set_state(state='my ToaTallY Whatever vAlUe 12t87932', group_id='my_favorite_colors', entity_slug='number_one')
# <EntityState "my ToaTallY Whatever vAlUe 12t87932" entity_id="my_favorite_colors.number_one">


# Event Examples

