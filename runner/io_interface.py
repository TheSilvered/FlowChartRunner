from abc import ABC, abstractmethod


class Console(ABC):
    @abstractmethod
    def stdout_write(self, string: str):
        pass

    @abstractmethod
    def stderr_write(self, string: str):
        pass

    @abstractmethod
    def stdin_read(self) -> str:
        pass
