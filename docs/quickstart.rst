Quickstart
***********

Prerequisites
==============

Homeassistant
-----------
Before using this library, you need to have Homeassistant OS running on a device. Something like a Rasberry Pi or spare laptop.
If you don't want to do that you can Homeassistant container on your laptop or desktop with docker.
See `here <https://www.home-assistant.io/installation/>`_ for how to install the installation right for you.



Configuring the API in Homeassistant
======================================

Enable the :code:`api` integration on Homeassistant
------------------------------------------------------
This library requires that you enable the :code:`api` integration on your Homeassistant if you are familiar with setting up integrations.
The :code:`api` integration is also enabled when you enabled the :code:`default_config` integration.


Access Token
--------------
Then once you have done that you need to head over to your profile and set up a "Long Lived Access Token" for you feed to the script. 
A good guide on how to do that is `here <https://www.home-assistant.io/docs/authentication/#your-account-profile>`_

Exposing Homeassistant to the Web
--------------------------------------
You may want to setup remote access through a Dynamic DNS server like DuckDNS (a good youtube tutorial on how to do that `here <https://www.youtube.com/watch?v=AK5E2T5tWyM>`_, keep in mind you will need to portforward to set that up.
If you do pursue this your api url will be something like :code:`https://yourhomeassistant.duckdns.org:8123/api`.
Which is different than what it might have looked like before.
Which might have been something like :code:`http://homeassistant.local:8123/api` or :code:`http://localhost:8123/api`

Installation
==============

Installing with :code:`pip`
-----------------------------------

Installation with pip is really easy and will install the dependencies this project needs.

.. code-block:: bash

   # To install the latest stable version from Pypi
   pip install homeassistant_api

   # To install the latest dev version
   pip install git+https://github.com/GrandMoff100/HomeassistantAPI/tree/dev

   # Example of installing a pre-release
   pip install homeassistant_api==2.0.0a1


Installating with :code:`git`
----------------------------------

To install with git we're going to clone the repository and then run setup.py like so.

.. code-block:: bash

   # Clone with git
   git clone https://github.com/GrandMoff100/HomeassistantAPI
   
   # Switch current working directory to the repository
   cd HomeassistantAPI

   # Run setup.py
   python setup.py install


Then you should be all set to start using the project! If run into any problems open an issue on our github :resource:`issue tracker <issues>`


Example Usages
==============
Some examples applications of this project include integrating it into a console executable, flask application or just a regular python script.
You can start a project that allows you to use this from the command line.
Or add it a discord bot to manage your homeassistant from inside discord (you might want to use AsyncClient if you do)
In any event, the possibilities are endless, so go make some cool stuff and share it with us!
