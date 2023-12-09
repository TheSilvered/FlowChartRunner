import pygame as pg
from .constants import (
    TABLE_BG_LIGHT, TABLE_BG_DARK, TABLE_H_PADDING, TABLE_V_PADDING, PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH
)
from text_rendering import write_text, line_height


class Table:
    def __init__(self, pos, row_heights, col_widths, size=None):
        self.num_rows = len(row_heights)
        self.num_cols = len(col_widths)

        if size is None:
            size = (
                sum(col_widths) + TABLE_H_PADDING * 2 * self.num_cols,
                sum(row_heights) + TABLE_V_PADDING * 2 * self.num_rows
            )

        self.rect = pg.Rect(pos, size)
        self.data = [["" for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.col_widths = col_widths
        self.row_heights = row_heights

    def __getitem__(self, key):
        if isinstance(key, tuple) or isinstance(key, list):
            return self.data[key[0]][key[1]]
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key[0]][key[1]] = value

    def draw(self, screen):
        col_rects = []
        curr_x = self.rect.x
        for i in range(self.num_cols):
            rect = pg.Rect(curr_x, self.rect.y, self.col_widths[i] + TABLE_H_PADDING * 2, self.rect.h)
            col_rects.append(rect)
            curr_x += rect.w

        curr_y = self.rect.y
        for i, row in enumerate(self.data):
            row_rect = pg.Rect(self.rect.x, curr_y, self.rect.w, self.row_heights[i] + TABLE_V_PADDING * 2)
            curr_y += row_rect.h
            if i % 2 == 0:
                pg.draw.rect(screen, TABLE_BG_LIGHT, row_rect)
            else:
                pg.draw.rect(screen, TABLE_BG_DARK, row_rect)

            for j, col in enumerate(row):
                col_rect = col_rects[j]
                text_surf = write_text(col)
                text_rect = pg.Rect(0, 0, self.col_widths[j], self.row_heights[i])
                screen.blit(text_surf, (col_rect.x + TABLE_H_PADDING, row_rect.y + TABLE_V_PADDING), text_rect)


class DictTable(Table):
    def __init__(self, pos, dictionary: dict):
        super().__init__(pos, [line_height() * len(dictionary)], [PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH])
        self.dictionary = dictionary

    def draw(self, screen):
        self.data = list(self.dictionary.items())
        super().draw(screen)
