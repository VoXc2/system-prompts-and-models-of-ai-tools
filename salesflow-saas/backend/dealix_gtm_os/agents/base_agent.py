from abc import ABC, abstractmethod

class BaseAgent(ABC):
    name: str = "base"
    description: str = ""

    @abstractmethod
    async def run(self, input_data: dict) -> dict:
        pass
