from homeassistant_api import Client

client = Client(
    "http://homeassistant.local:8123/api",
    "myfabulousapikey",
)

new_state = client.set_state(
    entity_id="sensor.some_variable", state="42 the answer to everything"
)

print(new_state)
