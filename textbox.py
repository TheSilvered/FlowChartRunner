from draw_utils import *
from constants import INFO_BG_DARK, TEXTBOX_PADDING


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
            pg.key.set_repeat(300, 25)
            self._focused = True
        else:
            pg.key.set_repeat()
            self._focused = False

    def draw(self, screen: pg.Surface):
        cursor_pos = [0, 0]
        text = self.text[:self.caret_pos]
        lines = text.split("\n")
        cursor_pos[0] = get_text_size(lines[-1])[0]
        cursor_pos[1] = (len(lines) - 1) * line_height()
        area_rect = pg.Rect(
            self.area_rect_offset,
            (self.rect.w - TEXTBOX_PADDING * 2, self.rect.h - TEXTBOX_PADDING * 2))
        if cursor_pos[0] < area_rect.left:
            area_rect.left = cursor_pos[0]
            self.area_rect_offset[0] = cursor_pos[0]
        elif cursor_pos[0] + 2 >= area_rect.right:
            area_rect.right = cursor_pos[0] + 1
            self.area_rect_offset[0] = area_rect.right - area_rect.w
        if cursor_pos[1] < area_rect.top:
            area_rect.top = cursor_pos[1]
            self.area_rect_offset[1] = cursor_pos[1]
        elif cursor_pos[1] + line_height() >= area_rect.bottom:
            area_rect.bottom = cursor_pos[1] + line_height() - 1
            self.area_rect_offset[1] = area_rect.bottom - area_rect.h

        cursor_pos[0] += self.rect.x + TEXTBOX_PADDING - self.area_rect_offset[0]
        cursor_pos[1] += self.rect.y + TEXTBOX_PADDING - self.area_rect_offset[1]

        rendered_text = write_text_highlighted(self.text)
        pg.draw.rect(screen, INFO_BG_DARK, self.rect)
        screen.blit(rendered_text, (self.rect.x + TEXTBOX_PADDING, self.rect.y + TEXTBOX_PADDING), area_rect)
        pg.draw.rect(screen, (255, 0, 0), pg.Rect(cursor_pos, (2, line_height())))

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                self.caret_pos = max(0, self.caret_pos - 1)
            elif event.key == pg.K_RIGHT:
                self.caret_pos = min(len(self.text), self.caret_pos + 1)
            elif event.key == pg.K_UP:
                text = self.text[:self.caret_pos]
                lines = text.split("\n")
                if len(lines) == 1:
                    return
                self.caret_pos -= len(lines[-1]) + len(lines[-2]) + 1  # + 1 for \n
                self.caret_pos += min(len(lines[-1]), len(lines[-2]))
            elif event.key == pg.K_DOWN:
                text = self.text[:self.caret_pos]
                lines = text.split("\n")
                all_lines = self.text.split("\n", maxsplit=len(lines) + 1)
                if len(all_lines) - len(lines) == 0:
                    return
                curr_line = all_lines[len(lines) - 1]
                next_line = all_lines[len(lines)]
                self.caret_pos += len(curr_line) - len(lines[-1]) + 1
                self.caret_pos += min(len(next_line), len(lines[-1]))
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:max(0, self.caret_pos - 1)] + self.text[self.caret_pos:]
                self.caret_pos = max(0, self.caret_pos - 1)
            elif event.key == pg.K_DELETE:
                self.text = self.text[:self.caret_pos] + self.text[self.caret_pos + 1:]
            elif event.key == pg.K_ESCAPE:
                self.focused = False
            else:
                if event.unicode == '\r':
                    self.text = self.text[:self.caret_pos] + '\n' + self.text[self.caret_pos:]
                    self.caret_pos += 1
                elif event.unicode:
                    self.text = self.text[:self.caret_pos] + event.unicode + self.text[self.caret_pos:]
                    self.caret_pos += 1
