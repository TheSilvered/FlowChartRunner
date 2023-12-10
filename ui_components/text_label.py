import pygame as pg
from .base_component import UIBaseComponent, Pos
from text_rendering import write_text, write_text_highlighted


class TextLabel(UIBaseComponent):
    def __init__(self, pos, text, highlight=False, align="left", width=-1):
        self._text = text
        self._highlight = highlight
        self._align = align
        self._width = width
        self._text_surf = None
        super().__init__(pg.Rect(pos, (0, 0)))
        self.render_text()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        prev = self._text
        self._text = value
        if prev != value:
            self.render_text()

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, value):
        prev = self._highlight
        self._highlight = value
        if prev != value:
            self.render_text()

    @property
    def align(self):
        return self._align

    @align.setter
    def align(self, value):
        prev = self._align
        self._align = value
        if prev != value:
            self.render_text()

    @property
    def w(self):
        return self._width

    @w.setter
    def w(self, value):
        prev = self._width
        self._width = value
        if prev != value:
            self.render_text()

    @property
    def size(self) -> Pos:
        return super().size

    @size.setter
    def size(self, value):
        raise ValueError("cannot set the size of a text label")

    def render_text(self):
        if self._highlight:
            self._text_surf = write_text_highlighted(self._text, self._align, self._width)
        else:
            self._text_surf = write_text(self._text, self._align, self._width)
        self.rect.size = self._text_surf.get_size()

    def handle_event(self, event: pg.event.Event) -> bool:
        return False

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        screen.blit(self._text_surf, self.rect)
