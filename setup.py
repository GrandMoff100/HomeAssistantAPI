from setuptools import setup

with open('README.md', 'r') as f:
    read = f.read()


setup(
    name="HomeAssistant API",
    description="Python Wrapper for Homeassistant's REST API",
    version='2.0.0a1',
    packages=[
        'homeassistant_api',
        'homeassistant_api.models'
    ],
    install_requires=['requests'],
    long_description=read,
    long_description_content_type='text/markdown'
)