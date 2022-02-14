###########
Usage
###########


The Basics...
**************

This library is centered around the :code:`Client` class.
Once you have have your api base url and Long Lived Access Token from homeassistant we can start to do stuff.
The rest of this guide assumes you have the :code:`Client` (or :code:`AsyncClient`) saved to a :code:`client` variable like this.
Most of these examples require some integrations to be setup inside homeassistant for the examples to actually work.


.. code-block:: python
    :linenos:

    import os
    from homeassistant_api import Client

    URL = '<API BASE URL>'
    TOKEN = '<LONG LIVED ACCESS TOKEN>'

    client = Client(URL, TOKEN)


Client
========
The most commonly used features of this library include triggering services and getting and modifying entity states.

Services
---------
.. code-block:: python

    domains = client.get_domains()
    # {'homeassistant': <Domain homeassistant>, 'notify': <Domain notify>}

    service = domains.cover.services.close_cover # Works the same as domains['cover'].services['open_cover']
    # <Service open_cover domain="cover">

    changed_states = client.trigger_service('cover', 'close_cover', entity_id='cover.garage_door')
    # Alternatively (using fetched service from above)
    changed_states = service.trigger(entity_id='cover.garage_door')
    # [<EntityState "closing" entity_id="cover.garage_door">]


Entities
---------

.. code-block:: python

    entity_groups = client.get_entities()
    # {'person': <EntityGroup person>, 'zone': <EntityGroup zone>, ...}

    door = client.get_entity(entity_id='cover.garage_door')
    # <Entity entity_id="cover.garage_door" state="<EntityState "closed">">

    states = client.get_states()
    # [<EntityState "above_horizon" entity_id="sun.sun">, <EntityState "zoning" entity_id="zone.home">,...]

    state = client.get_state('sun.sun')
    # <EntityState "above_horizon" entity_id="sun.sun">

    new_state = client.set_state(state='my ToaTallY Whatever vAlUe 12t87932', group_id='my_favorite_colors', entity_slug='number_one')
    # <EntityState "my ToaTallY Whatever vAlUe 12t87932" entity_id="my_favorite_colors.number_one">

    # Alternatively you can set state from the entity class itself
    from homeassistant_api import State

    # If you are wondering where door came from its about 15 lines up.
    door.state.state = 'My new state'
    door.state.attributes['open_height'] = '23'
    door.set_state(door.state)
    # <EntityState "My new state" entity_id="cover.garage_door">


AsyncClient
=============
Before you run this code you need to install the :code:`homeassistant_api[async]` (it just installs :code:`aiohttp`).
Here is the async counterpart to the usage above.
Except how to run async code in the console without starting an eventloop yourself you ask? You can install :code:`aioconsole` and then run :code:`$ apython`


Services
------------
.. code-block:: python

    from homeassistant_api._async import AsyncClient

    client = AsyncClient(url, token)

    domains = await client.get_domains()
    # {'homeassistant': <Domain homeassistant>, 'notify': <Domain notify>}

    service = domains.cover.services.close_cover # Works the same as domains['cover'].services['open_cover']
    # <Service open_cover domain="cover">

    changed_states = client.trigger_service('cover', 'close_cover', entity_id='cover.garage_door')
    # Alternatively (using fetched service from above)
    changed_states = service.trigger(entity_id='cover.garage_door')
    # [<EntityState "closing" entity_id="cover.garage_door">]


Entities
-----------

.. code-block:: python

    entity_groups = await client.get_entities()
    # {'person': <EntityGroup person>, 'zone': <EntityGroup zone>, ...}

    door = await client.get_entity(entity_id='cover.garage_door')
    # <Entity entity_id="cover.garage_door" state="<EntityState "closed">">

    states = await client.get_states()
    # [<EntityState "above_horizon" entity_id="sun.sun">, <EntityState "zoning" entity_id="zone.home">,...]

    state = await client.get_state('sun.sun')
    # <EntityState "above_horizon" entity_id="sun.sun">

    new_state = await client.set_state(state='my ToaTallY Whatever vAlUe 12t87932', group_id='my_favorite_colors', entity_slug='number_one')
    # <EntityState "my ToaTallY Whatever vAlUe 12t87932" entity_id="my_favorite_colors.number_one">

    # Alternatively you can set state from the entity class itself
    from homeassistant_api import State

    # If you are wondering where door came from its about 15 lines up.
    door.state.state = 'My new state'
    door.state.attributes['open_height'] = '23'
    await door.set_state(door.state)
    # <EntityState "My new state" entity_id="cover.garage_door">


What's Next?
*************

Browse below to learn more about what you can do with :code:`homeassistant_api`.


.. toctree::
   :maxdepth: 2

   processing
   api