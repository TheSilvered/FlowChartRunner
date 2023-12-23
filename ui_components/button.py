from abc import ABC
from typing import Callable
import pygame as pg
from .base_component import UIBaseComponent


class Button(UIBaseComponent, ABC):
    def __init__(
            self,
            rect: pg.Rect,
            on_click: Callable = None,
            on_click_args: tuple | list = (),
            state_count: int = 0,
            extra_padding: int | tuple[int, int] | tuple[int, int, int, int] = 0):
        super().__init__(rect)
        self.state_count = state_count
        self._current_state = 0
        self._pressed = False
        self.on_click = on_click
        self.on_click_args = on_click_args
        if isinstance(extra_padding, int):
            self.extra_padding = (extra_padding, extra_padding, extra_padding, extra_padding)
        elif len(extra_padding) == 2:
            self.extra_padding = (extra_padding[0], extra_padding[1], extra_padding[0], extra_padding[1])
        else:
            self.extra_padding = extra_padding

    @property
    def current_state(self):
        return self._current_state

    @property
    def pressed(self):
        return self._pressed

    def click(self):
        if self.state_count > 0:
            self._current_state += 1
            self._current_state %= self.state_count
        if self.on_click is not None:
            self.on_click(*self.on_click_args)

    def collide_clickable(self, point):
        rect = self.rect.copy()
        rect.x -= self.extra_padding[0]
        rect.y -= self.extra_padding[1]
        rect.w += self.extra_padding[0] + self.extra_padding[2]
        rect.h += self.extra_padding[1] + self.extra_padding[3]
        return rect.collidepoint(point)

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and self.collide_clickable(event.pos) and event.button == pg.BUTTON_LEFT:
            self._pressed = True
            return True
        elif event.type == pg.MOUSEBUTTONUP and event.button == pg.BUTTON_LEFT:
            if not self._pressed:
                return False
            self._pressed = False
            if self.collide_clickable(event.pos):
                self.click()
                return True
            return False
        return False
