*******************
Advanced Section
*******************

Persistent Caching
********************

Persistent caching is exactly what it means. It's making your requests cache between :ref:`Client` objects, and between runs, and contexts (:code:`with client:` statements), well... persist.
Rather than the default behavior, which is saving the cache to memory and erasing it after each context and run.


If you want to persist your requests cache you can pass your own caching backend and expire after amount to :ref:`Client`'s init method.
The most frequently used backends are filesystem backends or sqlite backends.
You can use :py:class:`aiohttp_client_cache.backends.filesystem.FileBackend` or :py:class:`requests_cache.backends.filesystem.FileCache` depending on whether your program is async or not.
See the docs for `requests_cache <https://requests-cache.readthedocs.io/en/latest/>`__ and `aiohttp_client_cache <https://aiohttp-client-cache.readthedocs.io/en/latest/>`__ for how to implement these backends and much more.

You can simply pass them to your client like so.

.. code-block:: python

    from homeassistant_api import Client
    from requests_cache import FileCache

    client = Client("<URL>", "<TOKEN>", cache_backend=FileCache(cache_name="<whatever_you_want>", cache_dir="foobar-cache"))

    # CachedSession is activated by the `with` statement.
    with client:
        # Grab and update some cool entities and services inside your installation.
        ...

    # Or an example for async

    from homeassistant_api import Client
    from aiohttp_client_cache import SQLiteCache

    client = Client("<URL>", "<TOKEN>", cache_backend=SQLiteCache('my_app_cache', timeout=60))
    # CachedSession is activated by the `async with` statement.
    async def main():
        async with client:
            # Grab and update some cool entities and services inside your installation.
            ...


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
