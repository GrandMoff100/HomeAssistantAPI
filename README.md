# HomeassistantAPI
Python Wrapper for Homeassistant's REST API

## Installation
There are a variety of ways to install this wrapper.

### Using `pip` from [PYPI](https://pypi.org/project_homeassistant_api/)
```
$ pip install homeassistant_api
```

### Using Source from [GitHub](https://github.com/GrandMoff100/HomeassistantAPI)
```
$ git clone https://github.com/GrandMoff100/HomeassistantAPI
$ cd HomeassistantAPI
$ python setup.py install
```

## Usage
See [example.py](https://github.com/GrandMoff100/HomeAssistantAPI/blob/master/example.py)

```py
import os
from homeassistant_api import Client


url = os.getenv('HOMEASSISTANT_API_ENDPOINT') # http://localhost:8123/api/
token = os.getenv('HOMEASSISTANT_TOKEN') # ey816najgfjassf...


client = Client(url, token)

servicedomains = client.get_services()

servicedomains.light.turn_off.trigger(entity_id='light.living_room') # Sends a request to turn off the living room light
```
