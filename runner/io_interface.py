from abc import ABC, abstractmethod
import sys
import multiprocessing as mp
from enum import Enum, auto
import queue
from .error import StopExecution


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


class LinkInMessage(Enum):
    STOP_EXECUTION = auto()


class LinkOutMessage(Enum):
    SET_IN_HINT = auto()


class NonBlockingLink(Console):
    def __init__(self, out_q: mp.Queue, err_q: mp.Queue, in_q: mp.Queue, in_msg_q: mp.Queue, out_msg_q: mp.Queue):
        self.out_q = out_q
        self.err_q = err_q
        self.in_q = in_q
        self.in_msg_q = in_msg_q
        self.out_msg_q = out_msg_q

    def stdout_write(self, string: str):
        self.out_q.put(string)

    def stderr_write(self, string: str):
        self.err_q.put(string)

    def _handle_message(self):
        try:
            msg = self.in_msg_q.get_nowait()
        except queue.Empty:
            return
        if msg[0] == LinkInMessage.STOP_EXECUTION:
            raise StopExecution()

    def stdin_read(self) -> str:
        while True:
            try:
                value = self.in_q.get_nowait()
                break
            except queue.Empty:
                self._handle_message()
        return value

    def stdin_hint(self, string: str):
        self.out_msg_q.put((LinkOutMessage.SET_IN_HINT, string))
