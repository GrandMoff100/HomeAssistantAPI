###########
Usage
###########


The Basics...
#################

This library is centered around the :ref:`Client` class.
Once you have have your api base url and Long Lived Access Token from Home Assistant we can start to do stuff.
The rest of this guide assumes you have the :ref:`Client` saved to a :code:`client` variable.
Most of these examples require some integrations to be setup inside Home Assistant for the examples to actually work.
The most commonly used features of this library include triggering services and getting and modifying entity states.


.. code-block:: python
    :linenos:

    import os
    from homeassistant_api import Client

    URL = '<API BASE URL>'
    TOKEN = '<LONG LIVED ACCESS TOKEN>'

    # Assigns the Client object to a variable and checks if it's running.
    client = Client(URL, TOKEN)

    service = client.get_domain("light")  # Gets the light service domain from Home Assistant

    service.turn_on(entity_id="light.my_living_room_light")
    # Triggers the light.turn_on service on the entity `light.my_living_room_light`


.. code-block:: python
   :linenos:

    from datetime import datetime
    from homeassistant_api import Client

    # You can also initialize Client before you use it.

    client = Client("https://myhomeassistant.duckdns.org:8123/api", "mylongtokenpasswordthingyfoobar")

    # If you want to use caching you can use client as a context manager like so
    with client:
        while True:
            sun = client.get_entity(entity_id="sun.sun")
            state = sun.get_state()  # Because requests are cached we reduce bandwidth usage :D
            # Cache expires every 30 seconds by default.
            if state.state == "below_horizon":
                difference = datetime.now() - state.last_updated
                print("Sun set", difference.seconds, "seconds ago.")
                break

Services
**********

.. code-block:: python

    light = client.get_domain("light")

    print(light.services)
    # {'turn_on': Service(service_id='turn_on', name='Turn on', description='Turn on one or more lights and adjust properties of the light, even when they are turned on already.\n', ...

    changed_states = light.toggle(entity_id="light.light_bulb_1")

Entities
*************

.. code-block:: python

    entity_groups = client.get_entities()
    # {'person': <Group person>, 'zone': <Group zone>, ...}

    door = client.get_entity(entity_id='cover.garage_door')
    # <Entity entity_id="cover.garage_door" state="<EntityState "closed">">

    states = client.get_states()
    # [<State "above_horizon" entity_id="sun.sun">, <State "zoning" entity_id="zone.home">,...]

    state = client.get_state('sun.sun')
    # <State "above_horizon" entity_id="sun.sun">

    new_state = client.set_state(state='my ToaTallY Whatever vAlUe 12t87932', group_id='my_favorite_colors', entity_slug='number_one')
    # <State "my ToaTallY Whatever vAlUe 12t87932" entity_id="my_favorite_colors.number_one">

    # Alternatively you can set state from the entity class itself
    from homeassistant_api import State

    # If you are wondering where door came from its about 15 lines up.
    door.set_state(State(state="My new state", attributes={"open_height": "5ft"}))
    # <State "My new state" entity_id="cover.garage_door">


Using Client with :code:`async`/:code:`await`
*************************************************
Are you wondering if you can use :code:`homeassistant_api` using Python's :code:`async`/:code:`await` syntax?
Good news! You can!

Async Services
********************
.. code-block:: python

    import asyncio
    from homeassistant_api import Client

    # Initialize client like usual
    client = Client(url, token)

    async def main():

        domains = await client.async_get_domains()
        print(domains)
        # {'homeassistant': <Domain homeassistant>, 'notify': <Domain notify>}

        cover = await client.async_get_domain("cover")

        changed_states = await cover.close_cover(entity_id='cover.garage_door')
        # [<EntityState "closing" entity_id="cover.garage_door">]

    asyncio.get_event_loop().run_until_complete(main())

Async Entities
*****************

.. code-block:: python

    entity_groups = await client.async_get_entities()
    # {'person': <EntityGroup person>, 'zone': <EntityGroup zone>, ...}

    door = await client.async_get_entity(entity_id='cover.garage_door')
    # <Entity entity_id="cover.garage_door" state="<EntityState "closed">">

    states = await client.async_get_states()
    # [<EntityState "above_horizon" entity_id="sun.sun">, <EntityState "zoning" entity_id="zone.home">,...]

    state = await client.async_get_state('sun.sun')
    # <EntityState "above_horizon" entity_id="sun.sun">

    new_state = await client.async_set_state(state='my ToaTallY Whatever vAlUe 12t87932', group_id='my_favorite_colors', entity_slug='number_one')
    # <EntityState "my ToaTallY Whatever vAlUe 12t87932" entity_id="my_favorite_colors.number_one">

    # Alternatively you can set state from the entity class itself
    from homeassistant_api import State

    # If you are wondering where door came from its about 15 lines up.
    door.state.state = 'My new state'
    door.state.attributes['open_height'] = '23'
    await door.async_set_state(door.state)
    # <EntityState "My new state" entity_id="cover.garage_door">


What's Next?
#############

Browse below to learn more about what you can do with :mod:`homeassistant_api`.

* `API Reference <api.html>`_
* `Advanced Section <advanced.html>`_
