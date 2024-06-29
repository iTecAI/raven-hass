from typing import Any, ClassVar

from pydantic import BaseModel


class RegisteredModel(BaseModel):
    _client: ClassVar[Any] = None
    _registry: ClassVar["Registry"] = None

    @classmethod
    def set_client(cls, client: Any):
        cls._client = client

    @classmethod
    def set_registry(cls, registry: "Registry"):
        cls._registry = registry

    @property
    def client(self) -> Any:
        return self._client

    @property
    def registry(self) -> "Registry | None":
        return self._registry


class Registry:
    def __init__(self):
        self.registry: dict[str, RegisteredModel] = {}

    def register(self, *keys: str):
        if len(keys) == 0:
            raise ValueError("At least one key must be specified")

        def register_inner(original_class: Any):
            for key in keys:
                original_class.set_registry(self)
                original_class.model_rebuild()
                self.registry[key] = original_class
            return original_class

        return register_inner

    def __getitem__(self, key: str):
        return self.registry.get(key, None)

    def assign_client(self, client: Any):
        for v in self.registry.values():
            v.set_client(client)
