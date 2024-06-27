from asyncio import Event, Queue, Task, create_task
from contextlib import asynccontextmanager, contextmanager
import json
from traceback import print_exc
from typing import Any, AsyncGenerator, TypeVar
from urllib.parse import urlparse
from uuid import uuid4
from httpx import AsyncClient
from websockets import ConnectionClosed, WebSocketClientProtocol, connect
from .models import WS_MESSAGE_TYPES, WSMessage, WSResult


class BaseApi:
    def __init__(self, host: str, token: str):
        self.host = host
        self.token = token
        self._rest_client: AsyncClient | None = None
        self._ws_client: WebSocketClientProtocol | None = None
        self.ws_task: Task | None = None
        self.event_queues: dict[str, tuple[str, Queue]] = {}
        self.ws_active = Event()
        self.hass_version: str | None = None
        self.ws_id = 1

    @property
    def rest(self) -> AsyncClient:
        if not self._rest_client:
            raise RuntimeError("Attempting to call uninitialized API")
        return self._rest_client

    @property
    def ws(self) -> WebSocketClientProtocol:
        if not self._ws_client:
            raise RuntimeError("Attempting to call uninitialized API")
        return self._ws_client

    @property
    def base_host(self) -> str:
        return urlparse(self.host).netloc

    @property
    def secure(self) -> bool:
        return urlparse(self.host).scheme == "https"

    async def run_ws(self):
        async for websocket in connect(
            ("wss://" if self.secure else "ws://") + self.base_host + "/api/websocket"
        ):
            self._ws_client = websocket
            self.ws_active.set()
            self.ws_id = 1
            try:
                async for message in websocket:
                    try:
                        parsed = json.loads(message)
                        if "type" in parsed.keys():
                            obj = WS_MESSAGE_TYPES[parsed["type"]](**parsed)
                            for queue in self.event_queues.values():
                                if queue[0] == obj.type:
                                    queue[1].put_nowait(obj)
                    except:
                        pass
            except ConnectionClosed:
                continue
            finally:
                self._ws_client = None
                self.ws_active.clear()

    async def __aenter__(self):
        self._rest_client = AsyncClient(
            headers={
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
            }
        )
        self.ws_task = create_task(self.run_ws())
        with self.events("auth_required", "auth_ok", "auth_invalid") as events:
            async for event in events:
                if event.type == "auth_required":
                    await self.ws.send(
                        json.dumps({"type": "auth", "access_token": self.token})
                    )
                else:
                    if event.ok:
                        self.hass_version = event.ha_version
                        return self
                    raise RuntimeError("Failed to authenticate")

    async def __aexit__(self, *args, **kwargs):
        if self._rest_client:
            await self._rest_client.aclose()

        if self.ws_task:
            self.ws_task.cancel()

    @contextmanager
    def events(self, *event_types: str):
        queue = Queue()
        ids = []
        for ev in list(set(event_types)):
            _id = uuid4().hex
            self.event_queues[_id] = (ev, queue)
            ids.append(_id)

        async def _listen():
            while True:
                yield await queue.get()

        try:
            yield _listen()
        finally:
            for i in ids:
                del self.event_queues[i]

    async def send_ws(self, type: str, **kwargs) -> int:
        msg_id = self.ws_id
        self.ws_id += 1
        data = {"id": msg_id, "type": type, **kwargs}
        await self.ws_active.wait()
        await self.ws.send(json.dumps(data))
        return msg_id

    async def send_ws_command(self, type: str, **kwargs) -> WSResult:
        with self.events("result") as results:
            msg_id = await self.send_ws(type, **kwargs)
            async for message in results:
                if message.id == msg_id:
                    return message
