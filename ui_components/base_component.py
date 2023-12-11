import pygame as pg
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final


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
            return NotImplemented

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            return Pos(self.x - other[0], self.y - other[1])
        except Exception:
            return NotImplemented

    def __mul__(self, other):
        try:
            return Pos(self.x * other[0], self.y * other[1])
        except Exception:
            return NotImplemented

    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        try:
            return Pos(self.x / other[0], self.y / other[1])
        except ZeroDivisionError as e:
            raise e
        except Exception:
            return NotImplemented

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
        self._constraints = []

    @abstractmethod
    def handle_event(self, event: pg.event.Event) -> bool:
        pass

    @final
    def draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        for constraint in self._constraints:
            constraint.apply(self)
        self._draw(screen, *args, **kwargs)
        # pg.draw.rect(screen, (255, 0, 255), self.rect, 1)

    @abstractmethod
    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        pass

    def add_constraint(self, constraint):
        self._constraints.append(constraint)
        return self

    def clear_constraints(self):
        self._constraints.clear()

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


class DummyComponent(UIBaseComponent):
    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        pass

    def handle_event(self, event: pg.event.Event) -> bool:
        return False
