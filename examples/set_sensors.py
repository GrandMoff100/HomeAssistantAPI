from homeassistant_api import Client

with Client(
    "http://homeassistant.local:8123/api",
    "myfabulousapikey",
) as client:
    new_state = client.set_state(
        entity_id="sensor.some_variable", state="42 the answer to everything"
    )
    print(new_state)
