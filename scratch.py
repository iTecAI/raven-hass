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
        with open("services.test.json", "w") as f:
            print(
                json.dumps(
                    [
                        i.model_dump(mode="json")
                        for i in Service.from_services(result.result)
                    ],
                    indent=4,
                ),
                file=f,
            )


asyncio.run(main())
