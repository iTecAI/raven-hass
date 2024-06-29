from typing import Any


class Registry:
    def __init__(self):
        self.registry = {}

    def register(self, *keys: str):
        if len(keys) == 0:
            raise ValueError("At least one key must be specified")

        def register_inner(original_class: Any):
            for key in keys:
                self.registry[key] = original_class
            return original_class

        return register_inner

    def __getitem__(self, key: str):
        return self.registry.get(key, None)
