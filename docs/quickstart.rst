.. _quickstart:

***********
Quickstart
***********

Prerequisites
==============

Homeassistant
---------------
Before using this library, you need to have Homeassistant OS or Home Assistant Core running on a device (i.e. Rasberry Pi, Spare Laptop, etc.), Docker container, or `Home Assistant development environment`.
See `here <https://www.home-assistant.io/installation/>`__ for how to install the installation right for you.

Configuring the REST API Server in Homeassistant
======================================

Enable the :code:`api` integration in Homeassistant
------------------------------------------------------
This library requires that the :code:`api` integration on your Homeassistant is enabled.
It is enabled by default with the :code:`default_config` integration.
But if by chance you have disabled :code:`default_config` you need to enable :code:`api`.
Which requires the :code:`http` integration as well.
(Again most likely alreayd enabled on most installations.)
If you are not sure if it is enabled or not, chances are if your frontend is enabled, so is your API Server.

Access Token
--------------
Then once you have done that you need to head over to your profile and set up a "Long Lived Access Token" to input to your script later.
A good guide on how to do that is `here <https://www.home-assistant.io/docs/authentication/#your-account-profile>`__

Exposing Homeassistant to the Web
--------------------------------------
You may want to setup remote access through a Dynamic DNS server like DuckDNS (a good youtube tutorial on how to do that `here <https://www.youtube.com/watch?v=AK5E2T5tWyM>`_, keep in mind you will need to port forward to set that up.)
If you do pursue this your api url will be something like :code:`https://yourhomeassistant.duckdns.org:8123/api`.
Which is different than what it could have looked like before.
Which might have been something like :code:`http://homeassistant.local:8123/api` or :code:`http://localhost:8123/api`

Installation
==============

Installing with :code:`pip`
-----------------------------------

Installation with pip is really easy and will install the dependencies this project needs.

.. code-block:: bash

   # To install the latest stable version from Pypi
   $ pip install homeassistant_api

   # To install the latest dev version
   $ pip install git+https://github.com/GrandMoff100/HomeassistantAPI

   # Example of installing a pre-release
   $ pip install homeassistant_api==2.0.0a1


Installating with :code:`git`
----------------------------------

To install with git we're going to clone the repository and then run :code:`$ poetry install` like so.

.. code-block:: bash

   # Clone with git
   git clone https://github.com/GrandMoff100/HomeassistantAPI

   # CD into your project
   cd <path/to/my/awesome/homeassistant/project>

   # Install poetry
   python -m pip install poetry

   # Run poetry install
   python -m poetry install ~/HomeAssistantAPI


Then you should be all set to start using the project! If run into any problems open an issue on our github :resource:`issue tracker <issues>`


Example Usages
================
Some examples applications of this project include integrating it into a another library, flask application or just a regular python script.
Maybe you want to start a project that allows you to use your homeassistant from your command line but some sassy responses.
Or maybe add it to a discord bot to manage your homeassistant from inside discord (you might want to use AsyncClient if you do, *hint hint wink wink nudge nudge*)
In any event, the possibilities are endless, so go make some cool stuff and share it with us on the :resource:`repository <repo>`!
We hope to see your project soon!
