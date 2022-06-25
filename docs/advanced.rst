*******************
Advanced Section
*******************

Persistent Caching
********************

Persistent caching is exactly what it means. It makes your requests cache persist or stay around between :py:class:`Client` objects, and between runs, and contexts (:code:`with client:` statements).
Rather than the default behavior, which is saving the cache to memory or not at all and erasing it after each context and run.


If you want to persist your requests cache you can pass your own custom cached session to :py:class:`Client`'s init method.
You can pass a variety of options to your cached session like how fast to expire the cache, where to cache it (the cache backend), and what to do when the cache is expired.

Depending on whether you are using this in an async of sync project you will want to use either :py:class:`aiohttp_client_cache.backends.CachedSession` or :py:class:`requests_cache.CachedSession` respectively.
See the docs for `requests_cache <https://requests-cache.readthedocs.io/en/latest/>`__ and `aiohttp_client_cache <https://aiohttp-client-cache.readthedocs.io/en/latest/>`__ for how to implement these backends, options, and much more.

You can simply pass them to your client like so.

.. code-block:: python

    from homeassistant_api import Client
    from requests_cache import CachedSession

    client = Client(
        "<API_URL>",
        "<TOKEN>",
        cache_session=CachedSession(
            backend="filesystem",
            expire_after=timedelta(minutes=5)
        )
    )

    # CachedSession is activated by the `with` statement.
    with client:
        # Grab and update some cool entities and services inside your installation.
        ...

    # Or an example for async
    import asyncio
    from homeassistant_api import Client
    from aiohttp_client_cache import CachedSession, FileBackend

    client = Client("<URL>", "<TOKEN>", cache_session=CachedSession(cache=FileBackend(), expire_after=timedelta(minutes=5)))
    # CachedSession is activated by the `async with` statement.
    async def main():
        async with client:
            # Grab and update some cool entities and services inside your installation.
            ...
    asyncio.run(main())


Response Processing
**********************
Home Assistant API uses functions called processors.
These functions take a Response object as a parameter and return the python data type associated with the content-type header.

How To Register Response Processors (Converters)
==================================================

To register a response processor you need to import the Processing class and then implement the decorator.


.. code-block:: python

    from homeassistant_api import Processing, Client
    from homeassistant_api.processing import process_json


    @Processing.processor("application/octet-stream")
    def text_processor(response):
        return response.text.lower()

    @Processing.processor("text/csv")
    async def async_text_processor(response):
        text = await response.text()
        return [line.split(",") for line in text.splitlines()]

    @Processing.processor("application/json")
    def json_processor(response):
        print("I processed a json response!)
        return process_json(response)


    client = Client(url, token)
    print(client.get_entities())


In this example.
The first processor (a function wrapped with the processor decorator) is going to be called when we receive a response that has that as its :code:`Content-Type` header.
:code:`homeassistant_api` provides processors for :code:`application/octet-stream` and :code:`application/json` by default,
But :code:`@Processing.processor` gives the most recently registered processor the highest precedence when choosing a processor for a response.
So our processor here will be chosen over the default processors.

The second processor is an async processor that only gets called when Client receives an async response that has :code:`text/csv` as its :code:`Content-Type` header.
If you wanted, you could not use :code:`homeassistant_api`'s default json processing using the :code:`json` module,
and use instead the :code:`ujson` module (which is faster but more restrictive).

The third processor function implements the default processor function for the :code:`application/json` mimetype after printing a string.
If you wanted to run some intermediate processing.

Most likely the only processors you will ever use are :code:`application/json` and :code:`application/octet-stream`
