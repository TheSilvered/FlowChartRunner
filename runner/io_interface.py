from abc import ABC, abstractmethod
import sys


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

    @abstractmethod
    def stdin_hint(self, string: str):
        pass


class TerminalLink(Console):
    def stdout_write(self, string: str):
        print(string, file=sys.stdout, flush=True)

    def stderr_write(self, string: str):
        print(string, file=sys.stderr, flush=True)

    def stdin_read(self) -> str:
        return input("> ")

    def stdin_hint(self, string: str):
        print(string, end=" ")
