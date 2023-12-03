from blocks import *
from constants import (
    PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH, PROPERTY_H_PADDING, PROPERTY_V_PADDING,
    INFO_BG_DARK, INFO_BG_LIGHT
)
from textbox import TextBox


class InfoBar:
    def __init__(self, block: BlockBase):
        self.block = block
        if block.editable:
            self.tb_content: TextBox | None = TextBox(pg.Rect(
                0, 0,
                PROPERTY_NAME_COL_WIDTH + PROPERTY_VALUE_COL_WIDTH, 300
            ))
            self.tb_content.set_text(block.content)
        else:
            self.tb_content: TextBox | None = None

    def __eq__(self, other):
        return id(self.block) == id(other)

    def handle_event(self, event: pg.event.Event) -> bool:
        if self.tb_content is None:
            return False

        if event.type == pg.MOUSEBUTTONDOWN and not self.tb_content.focused:
            if self.tb_content.rect.collidepoint(event.pos):
                self.tb_content.focused = True
                return True
        elif self.tb_content.focused:
            return self.tb_content.handle_event(event)
        return False

    def draw(self, screen):
        if self.tb_content is not None:
            self.block.content = self.tb_content.text

        self.__draw_properties(screen)
        if self.tb_content is not None:
            self.tb_content.rect.right = screen.get_width()
            self.tb_content.rect.bottom = screen.get_height()
            self.tb_content.draw(screen)

    def __draw_properties(self, screen):
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        property_name_col = pg.Rect(
            screen_w - PROPERTY_NAME_COL_WIDTH - PROPERTY_VALUE_COL_WIDTH, 0,
            PROPERTY_NAME_COL_WIDTH, screen_h)
        property_value_col = pg.Rect(
            screen_w - PROPERTY_VALUE_COL_WIDTH, 0,
            PROPERTY_VALUE_COL_WIDTH, screen_h)
        lh = line_height() + PROPERTY_V_PADDING * 2

        properties = [
            ("Type", self.block.__class__.__name__),
            ("Position", f"x: {self.block.pos.x}, y: {self.block.pos.y}"),
            ("Size", f"w: {self.block.get_size()[0]}, h: {self.block.get_size()[1]}"),
        ]

        for i, (p_name, p_val) in enumerate(properties):
            line_rect = pg.Rect(property_name_col.x, lh * i, property_name_col.w + property_value_col.w, lh)
            if i % 2 == 0:
                pg.draw.rect(screen, INFO_BG_DARK, line_rect)
            else:
                pg.draw.rect(screen, INFO_BG_LIGHT, line_rect)

            p_name_surf = write_text(p_name)
            p_val_surf = write_text(p_val)
            p_name_rect = pg.Rect(0, 0, property_name_col.w, lh)
            p_val_rect = pg.Rect(0, 0, property_value_col.w, lh)
            screen.blit(
                p_name_surf,
                (property_name_col.x + PROPERTY_H_PADDING, lh * i + PROPERTY_V_PADDING),
                p_name_rect
            )
            screen.blit(
                p_val_surf,
                (property_value_col.x + PROPERTY_H_PADDING, lh * i + PROPERTY_V_PADDING),
                p_val_rect
            )

        pg.draw.rect(
            surface=screen,
            color=BLOCK_BORDER_COLOR,
            rect=pg.Rect(
                property_name_col.x - 2, -2,
                PROPERTY_NAME_COL_WIDTH + PROPERTY_VALUE_COL_WIDTH + 4, len(properties) * lh + 4),
            width=2
        )
