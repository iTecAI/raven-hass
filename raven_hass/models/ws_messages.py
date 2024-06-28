from typing import Any, Literal, Type
from pydantic import BaseModel


class WSMessage(BaseModel):
    id: int | None = None
    type: str


class WSAuthRequired(WSMessage):
    type: Literal["auth_required"]
    ha_version: str


class WSAuthResult(WSMessage):
    type: Literal["auth_ok", "auth_invalid"]
    ha_version: str | None = None
    message: str | None = None

    @property
    def ok(self) -> bool:
        return self.type == "auth_ok"


class WSResult[T](WSMessage):
    type: Literal["result"]
    success: bool
    result: T | None = None
    error: Any | None = None


class WSEvent(WSMessage):
    type: Literal["event"]
    event: Any


WS_MESSAGE_TYPES: dict[str, Type[WSMessage]] = {
    "auth_required": WSAuthRequired,
    "auth_ok": WSAuthResult,
    "auth_invalid": WSAuthResult,
    "result": WSResult,
    "event": WSEvent,
}
