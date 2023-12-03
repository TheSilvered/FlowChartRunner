from draw_utils import *
from constants import INFO_BG_DARK, TEXTBOX_PADDING, TEXTBOX_CARET_COLOR


class TextBox:
    def __init__(self, rect: pg.Rect, on_update, on_update_args, real_time_update: bool, multiline: bool):
        self.text = ""
        self.caret_pos = 0
        self.on_update = on_update
        self.on_update_args = on_update_args
        self.real_time_update: bool = real_time_update
        self.rect: pg.Rect = rect
        self.multiline: bool = multiline
        self._focused: bool = False
        self.area_rect_offset = [0, 0]

    @property
    def focused(self):
        return self._focused

    @focused.setter
    def focused(self, focus):
        if focus:
            pg.key.set_repeat(400, 40)
            self._focused = True
        else:
            pg.key.set_repeat()
            self._focused = False

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

    def __get_caret_pos(self):
        caret_pos = [0, 0]
        line_count = self.text.count("\n", 0, self.caret_pos)
        caret_line = self.__get_current_caret_line(False)
        caret_pos[0] = get_text_size(caret_line)[0]
        caret_pos[1] = line_count * line_height()
        return caret_pos

    def __get_area_rect(self, caret_pos):
        area_rect = pg.Rect(
            self.area_rect_offset,
            (self.rect.w - TEXTBOX_PADDING * 2, self.rect.h - TEXTBOX_PADDING * 2))
        if caret_pos[0] < area_rect.left:
            area_rect.left = caret_pos[0]
            self.area_rect_offset[0] = caret_pos[0]
        elif caret_pos[0] + 2 >= area_rect.right:
            area_rect.right = caret_pos[0] + 1
            self.area_rect_offset[0] = area_rect.right - area_rect.w
        if caret_pos[1] < area_rect.top:
            area_rect.top = caret_pos[1]
            self.area_rect_offset[1] = caret_pos[1]
        elif caret_pos[1] + line_height() >= area_rect.bottom:
            area_rect.bottom = caret_pos[1] + line_height() - 1
            self.area_rect_offset[1] = area_rect.bottom - area_rect.h

        return area_rect

    def draw(self, screen: pg.Surface):
        caret_pos = self.__get_caret_pos()
        area_rect = self.__get_area_rect(caret_pos)

        caret_pos[0] += self.rect.x + TEXTBOX_PADDING - self.area_rect_offset[0]
        caret_pos[1] += self.rect.y + TEXTBOX_PADDING - self.area_rect_offset[1]

        rendered_text = write_text_highlighted(self.text)
        pg.draw.rect(screen, INFO_BG_DARK, self.rect)
        screen.blit(rendered_text, (self.rect.x + TEXTBOX_PADDING, self.rect.y + TEXTBOX_PADDING), area_rect)
        pg.draw.rect(screen, TEXTBOX_CARET_COLOR, pg.Rect(caret_pos, (2, line_height())))

    def insert_text(self, text: str):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        self.text = self.text[:self.caret_pos] + text + self.text[self.caret_pos:]
        self.caret_pos += len(text)

    def handle_event(self, event: pg.event.Event):
        if event.type != pg.KEYDOWN:
            return
        if event.key == pg.K_LEFT:
            self.caret_pos = max(0, self.caret_pos - 1)
        elif event.key == pg.K_RIGHT:
            self.caret_pos = min(len(self.text), self.caret_pos + 1)
        elif event.key == pg.K_UP:
            line_above = self.__get_caret_line_above()
            if line_above is None:
                return
            curr_line = self.__get_current_caret_line(False)
            self.caret_pos -= len(curr_line) + len(line_above) + 1  # + 1 for \n
            self.caret_pos += min(len(curr_line), len(line_above))
        elif event.key == pg.K_DOWN:
            line_below = self.__get_caret_line_below()
            if line_below is None:
                return
            curr_line_full = self.__get_current_caret_line(True)
            curr_line_part = self.__get_current_caret_line(False)
            self.caret_pos += len(curr_line_full) - len(curr_line_part) + 1  # + 1 for \n
            self.caret_pos += min(len(line_below), len(curr_line_part))
        elif event.key == pg.K_END:
            if pg.key.get_mods() & pg.KMOD_CTRL:
                self.caret_pos = len(self.text)
                return
            curr_line_part = self.__get_current_caret_line(False)
            curr_line_full = self.__get_current_caret_line(True)
            self.caret_pos += len(curr_line_full) - len(curr_line_part)
        elif event.key == pg.K_HOME:
            if pg.key.get_mods() & pg.KMOD_CTRL:
                self.caret_pos = 0
                return
            curr_line = self.__get_current_caret_line(False)
            self.caret_pos -= len(curr_line)
        elif event.key == pg.K_BACKSPACE:
            self.text = self.text[:max(0, self.caret_pos - 1)] + self.text[self.caret_pos:]
            self.caret_pos = max(0, self.caret_pos - 1)
        elif event.key == pg.K_DELETE:
            self.text = self.text[:self.caret_pos] + self.text[self.caret_pos + 1:]
        elif event.key == pg.K_ESCAPE:
            self.focused = False
        else:
            self.insert_text(event.unicode)
