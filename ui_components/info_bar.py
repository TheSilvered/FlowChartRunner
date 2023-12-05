from .blocks import *
from .constants import (
    PROPERTY_VALUE_COL_WIDTH, INFO_BAR_WIDTH, PROPERTY_H_PADDING, PROPERTY_V_PADDING, PROPERTY_TEXTBOX_PADDING,
    INFO_BG_DARK, INFO_BG_LIGHT, PROPERTY_BORDER_COLOR, INFO_BAR_ARROW_SELECTOR_PADDING, TEXTBOX_MIN_HEIGHT
)
from .textbox import TextBox
from .arrow_point_selector import ArrowPointSelector
from language_manager import Language


class InfoBar:
    def __init__(self, block: BlockBase, language: Language):
        self.block = block
        self.tb_content = None
        self.arrows_in_selector = None
        self.arrow1_out_selector = None
        self.arrow2_out_selector = None
        self.language = language
        self.y_offset = 0

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
                    INFO_BAR_WIDTH - PROPERTY_TEXTBOX_PADDING * 2, TEXTBOX_MIN_HEIGHT
                ),
                self.language.info.content_textbox.placeholder
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
        if event.type == pg.MOUSEBUTTONDOWN \
           and event.button == pg.BUTTON_LEFT \
           and self.tb_content is not None \
           and not self.tb_content.focused:
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

        if event.type == pg.MOUSEWHEEL and pg.display.get_window_size()[0] - pg.mouse.get_pos()[0] <= INFO_BAR_WIDTH:
            self.y_offset += event.y * 15
            return True

        if event.type == pg.MOUSEBUTTONDOWN and pg.display.get_window_size()[0] - event.pos[0] <= INFO_BAR_WIDTH:
            return True

        return False

    def __get_ui_height(self):
        height = self.__property_table_height() + self.__arrow_point_selector_height()
        height += TEXTBOX_MIN_HEIGHT + PROPERTY_TEXTBOX_PADDING if self.tb_content is not None else 0
        return height

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

        if self.y_offset > 0:
            self.y_offset = 0
        elif -self.y_offset > self.__get_ui_height() - screen_h > 0:
            self.y_offset = -self.__get_ui_height() + screen_h
        elif self.__get_ui_height() < screen_h:
            self.y_offset = 0

        current_y = self.y_offset
        current_y = self.__draw_properties(screen, current_y)
        current_y = self.__draw_point_selectors(screen, current_y)

        if self.tb_content is not None:
            new_height = screen_h - current_y - PROPERTY_TEXTBOX_PADDING
            self.tb_content.rect.h = max(TEXTBOX_MIN_HEIGHT, new_height)

            self.tb_content.rect.right = screen_w - PROPERTY_TEXTBOX_PADDING
            self.tb_content.rect.top = current_y
            self.tb_content.draw(screen)

        # pg.draw.line(screen, (255, 0, 255), (screen_w - INFO_BAR_WIDTH, self.__get_ui_height()),
        # (screen_w, self.__get_ui_height()))

        pg.draw.line(screen, PROPERTY_BORDER_COLOR, (rect_x - 2, 0), (rect_x - 2, screen_h), 2)

    @staticmethod
    def __draw_one_selector(screen, name, selector, current_y):
        screen.blit(
            write_text(name, "center", INFO_BAR_WIDTH),
            (screen.get_width() - INFO_BAR_WIDTH, current_y)
        )
        current_y += INFO_BAR_ARROW_SELECTOR_PADDING * 2 + line_height()
        selector.pos = (
            screen.get_width() - INFO_BAR_WIDTH // 2 - selector.size[0] // 2,
            current_y
        )
        selector.draw(screen)
        return current_y + selector.size[1] + INFO_BAR_ARROW_SELECTOR_PADDING

    @staticmethod
    def __draw_two_selectors(screen, title, name1, name2, selector1, selector2, current_y):
        screen.blit(
            write_text(title, "center", INFO_BAR_WIDTH),
            (screen.get_width() - INFO_BAR_WIDTH, current_y)
        )
        current_y += INFO_BAR_ARROW_SELECTOR_PADDING * 2 + line_height()
        screen.blit(
            write_text(name1, "center", INFO_BAR_WIDTH // 2),
            (screen.get_width() - INFO_BAR_WIDTH, current_y)
        )
        screen.blit(
            write_text(name2, "center", INFO_BAR_WIDTH // 2),
            (screen.get_width() - INFO_BAR_WIDTH // 2, current_y)
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

    @staticmethod
    def __arrow_point_selector_line_height():
        return line_height() + INFO_BAR_ARROW_SELECTOR_PADDING * 2

    def __arrow_point_selector_height(self):
        if self.arrows_in_selector is not None and self.arrow1_out_selector is None:
            return self.arrows_in_selector.size[1] \
                 + self.__arrow_point_selector_line_height() \
                 + INFO_BAR_ARROW_SELECTOR_PADDING * 2
        elif self.arrows_in_selector is None and self.arrow1_out_selector is not None:
            return self.arrow1_out_selector.size[1] \
                 + self.__arrow_point_selector_line_height() \
                 + INFO_BAR_ARROW_SELECTOR_PADDING * 2
        elif self.arrow1_out_selector is not None and self.arrow2_out_selector is None:
            return self.arrows_in_selector.size[1] \
                 + self.arrow1_out_selector.size[1] \
                 + self.__arrow_point_selector_line_height() * 2 \
                 + INFO_BAR_ARROW_SELECTOR_PADDING * 5
        elif None not in (self.arrows_in_selector, self.arrow1_out_selector, self.arrow1_out_selector):
            return self.arrows_in_selector.size[1] \
                 + self.arrow1_out_selector.size[1] \
                 + self.__arrow_point_selector_line_height() * 3 \
                 + INFO_BAR_ARROW_SELECTOR_PADDING * 5
        else:
            return 0

    def __draw_point_selectors(self, screen, current_y):
        current_y += INFO_BAR_ARROW_SELECTOR_PADDING

        if self.arrows_in_selector is not None:
            current_y = self.__draw_one_selector(
                screen,
                self.language.info.in_point_selector.name,
                self.arrows_in_selector,
                current_y
            )

        if self.arrow1_out_selector is not None and self.arrow2_out_selector is None:
            if self.arrows_in_selector is not None:
                current_y += INFO_BAR_ARROW_SELECTOR_PADDING * 2
            current_y = self.__draw_one_selector(
                screen,
                self.language.info.out_point_selector.name,
                self.arrow1_out_selector,
                current_y
            )
        elif self.arrow1_out_selector is not None and self.arrow2_out_selector is not None:
            if self.arrows_in_selector is not None:
                current_y += INFO_BAR_ARROW_SELECTOR_PADDING * 2
            current_y = self.__draw_two_selectors(
                screen,
                self.language.info.out_point_selectors.name,
                self.language.info.true_out_point_selector.name,
                self.language.info.false_out_point_selector.name,
                self.arrow1_out_selector, self.arrow2_out_selector,
                current_y
            )

        return current_y

    @staticmethod
    def __property_line_height():
        return line_height() + PROPERTY_V_PADDING * 2

    def __property_table_height(self):
        return self.__property_line_height() * len(self._properties)

    def __block_name(self):
        return self.language[self.block.__class__.__name__].name

    def __draw_properties(self, screen, current_y):
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
            (
                self.language.info.type.name,
                self.language.info.type.value.format(name=self.__block_name())
            ), (
                self.language.info.position.name,
                self.language.info.position.value.format(x=self.block.pos.x, y=self.block.pos.y)
            ), (
                self.language.info.size.name,
                self.language.info.size.value.format(w=self.block.get_size()[0], h=self.block.get_size()[1])
            )
        ]

        for i, (p_name, p_val) in enumerate(self._properties):
            line_rect = pg.Rect(property_name_col.x, lh * i + current_y, property_name_col.w + property_value_col.w, lh)
            if i % 2 == 0:
                pg.draw.rect(screen, INFO_BG_LIGHT, line_rect)
            else:
                pg.draw.rect(screen, INFO_BG_DARK, line_rect)

            p_name_surf = write_text(p_name)
            p_val_surf = write_text(p_val)
            p_name_rect = pg.Rect(0, 0, property_name_col.w, lh)
            p_val_rect = pg.Rect(0, 0, property_value_col.w, lh)
            screen.blit(
                p_name_surf,
                (property_name_col.x + PROPERTY_H_PADDING, lh * i + PROPERTY_V_PADDING + current_y),
                p_name_rect
            )
            screen.blit(
                p_val_surf,
                (property_value_col.x + PROPERTY_H_PADDING, lh * i + PROPERTY_V_PADDING + current_y),
                p_val_rect
            )

        return current_y + lh * len(self._properties) + PROPERTY_V_PADDING
