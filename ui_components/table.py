import pygame as pg
from .constants import (
    TABLE_BG_LIGHT, TABLE_BG_DARK, TABLE_H_PADDING, TABLE_V_PADDING, PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH
)
from text_rendering import write_mono_text, mono_line_height
from .base_component import UIBaseComponent
from .constraint import Constraint


class Table(UIBaseComponent):
    """
    pos: the position
    width: the width
    row_height: the height of one row in pixels
    col_widths: percentages number of units each column occupies (ex. (1, 2, 1) -> 25%, 50%, 25%)
    data: initial data of the table
    """
    def __init__(self, pos, width, row_height, col_widths, data=None):
        if data is None:
            data = []
        else:
            data = list(data)

        height = (row_height + TABLE_V_PADDING * 2) * len(data)
        super().__init__(pg.Rect(pos, (width, height)))
        self.add_constraint(UpdateTableHeight())

        tot_units = sum(col_widths)
        self.col_widths = [units / tot_units for units in col_widths]
        self.row_height = row_height
        self.num_cols = len(col_widths)
        self._data = [list(row) for row in data]

        for i, row in enumerate(data):
            if len(row) != self.num_cols:
                raise ValueError(f"row {i} with {len(row)} elements instead of {self.num_cols}")

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        data = [list(row) for row in value]
        for i, row in enumerate(data):
            if len(row) != self.num_cols:
                raise ValueError(f"row {i} with {len(row)} instead of {self.num_cols}")
        self._data = data

    def __getitem__(self, key):
        if isinstance(key, tuple) or isinstance(key, list):
            return self.data[key[0]][key[1]]
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key[0]][key[1]] = value

    def handle_event(self, event: pg.event.Event) -> bool:
        return False

    def __true_widths(self):
        return [self.w * w for w in self.col_widths]

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        col_rects = []
        curr_x = self.x
        col_widths = self.__true_widths()
        for i in range(self.num_cols):
            rect = pg.Rect(curr_x, self.y, col_widths[i] + TABLE_H_PADDING * 2, self.h)
            col_rects.append(rect)
            curr_x += rect.w

        curr_y = self.y
        for i, row in enumerate(self.data):
            row_rect = pg.Rect(self.x, curr_y, self.w, self.row_height + TABLE_V_PADDING * 2)
            curr_y += row_rect.h
            if i % 2 == 0:
                pg.draw.rect(screen, TABLE_BG_LIGHT, row_rect)
            else:
                pg.draw.rect(screen, TABLE_BG_DARK, row_rect)

            for j, col in enumerate(row):
                col_rect = col_rects[j]
                text_surf = write_mono_text(str(col))
                text_rect = pg.Rect(0, 0, col_widths[j], self.row_height)
                screen.blit(text_surf, (col_rect.x + TABLE_H_PADDING, row_rect.y + TABLE_V_PADDING), text_rect)


class UpdateTableHeight(Constraint):
    def apply(self, ui_comp: Table):
        ui_comp.h = len(ui_comp.data) * (ui_comp.row_height + TABLE_V_PADDING * 2)


class DictTable(Table):
    def __init__(self, pos, width, dictionary: dict):
        super().__init__(
            pos,
            width,
            mono_line_height(),
            [PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH],
            dictionary.items()
        )
        self.dictionary = dictionary

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        self.data = list(self.dictionary.items())
        super()._draw(screen)
