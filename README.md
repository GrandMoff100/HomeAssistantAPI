# HomeassistantAPI
[![Documentation Status](https://readthedocs.org/projects/homeassistantapi/badge/?version=latest)](https://homeassistantapi.readthedocs.io/en/latest/?badge=latest)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![Lines of code](https://img.shields.io/tokei/lines/github/GrandMoff100/HomeassistantAPI)
![PyPI - Downloads](https://img.shields.io/pypi/dm/homeassistant_api)
![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/GrandMoff100/HomeassistantAPI/latest)

![GitHub release (latest by date)](https://img.shields.io/github/v/release/GrandMoff100/HomeassistantAPI?style=for-the-badge)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/GrandMoff100/HomeassistantAPI/latest/total?style=for-the-badge)

![GitHub Contributors Image](https://contrib.rocks/image?repo=GrandMoff100/HomeassistantAPI)

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