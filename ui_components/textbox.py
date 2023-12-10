import time
import pygame as pg
from draw_utils import draw_rect
from text_rendering import get_text_size, line_height, write_text, write_text_highlighted
from .constants import (
    TEXTBOX_BG_COLOR, TEXTBOX_PADDING, TEXTBOX_CARET_COLOR, TEXTBOX_CARET_BLINK_SPEED, TEXTBOX_BORDER_COLOR,
    TEXTBOX_SELECTEC_BORDER_COLOR
)
from text_rendering.constants import HC_STRS
from typing import Callable
from .base_component import UIBaseComponent

movement_keys = pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT, pg.K_HOME, pg.K_END
control_keys = pg.K_LCTRL, pg.K_RCTRL, pg.K_LSHIFT, pg.K_RSHIFT, pg.K_LALT, pg.K_RALT


class TextBox(UIBaseComponent):
    def __init__(
            self,
            rect: pg.Rect,
            placeholder_text: str = "",
            on_update: Callable = None, on_update_args: tuple = (),
            on_send: Callable = None, on_send_args: tuple = (),
            single_line: bool = False
    ):
        super().__init__(rect)

        self._text = ""
        self._caret_pos = 0
        self._focused: bool = False
        self.area_rect_offset = [0, 0]
        self.blink_start = 0
        self.selection_start = None
        self.selecting_with_mouse = False
        self.placeholder_text = placeholder_text
        self.on_update = on_update
        self.on_update_args = on_update_args
        self.on_send = on_send
        self.on_send_args = on_send_args
        self.__single_line = single_line

    @property
    def focused(self):
        return self._focused

    @focused.setter
    def focused(self, focus):
        if self._focused != focus:
            self.selection_start = None
        if focus:
            pg.key.set_repeat(400, 40)
            self._focused = True
            self.blink_start = time.perf_counter()
        else:
            pg.key.set_repeat()
            self._focused = False

    @property
    def caret_pos(self):
        return self._caret_pos

    @caret_pos.setter
    def caret_pos(self, value):
        if self._caret_pos != value:
            self.blink_start = time.perf_counter()
        self._caret_pos = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_value):
        if self._text != new_value:
            self._text = new_value
            if self.on_update is not None:
                self.on_update(self, *self.on_update_args)

    def set_text(self, text):
        self.text = text
        self.caret_pos = len(text)

    def __get_current_caret_line(self, whole):
        start = self.text.rfind("\n", 0, self.caret_pos)
        if whole:
            end = self.text.find("\n", self.caret_pos)
            if end == -1:
                end = len(self.text)
        else:
            end = self.caret_pos
        return self.text[start + 1:end]

    def __get_caret_line_above(self):
        end = self.text.rfind("\n", 0, self.caret_pos)
        if end == -1:
            return None
        start = self.text.rfind("\n", 0, end)
        return self.text[start + 1:end]

    def __get_caret_line_below(self):
        start = self.text.find("\n", self.caret_pos)
        if start == -1:
            return None
        end = self.text.find("\n", start + 1)
        if end == -1:
            end = len(self.text)
        return self.text[start + 1:end]

    def __get_caret_pos(self, ignore_x=False):
        caret_pos = [0, 0]
        line_count = self.text.count("\n", 0, self.caret_pos)
        if not ignore_x:
            caret_line = self.__get_current_caret_line(False)
            caret_pos[0] = get_text_size(caret_line)[0]
        caret_pos[1] = line_count * line_height()
        return caret_pos

    def __get_area_rect(self, caret_pos):
        area_rect = pg.Rect(
            self.area_rect_offset,
            (self.w - TEXTBOX_PADDING * 2, self.h - TEXTBOX_PADDING * 2))
        if caret_pos[0] < area_rect.left:
            area_rect.left = caret_pos[0]
        elif caret_pos[0] + 2 >= area_rect.right:
            area_rect.right = caret_pos[0] + 1
        if caret_pos[1] < area_rect.top:
            area_rect.top = caret_pos[1]
        elif caret_pos[1] + line_height() >= area_rect.bottom:
            area_rect.bottom = caret_pos[1] + line_height() - 1

        line_count = self.text.count("\n") + 1
        max_y = line_count * line_height()
        if area_rect.bottom > max_y > area_rect.h:
            area_rect.bottom = max_y
        elif area_rect.h > max_y:
            area_rect.top = 0

        max_x = max(map(lambda x: get_text_size(x)[0], self.text.split("\n")))
        if area_rect.right > max_x > area_rect.w:
            area_rect.right = max_x
        elif area_rect.w > max_x:
            area_rect.left = 0

        self.area_rect_offset = [area_rect.x, area_rect.y]
        return area_rect

    def __get_selection_range(self):
        if self.selection_start is None:
            return self.caret_pos, self.caret_pos
        selection_start = min(self.caret_pos, self.selection_start)
        selection_end   = max(self.caret_pos, self.selection_start)
        return selection_start, selection_end

    def draw(self, screen: pg.Surface):
        caret_pos = self.__get_caret_pos()
        area_rect = self.__get_area_rect(caret_pos)

        caret_pos[0] += self.x + TEXTBOX_PADDING - self.area_rect_offset[0]
        caret_pos[1] += self.y + TEXTBOX_PADDING - self.area_rect_offset[1]

        if self.selection_start is None or self.caret_pos == self.selection_start:
            selection_range = None
        else:
            selection_range = self.__get_selection_range()

        if self.text:
            rendered_text = write_text_highlighted(
                self.text,
                selection_range=selection_range,
                add_newline_width=True
            )
        else:
            rendered_text = write_text(
                HC_STRS["light_gray"] + self.placeholder_text,
                selection_range=selection_range,
                add_newline_width=True
            )

        if self.focused:
            draw_rect(screen, self.rect, TEXTBOX_BG_COLOR, TEXTBOX_PADDING, 2, TEXTBOX_SELECTEC_BORDER_COLOR)
        else:
            draw_rect(screen, self.rect, TEXTBOX_BG_COLOR, TEXTBOX_PADDING, 2, TEXTBOX_BORDER_COLOR)

        screen.blit(rendered_text, (self.x + TEXTBOX_PADDING, self.y + TEXTBOX_PADDING), area_rect)

        curr_time = time.perf_counter()
        if not self.focused:
            return
        if curr_time - self.blink_start <= TEXTBOX_CARET_BLINK_SPEED:
            pg.draw.rect(screen, TEXTBOX_CARET_COLOR, pg.Rect(caret_pos, (2, line_height())))
        elif curr_time - self.blink_start > TEXTBOX_CARET_BLINK_SPEED * 2:
            self.blink_start = curr_time

    def insert_text(self, text: str):
        if not text:
            return
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        selection_range = self.__get_selection_range()
        self.text = self.text[:selection_range[0]] + text + self.text[selection_range[1]:]
        self.caret_pos = selection_range[0] + len(text)
        self.selection_start = None

    def __get_caret_pos_from_coordinates(self, pos):
        pos = list(pos)
        pos[0] -= self.x + TEXTBOX_PADDING
        pos[1] -= self.y + TEXTBOX_PADDING
        orig_caret_pos = self.caret_pos
        self.caret_pos = 0

        # Get the caret to the start of the correct line
        while self.__get_caret_pos(True)[1] < pos[1]:
            new_pos = self.text.find("\n", self.caret_pos)
            if new_pos == -1:
                break
            self.caret_pos = new_pos + 1
        else:
            # Put the character to the beginning of the previous line if the last line has not been reached
            # The max is to prevent rfind to end at -1
            self.caret_pos = self.text.rfind("\n", 0, max(0, self.caret_pos - 1)) + 1

        # Put the character after the selected character
        while self.__get_caret_pos()[0] < pos[0]:
            if self.caret_pos >= len(self.text) or self.text[self.caret_pos] == '\n':
                break
            self.caret_pos += 1

        # Put the character to the start of the previous character if the position is before the half point of the char
        if self.caret_pos > 0 and self.text[self.caret_pos - 1] != '\n':
            next_x = self.__get_caret_pos()[0]
            self.caret_pos -= 1
            prev_x = self.__get_caret_pos()[0]
            if pos[0] - prev_x > next_x - pos[0]:
                self.caret_pos += 1

        final_pos = self.caret_pos
        self.caret_pos = orig_caret_pos
        return final_pos

    def send(self):
        if self.on_send is not None:
            self.on_send(self, *self.on_send_args)
        self.focused = False

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == pg.BUTTON_LEFT:
            if not self.rect.collidepoint(event.pos):
                return False
            self.caret_pos = self.__get_caret_pos_from_coordinates(event.pos)
            self.selection_start = self.caret_pos
            self.selecting_with_mouse = True
            return True
        elif event.type == pg.MOUSEBUTTONUP and event.button == pg.BUTTON_LEFT:
            if self.caret_pos == self.selection_start and self.selecting_with_mouse:
                self.selection_start = None
            if self.selecting_with_mouse:
                self.selecting_with_mouse = False
                return True
            return self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEMOTION and self.selecting_with_mouse:
            if self.selecting_with_mouse:
                self.caret_pos = self.__get_caret_pos_from_coordinates(event.pos)
            return True
        elif event.type != pg.KEYDOWN:
            return False

        if self.selection_start is None:
            if pg.key.get_mods() & pg.KMOD_SHIFT and event.key in movement_keys:
                self.selection_start = self.caret_pos
        elif (self.selection_start is not None
              and not (pg.key.get_mods() & pg.KMOD_SHIFT)
              and event.key in movement_keys):
            self.selection_start = None

        if event.key == pg.K_LEFT:
            self.caret_pos = max(0, self.caret_pos - 1)
        elif event.key == pg.K_RIGHT:
            self.caret_pos = min(len(self.text), self.caret_pos + 1)
        elif event.key == pg.K_UP:
            line_above = self.__get_caret_line_above()
            if line_above is None:
                return True
            curr_line = self.__get_current_caret_line(False)
            self.caret_pos -= len(curr_line) + len(line_above) + 1  # + 1 for \n
            self.caret_pos += min(len(curr_line), len(line_above))
        elif event.key == pg.K_DOWN:
            line_below = self.__get_caret_line_below()
            if line_below is None:
                return True
            curr_line_full = self.__get_current_caret_line(True)
            curr_line_part = self.__get_current_caret_line(False)
            self.caret_pos += len(curr_line_full) - len(curr_line_part) + 1  # + 1 for \n
            self.caret_pos += min(len(line_below), len(curr_line_part))
        elif event.key == pg.K_END:
            if pg.key.get_mods() & pg.KMOD_CTRL:
                self.caret_pos = len(self.text)
                return True
            curr_line_part = self.__get_current_caret_line(False)
            curr_line_full = self.__get_current_caret_line(True)
            self.caret_pos += len(curr_line_full) - len(curr_line_part)
        elif event.key == pg.K_HOME:
            if pg.key.get_mods() & pg.KMOD_CTRL:
                self.caret_pos = 0
                return True
            curr_line = self.__get_current_caret_line(False)
            self.caret_pos -= len(curr_line)
        elif event.key == pg.K_BACKSPACE:
            if self.selection_start is not None and self.selection_start != self.caret_pos:
                sel_range = self.__get_selection_range()
                self.text = self.text[:sel_range[0]] + self.text[sel_range[1]:]
                self.caret_pos = sel_range[0]
                self.selection_start = None
            else:
                self.text = self.text[:max(0, self.caret_pos - 1)] + self.text[self.caret_pos:]
                self.caret_pos = max(0, self.caret_pos - 1)
                self.selection_start = None
        elif event.key == pg.K_DELETE:
            if self.selection_start is not None and self.selection_start != self.caret_pos:
                sel_range = self.__get_selection_range()
                self.text = self.text[:sel_range[0]] + self.text[sel_range[1]:]
                self.caret_pos = sel_range[0]
                self.selection_start = None
            else:
                self.text = self.text[:self.caret_pos] + self.text[self.caret_pos + 1:]
                self.selection_start = None
        elif event.key == pg.K_ESCAPE:
            if self.selection_start is not None:
                self.selection_start = None
            else:
                self.focused = False
        elif event.key == pg.K_RETURN:
            self.send()
            return True
        elif event.key not in control_keys:
            self.insert_text(event.unicode)

        return True
