from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAction(ABC):
    @abstractmethod
    async def execute(self, data: Dict[str, Any], params: Dict[str, Any]) -> Any:
        pass