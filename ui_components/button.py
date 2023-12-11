from abc import ABC
import pygame as pg
from .base_component import UIBaseComponent


class Button(UIBaseComponent, ABC):
    def __init__(self, rect, on_click=None, on_click_args: tuple | list = (), state_count: int = 0):
        super().__init__(rect)
        self.state_count = state_count
        self._current_state = 0
        self._pressed = False
        self.on_click = on_click
        self.on_click_args = on_click_args

    @property
    def current_state(self):
        return self._current_state

    def click(self):
        if self.state_count > 0:
            self._current_state += 1
            self._current_state %= self.state_count
        if self.on_click is not None:
            self.on_click(*self.on_click_args)

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos) and event.button == pg.BUTTON_LEFT:
            self._pressed = True
            return True
        elif event.type == pg.MOUSEBUTTONUP and event.button == pg.BUTTON_LEFT:
            if not self._pressed:
                return False
            self._pressed = False
            if self.rect.collidepoint(event.pos):
                self.click()
                return True
            return False
        return False
