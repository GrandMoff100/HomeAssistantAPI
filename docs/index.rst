.. Homeassistant API documentation master file, created by
   sphinx-quickstart on Wed Jul 14 00:58:24 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. image:: ./images/homeassistant-logo.png


Welcome to Homeassistant API!
=============================

Homeassistant API is pythonic way to interact with `Homeassistant's REST API integration <https://developers.home-assistant.io/docs/api/rest>`_

Features
----------

- Full consumption of the Homeassistant REST API endpoints
- Convenient classes that represent data from the API
- Asyncronous support for integration in async applications or libraries [COMING SOON]
- Modular design for intuitive readability

Getting Started
-------------------

Is this your first time using the library? This is the place to get started!

.. toctree::
   :maxdepth: 1

   Home <index>
   quickstart
   usage
   cookbook
   api


Example
---------

.. literalinclude:: ../examples/basic.py
   :language: python

Many more examples are available in the :resource:`repository <examples>`.


Code Reference
---------------
View the documentation for each class and function :doc:`here <api>`.


Contributing
-------------

We warmly welcome contributions.
If you have an idea or some code you want to add to the project please fork :resource:`the repository <repo>`, make your changes, and open a pull request. 
Most likely your changes will get merged if your code passes flake8 without any errors, and adds some functionality to the project. 
We'd love to incorporate your unique ideas and perspective!

