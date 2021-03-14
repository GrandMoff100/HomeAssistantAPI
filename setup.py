from setuptools import setup

with open('README.md', 'r') as f:
    read = f.read()


setup(
    name="HomeAssistant API",
    description="Python Wrapper for Homeassistant's REST API",
    version='0.0.0a',
    packages=['homeassistant_api'],
    install_requires=['requests'],
    long_description=read,
    long_description_content_type='text/markdown'
)