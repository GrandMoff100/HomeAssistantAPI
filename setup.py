from setuptools import setup
from homeassistant_api import __version__

with open('README.md', 'r') as f:
    read = f.read()

setup(
    name="HomeAssistant API",
    description="Python Wrapper for Homeassistant's REST API",
    version=__version__,
    packages=[
        'homeassistant_api',
        'homeassistant_api.models'
    ],
    install_requires=open('requirements.txt', 'r').read().splitlines(),
    long_description=read,
    long_description_content_type='text/markdown'
)
