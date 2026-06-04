from abc import ABC, abstractmethod


class BaseTool(ABC):

    name: str = ""
    description: str = ""
    parameters: dict = {}

    @abstractmethod
    def execute(
        self,
        params: dict,
        system_state: dict
    ) -> list:
        pass