from setuptools import setup
from homeassistant_api import __version__

with open("README.md", "r") as f:
    read = f.read()

setup(
    name="HomeAssistant API",
    url="https://github.com/GrandMoff100/HomeassistantAPI",
    description="Python Wrapper for Homeassistant's REST API",
    version=__version__,
    keywords=['homeassistant', 'api', 'wrapper', 'client'],
    author="GrandMoff100",
    author_email="nlarsen23.student@gmail.com",
    packages=[
        "homeassistant_api",
        "homeassistant_api.models",
        "homeassistant_api._async",
        "homeassistant_api._async.models"
    ],
    long_description=read,
    long_description_content_type="text/markdown",
    install_requires=["requests", "simplejson"],
    extras_require={
        "async": ["aiohttp"]
    },
    python_requires=">=3.6",
    provides=["homeassistant_api"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git"
    ]
)
