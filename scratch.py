import json
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
        with open("services.test.json", "w") as f:
            print(
                json.dumps(
                    [
                        [i for i in j.values()]
                        for j in (await client.send_ws_command("get_services"))
                        .model_dump(mode="json")["result"]
                        .values()
                    ]
                ),
                file=f,
            )


asyncio.run(main())
