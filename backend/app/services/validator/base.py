from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseValidator(ABC):
    @abstractmethod
    async def validate(self, content: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate content.
        Returns (is_valid, details).
        """
        pass
