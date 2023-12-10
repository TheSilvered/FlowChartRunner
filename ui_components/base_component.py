import pygame as pg
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Pos:
    x: int
    y: int

    @property
    def t(self) -> tuple[int | float, int | float]:
        return self.x, self.y

    @property
    def ti(self) -> tuple[int, int]:
        return int(self.x), int(self.y)

    @property
    def i(self):
        return Pos(*self.ti)

    def __add__(self, other):
        try:
            return Pos(self.x + other[0], self.y + other[1])
        except Exception:
            raise NotImplemented

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            return Pos(self.x - other[0], self.y - other[1])
        except Exception:
            raise NotImplemented

    def __isub__(self, other):
        return self.__sub__(other)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError(f"index {item} out of Pos")

    def __iter__(self):
        return iter(self.t)


pos_t = Pos | tuple[int | float, int | float] | list[int | float]


class UIBaseComponent(ABC):
    def __init__(self, rect: pg.Rect):
        self._rect = rect

    @abstractmethod
    def handle_event(self, event: pg.event.Event) -> bool:
        pass

    @abstractmethod
    def draw(self, screen: pg.Surface) -> None:
        pass

    @property
    def rect(self) -> pg.Rect:
        return self._rect

    @rect.setter
    def rect(self, value: pg.Rect):
        self._rect = value

    @property
    def pos(self) -> Pos:
        return Pos(*self._rect.topleft)

    @pos.setter
    def pos(self, value: pos_t):
        self._rect.topleft = Pos(*value).t

    @property
    def pos_i(self) -> Pos:
        return self.pos.i

    @property
    def x(self) -> int | float:
        return self.pos.x

    @x.setter
    def x(self, value: int | float):
        self.pos = (value, self.y)

    @property
    def xi(self) -> int:
        return int(self.x)

    @property
    def y(self) -> int | float:
        return self.pos.y

    @y.setter
    def y(self, value: int | float):
        self.pos = (self.x, value)

    @property
    def yi(self) -> int:
        return int(self.y)

    @property
    def size(self) -> Pos:
        return Pos(*self._rect.size)

    @size.setter
    def size(self, value: pos_t):
        self._rect.size = Pos(*value).t

    @property
    def size_i(self) -> Pos:
        return self.size.i

    @property
    def w(self):
        return self.size.x

    @w.setter
    def w(self, value: int | float):
        self.size = (value, self.h)

    @property
    def wi(self):
        return int(self.w)

    @property
    def h(self):
        return self.size.y

    @h.setter
    def h(self, value: int | float):
        self.size = (self.w, value)

    @property
    def hi(self):
        return int(self.h)
