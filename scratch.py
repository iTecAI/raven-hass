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
        print(await client.get_services())


asyncio.run(main())
