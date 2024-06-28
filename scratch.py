from dotenv import load_dotenv

load_dotenv()

import os
import asyncio
from raven_hass import RavenHassClient


async def main():
    async with RavenHassClient(
        os.environ["HASS_API"], os.environ["HASS_TOKEN"]
    ) as client:
        print(client.hass_version)
        async for event in client.subscribe_events():
            print(event)


asyncio.run(main())
