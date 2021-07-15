import os
from homeassistant_api import Client


url = os.getenv('HOMEASSISTANT_API_ENDPOINT')  # http://localhost:8123/api/
token = os.getenv('HOMEASSISTANT_API_TOKEN')  # ey816najgfjassf...


client = Client(url, token)  # Authenticates yourself with your api

# Service Examples
# domains = client.get_domains()
# {'homeassistant': <Domain homeassistant>, 'notify': <Domain notify>}

# service = domains.cover.services.close_cover # Works the same as domains['cover'].services['open_cover']
# <Service open_cover domain="cover">

# changed_states = client.trigger_service('cover', 'close_cover', entity_id='cover.garage_door')
# Alternatively (using fetched service from above)
# changed_states = service.trigger(entity_id='cover.garage_door')
# [<EntityState "closing" entity_id="cover.garage_door">]


# Entity Examples
# entity_groups = client.get_entities()
# {'person': <EntityGroup person>, 'zone': <EntityGroup zone>, ...}

# door = client.get_entity(entity_id='cover.garage_door')
# <Entity entity_id="cover.garage_door" state="<EntityState "closed">">

# State Examples
# states = client.get_states()
# [<EntityState "above_horizon" entity_id="sun.sun">, <EntityState "zoning" entity_id="zone.home">,...]

# state = client.get_state('sun.sun')
# <EntityState "above_horizon" entity_id="sun.sun">

# new_state = client.set_state(state='my ToaTallY Whatever vAlUe 12t87932', group_id='my_favorite_colors', entity_slug='number_one')
# <EntityState "my ToaTallY Whatever vAlUe 12t87932" entity_id="my_favorite_colors.number_one">

print(client.get_discovery_info())
