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
        print(client.hass_version)
        result = await client.send_ws_command("get_services")
        for svc in Service.from_services(result.result):
            for field in svc.fields.values():
                print(field.selector.client)


asyncio.run(main())
