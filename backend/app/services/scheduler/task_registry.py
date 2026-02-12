from typing import Callable, Dict, Any, Awaitable

class TaskRegistry:
    _registry: Dict[str, Callable[..., Awaitable[Any]]] = {}

    @classmethod
    def register(cls, task_type: str, handler: Callable[..., Awaitable[Any]]):
        cls._registry[task_type] = handler

    @classmethod
    def get_handler(cls, task_type: str) -> Callable[..., Awaitable[Any]]:
        return cls._registry.get(task_type)
