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
        with open("services.json", "w") as f:
            print(
                (await client.send_ws_command("get_services")).model_dump_json(
                    indent=4
                ),
                file=f,
            )


asyncio.run(main())
