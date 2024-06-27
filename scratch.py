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
        result = await client.send_ws_command("get_states", _type=dict)
        print(result)


asyncio.run(main())
