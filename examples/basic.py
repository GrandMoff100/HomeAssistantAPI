from homeassistant_api import Client


api_url = "https://larsen-hassio.duckdns.org:8123/api"  # Something like http://localhost:8123/api
token = os.getenv("HOMEASSISTANT_TOKEN")  # Used to aunthenticate yourself with homeassistant
# See the documentation on how to obtain a Long Lived Access Token


with Client(api_url, token) as client:  # Create Client objecty and check that its running.
    light = client.get_domain("light")

    # Tells homeassistant to trigger the turn_on service on the given entity_id
    light.turn_on(entity_id="light.front_room")
