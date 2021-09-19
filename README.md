# HomeassistantAPI

![Lines of code](https://img.shields.io/tokei/lines/github/GrandMoff100/HomeassistantAPI?style=for-the-badge)
![PyPI - Downloads](https://img.shields.io/pypi/dm/HomeAssistant-API?style=for-the-badge)
![GitHub commits since latest release (by date including pre-releases)](https://img.shields.io/github/commits-since/GrandMoff100/HomeassistantAPI/latest/master?include_prereleases&style=for-the-badge)
![Read the Docs (version)](https://img.shields.io/readthedocs/homeassistantapi/stable?style=for-the-badge)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/GrandMoff100/HomeassistantAPI?style=for-the-badge)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/GrandMoff100/HomeassistantAPI/latest/total?style=for-the-badge)

![Homeassistant Logo](/docs/images/homeassistant-logo.png)

Python Wrapper for Homeassistant's [REST API](https://developers.home-assistant.io/docs/api/rest/)


Please ⭐️ the repo if you find this project useful or cool!

For contributing guidelines see towards the bottom.

```py
from homeassistant_api import Client

client = Client(
    '<API URL>',
    '<Long Lived Access Token>'
)

client.get_domains().cover.open_garage(entity_id='cover.my_garage_door')
```

# Documentation
All documentation, api reference, Contribution guidelines and pretty much everything else you'd want to know is on our readthedocs site [here](https://homeassistantapi.rtfd.io)

If theres something missing open an issue and let us know! Thanks!
