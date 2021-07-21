import os
import asyncio
from homeassistant_api import AsyncClient

url = os.getenv('HOMEASSISTANT_API_ENDPOINT')
token = os.getenv('HOMEASSISTANT_API_TOKEN')


async def main():
    async with AsyncClient(url, token) as client:
        data = await client.get_entities()
        print(data)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())