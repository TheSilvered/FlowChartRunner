from .constants import (
    INFO_BAR_WIDTH, PROPERTY_TEXTBOX_PADDING, PROPERTY_BORDER_COLOR, INFO_BAR_BG, INFO_BAR_ARROW_SELECTOR_PADDING,
    TEXTBOX_MIN_HEIGHT, TEXTBOX_PADDING
)
from .table import DictTable
from .constraint import *
from .container import Container, ContainerDirection, ContainerAlignment
from .textbox import TextBox
from text_rendering import mono_line_height
from language_manager import Language


class ContentTextBoxAdaptHeight(Constraint):
    def __init__(self, info_bar):
        self.info_bar = info_bar

    def apply(self, ui_comp: UIBaseComponent):
        bottom = pg.display.get_window_size()[1] - PROPERTY_TEXTBOX_PADDING
        if bottom - ui_comp.y >= TEXTBOX_MIN_HEIGHT:
            ui_comp.h = bottom - ui_comp.y
        else:
            ui_comp.h = TEXTBOX_MIN_HEIGHT


class InputTextBox(TextBox):
    def __init__(self, runner_bar):
        super().__init__(pg.Rect(0, 0, 0, mono_line_height() + TEXTBOX_PADDING * 2), "", single_line=True)
        self.add_constraint(MatchWidth(runner_bar))
        self.add_constraint(SizeDiff((-PROPERTY_TEXTBOX_PADDING * 2, 0)))
        self.disabled = True
        self.runner = runner_bar.runner

    def disable(self):
        self.focused = False
        self.disabled = True

    def enable(self):
        self.disabled = False

    def send(self):
        self.runner.queue_input_text(self.text)
        self.text = ""
        self.placeholder_text = ""
        self.disable()

    def handle_event(self, event: pg.event.Event) -> bool:
        if self.disabled:
            self.focused = False
            return False
        return super().handle_event(event)


class RunnerBar(UIBaseComponent):
    def __init__(self, runner, language: Language):
        super().__init__(pg.Rect(0, 0, INFO_BAR_WIDTH, 0))
        self.add_constraint(AnchorWindow(AnchorPoint.TR, AnchorPoint.TR))
        self.add_constraint(MatchWindowHeight())

        components = []

        self.runner = runner
        self.language = language

        self.symtable_table = DictTable((0, 0), INFO_BAR_WIDTH, self.runner.sym_table)
        self.symtable_table.add_constraint(MatchWidth(self))
        components.append(self.symtable_table)

        self.input_textbox = InputTextBox(self)
        self.input_textbox.disable()
        components.append(self.input_textbox)
        self.allow_input = False

        self._resizing = False
        self._resize_offset = 0
        self.y_offset = 0

        self.container = Container(
            pg.Rect(0, 0, 0, 0),
            components,
            ContainerDirection.TOP_TO_BOTTOM,
            ContainerAlignment.CENTER,
            INFO_BAR_ARROW_SELECTOR_PADDING
        )
        self.container.add_constraint(MatchX(self))
        self.container.add_constraint(MatchWidth(self))
        self.container.add_constraint(MatchSumHeights(components, self.container.padding))
        self.container.add_constraint(BindAttr(self, "y_offset", "y"))

    def handle_event(self, event: pg.event.Event) -> bool:
        if self.container.handle_event(event):
            return True
        elif event.type == pg.MOUSEWHEEL and self.rect.collidepoint(pg.mouse.get_pos()):
            self.y_offset += event.y * 15
            return True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT and self.x - 10 <= event.pos[0] <= self.x + 10:
                self._resizing = True
                self._resize_offset = event.pos[0] - self.x
                return True
            return self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONUP and event.button == pg.BUTTON_LEFT:
            self._resizing = False
        return False

    def __clamp_y_offset(self):
        if self.y_offset > 0:
            self.y_offset = 0
            return

        if -self.y_offset > self.container.h - self.h > 0:
            self.y_offset = -self.container.h + self.h
        elif self.container.h < self.h:
            self.y_offset = 0

    def _draw(self, screen, *args, **kwargs):
        if self._resizing:
            self.w = max(screen.get_width() - pg.mouse.get_pos()[0] + self._resize_offset, INFO_BAR_WIDTH)

        placeholder = self.runner.get_placeholder_text()
        if placeholder is not None:
            self.input_textbox.placeholder_text = placeholder
            self.input_textbox.enable()

        self.__clamp_y_offset()

        pg.draw.rect(screen, INFO_BAR_BG, self.rect)
        self.container.draw(screen)

        pg.draw.line(
            screen,
            PROPERTY_BORDER_COLOR,
            self.symtable_table.rect.bottomleft,
            self.symtable_table.rect.bottomright,
            2
        )
        pg.draw.line(screen, PROPERTY_BORDER_COLOR, (self.x - 2, 0), (self.x - 2, self.h), 2)
