from .blocks import *
from .constants import (
    PROPERTY_VALUE_COL_WIDTH, INFO_BAR_WIDTH, PROPERTY_H_PADDING, PROPERTY_V_PADDING, PROPERTY_TEXTBOX_PADDING,
    INFO_BG_DARK, INFO_BG_LIGHT, PROPERTY_BORDER_COLOR, INFO_BAR_ARROW_SELECTOR_PADDING
)
from .textbox import TextBox
from .arrow_point_selector import ArrowPointSelector


class InfoBar:
    def __init__(self, block: BlockBase):
        self.block = block
        self.tb_content = None
        self.arrows_in_selector = None
        self.arrow1_out_selector = None
        self.arrow2_out_selector = None

        if not isinstance(block, StartBlock):
            self.arrows_in_selector = ArrowPointSelector(block.in_point, inward=True)

        if not isinstance(block, CondBlock) and not isinstance(block, EndBlock):
            self.arrow1_out_selector = ArrowPointSelector(block.out_point, inward=False)
        elif isinstance(block, CondBlock):
            self.arrow1_out_selector = ArrowPointSelector(block.on_true.out_point, inward=False)
            self.arrow2_out_selector = ArrowPointSelector(block.on_false.out_point, inward=False)

        self.__link_selectors()

        self._properties = [
            ("Type", self.block.__class__.__name__),
            ("Position", f"x: {self.block.pos.x}, y: {self.block.pos.y}"),
            ("Size", f"w: {self.block.get_size()[0]}, h: {self.block.get_size()[1]}"),
        ]

        if block.editable:
            self.tb_content: TextBox | None = TextBox(
                pg.Rect(
                    0, 0,
                    INFO_BAR_WIDTH - PROPERTY_TEXTBOX_PADDING * 2, 150
                ),
                "Insert contents..."
            )
            self.tb_content.set_text(block.content)
        else:
            self.tb_content: TextBox | None = None

    def __eq__(self, other):
        return id(self.block) == id(other)

    def __link_selectors(self):
        selectors = []
        if self.arrows_in_selector is not None:
            selectors.append(self.arrows_in_selector)
        if self.arrow1_out_selector is not None:
            selectors.append(self.arrow1_out_selector)
        if self.arrow2_out_selector is not None:
            selectors.append(self.arrow2_out_selector)
        for selector in selectors:
            for link in selectors:
                if link is selector:
                    continue
                selector.link_selector(link)

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and self.tb_content is not None and not self.tb_content.focused:
            if self.tb_content.rect.collidepoint(event.pos):
                self.tb_content.focused = True
                return True
        elif event.type == pg.MOUSEBUTTONUP and self.tb_content is not None and self.tb_content.focused:
            if not self.tb_content.rect.collidepoint(event.pos):
                self.tb_content.focused = False

        if self.tb_content is not None and self.tb_content.focused and self.tb_content.handle_event(event):
            return True

        if self.arrows_in_selector is not None and self.arrows_in_selector.handle_event(event):
            return True
        if self.arrow1_out_selector is not None and self.arrow1_out_selector.handle_event(event):
            return True
        if self.arrow2_out_selector is not None and self.arrow2_out_selector.handle_event(event):
            return True

        if event.type == pg.MOUSEBUTTONDOWN and pg.display.get_window_size()[0] - event.pos[0] <= INFO_BAR_WIDTH:
            return True

        return False

    def draw(self, screen):
        if self.tb_content is not None:
            self.block.content = self.tb_content.text
        if self.arrows_in_selector is not None:
            self.block.in_point = self.arrows_in_selector.direction
        if self.arrow1_out_selector is not None and self.arrow2_out_selector is None:
            self.block.out_point = self.arrow1_out_selector.direction
        elif self.arrow1_out_selector is not None and self.arrow2_out_selector is not None:
            self.block: CondBlock
            self.block.on_true.out_point = self.arrow1_out_selector.direction
            self.block.on_false.out_point = self.arrow2_out_selector.direction

        screen_w = screen.get_width()
        screen_h = screen.get_height()

        rect_x = screen_w - INFO_BAR_WIDTH
        screen_h = screen_h
        pg.draw.rect(screen, INFO_BG_DARK, pg.Rect(rect_x, 0, INFO_BAR_WIDTH, screen_h))

        self.__draw_properties(screen)
        self.__draw_point_selectors(screen)

        if self.tb_content is not None:
            self.tb_content.rect.right = screen_w - PROPERTY_TEXTBOX_PADDING
            self.tb_content.rect.bottom = screen_h - PROPERTY_TEXTBOX_PADDING
            self.tb_content.draw(screen)

        pg.draw.line(screen, PROPERTY_BORDER_COLOR, (rect_x - 2, 0), (rect_x - 2, screen_h), 2)

    @staticmethod
    def __draw_one_selector(screen, name, selector, current_y):
        screen.blit(
            write_text(name),
            (screen.get_width() - INFO_BAR_WIDTH + INFO_BAR_ARROW_SELECTOR_PADDING, current_y)
        )
        current_y += INFO_BAR_ARROW_SELECTOR_PADDING * 2 + line_height()
        selector.pos = (
            screen.get_width() - INFO_BAR_WIDTH // 2 - selector.size[0] // 2,
            current_y
        )
        selector.draw(screen)
        return current_y + selector.size[1] + INFO_BAR_ARROW_SELECTOR_PADDING

    @staticmethod
    def __draw_two_selectors(screen, name1, name2, selector1, selector2, current_y):
        screen.blit(
            write_text(name1),
            (screen.get_width() - INFO_BAR_WIDTH + INFO_BAR_ARROW_SELECTOR_PADDING, current_y)
        )
        screen.blit(
            write_text(name2),
            (screen.get_width() - INFO_BAR_WIDTH // 2 + INFO_BAR_ARROW_SELECTOR_PADDING, current_y)
        )
        current_y += INFO_BAR_ARROW_SELECTOR_PADDING * 2 + line_height()
        selector1.pos = (
            screen.get_width() - int(INFO_BAR_WIDTH * (3/4)) - selector1.size[0] // 2,
            current_y
        )
        selector1.draw(screen)

        selector2.pos = (
            screen.get_width() - int(INFO_BAR_WIDTH * (1/4)) - selector2.size[0] // 2,
            current_y
        )
        selector2.draw(screen)

        return current_y + selector1.size[1] + INFO_BAR_ARROW_SELECTOR_PADDING

    def __draw_point_selectors(self, screen):
        current_y = len(self._properties) * (line_height() + PROPERTY_V_PADDING * 2)
        current_y += INFO_BAR_ARROW_SELECTOR_PADDING

        if self.arrows_in_selector is not None:
            current_y = self.__draw_one_selector(screen, "Arrows-in point:", self.arrows_in_selector, current_y)

        if self.arrow1_out_selector is not None and self.arrow2_out_selector is None:
            self.__draw_one_selector(screen, "Arrow-out point:", self.arrow1_out_selector, current_y)
        elif self.arrow1_out_selector is not None and self.arrow2_out_selector is not None:
            self.__draw_two_selectors(
                screen,
                "True point:", "False point:",
                self.arrow1_out_selector, self.arrow2_out_selector,
                current_y
            )

    def __draw_properties(self, screen):
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        property_name_col = pg.Rect(
            screen_w - INFO_BAR_WIDTH, 0,
            INFO_BAR_WIDTH - PROPERTY_VALUE_COL_WIDTH, screen_h)
        property_value_col = pg.Rect(
            screen_w - PROPERTY_VALUE_COL_WIDTH, 0,
            PROPERTY_VALUE_COL_WIDTH, screen_h)
        lh = line_height() + PROPERTY_V_PADDING * 2

        self._properties = [
            ("Type", self.block.__class__.__name__),
            ("Position", f"x: {self.block.pos.x}, y: {self.block.pos.y}"),
            ("Size", f"w: {self.block.get_size()[0]}, h: {self.block.get_size()[1]}"),
        ]

        for i, (p_name, p_val) in enumerate(self._properties):
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
