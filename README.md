# HomeassistantAPI
Python Wrapper for Homeassistant's [REST API](https://developers.home-assistant.io/docs/api/rest/)


Please ⭐️ the repo if you find this project useful or cool!

For contributing guidelines see towards the bottom.

## Installation
There are a variety of ways to install this wrapper.

### Using `pip` from [PYPI](https://pypi.org/project/homeassistant_api/)
```
$ pip install homeassistant_api
```

### Using Source from [GitHub](https://github.com/GrandMoff100/HomeassistantAPI)
```
$ git clone https://github.com/GrandMoff100/HomeassistantAPI
$ cd HomeassistantAPI
$ python setup.py install
```

## Setup
### Hardware
Before using this library, you need to have Homeassistant OS running on a device. 
Something like a Rasberry Pi or spare laptop. 

### Enable `api` integration on Homeassistant
This library requires that you enable the [`api` integration](https://www.home-assistant.io/integrations/api) on your Homeassistant if you are familiar with setting up integrations.

### Access Token
Then once you have done that you need to head over to your profile and set up a "Long Lived Access Token" for you feed to the script. A good guide on how to do that is [here](https://www.home-assistant.io/docs/authentication/#your-account-profile)

### Exposing Homeassistant to the Web
You may want to setup a DNS server like DuckDNS 
(a good youtube tutorial on how to do that [here](https://www.youtube.com/watch?v=AK5E2T5tWyM), 
or port forwarding your homeassistant (if you are feeling adventurous)
Both options will allow you to access your Homeassistant remotely. All you will have to change is telling your script where to find your api (a.k.a. the base api endpoint)

## Usage

Once you have setup the `api` integration and created a Long Lived Access Token, its time to feed these into the script. 

See [example.py](https://github.com/GrandMoff100/HomeAssistantAPI/blob/master/example.py)

```py
import os
from homeassistant_api import Client

# Tell the script where your homeassistant api server is, by typing it into the string in place of `<HOMEASSISTANT_API_ENDPOINT>`
url = '<HOMEASSISTANT_API_ENDPOINT>') # http://localhost:8123/api or https://myhomeassistant.duckdns.com:8123/api

# Copy and paste your long lived access token into the string in place of `<HOMEASSISTANT_TOKEN>`
token = '<HOMEASSISTANT_TOKEN>') # ey816najgfjassf...


client = Client(url, token)

servicedomains = client.get_services()

print(servicedomains)

# This assumes you have an actual light in your living room hooked up to homeassistant
servicedomains.light.services.turn_off.trigger(entity_id='light.living_room') # Sends a request to turn off the living room light

```

## Contributing

We welcome contributions very warmly.
If you have an idea or some code you want to add to the project please fork this repository, make you changes, and open a pull request. Most likely your changes wil get merged if your code passes flake8 without any errors, and adds some functionality to the project. 
We'd love to see your ideas and perspective!
