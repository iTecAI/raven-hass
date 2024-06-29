import json
from dotenv import load_dotenv

load_dotenv()

import os
import asyncio
from raven_hass import RavenHassClient, Service


async def main():
    async with RavenHassClient(
        os.environ["HASS_API"], os.environ["HASS_TOKEN"]
    ) as client:
        entities = await client.get_entities()
        for ent in entities:
            if ent.domain == "light":
                print(await ent.call_service("light.toggle"))


asyncio.run(main())
