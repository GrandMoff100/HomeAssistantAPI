import os

from homeassistant_api import Client

client = Client(
    "https://larsen-hassio.duckdns.org:8123/api",
    os.environ["HOMEASSISTANT_TOKEN"],
)


entries = client.logbook_entries()

for entry in entries:
    print(entry.entity_id)
