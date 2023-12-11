from .blocks import *
from text_rendering import mono_line_height
from .constants import (
    PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH, INFO_BAR_WIDTH, PROPERTY_TEXTBOX_PADDING, PROPERTY_BORDER_COLOR,
    INFO_BAR_BG, INFO_BAR_ARROW_SELECTOR_PADDING, TEXTBOX_MIN_HEIGHT
)
from .textbox import TextBox
from .arrow_point_selector import ArrowPointSelector
from language_manager import Language
from .table import Table
from .constraint import *
from .container import Container, ContainerDirection, ContainerAlignment


class InfoBar(UIBaseComponent):
    def __init__(self, block: BlockBase, language: Language):
        super().__init__(pg.Rect(0, 0, INFO_BAR_WIDTH, 0))
        self.add_constraint(AnchorWindow(AnchorPoint.TR, AnchorPoint.TR)) \
            .add_constraint(MatchWindowHeight())

        components = []

        self.block = block
        self.tb_content = None
        self.arrows_in_selector = None
        self.arrow1_out_selector = None
        self.arrow2_out_selector = None
        self.language = language
        self.y_offset = 0

        if isinstance(block, IOBlock):
            self.table = Table((0, 0), [mono_line_height()] * 4, [PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH])
            self.table[3, 0] = self.language.info.input.name
        else:
            self.table = Table((0, 0), [mono_line_height()] * 3, [PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH])
        self.table[0, 0] = self.language.info.type.name
        self.table[1, 0] = self.language.info.position.name
        self.table[2, 0] = self.language.info.size.name

        components.append(self.table)

        if isinstance(block, IOBlock):
            self.table[3, 0] = self.language.info.input.name

        if not isinstance(block, StartBlock):
            components.append(TextLabel((0, 0), language.info.in_point_selector.name, ui_font=True))
            self.arrows_in_selector = ArrowPointSelector(block.in_point, inward=True)
            components.append(self.arrows_in_selector)

        if not isinstance(block, CondBlock) and not isinstance(block, EndBlock):
            components.append(TextLabel((0, 0), language.info.out_point_selector.name, ui_font=True))
            self.arrow1_out_selector = ArrowPointSelector(block.out_point, inward=False)
            components.append(self.arrow1_out_selector)
        elif isinstance(block, CondBlock):
            components.append(TextLabel((0, 0), language.info.out_point_selectors.name, ui_font=True))
            self.arrow1_out_selector = ArrowPointSelector(block.on_true.out_point, inward=False)
            self.arrow2_out_selector = ArrowPointSelector(block.on_false.out_point, inward=False)
            true_label = TextLabel((0, 0), language.info.true_out_point_selector.name, ui_font=True)
            false_label = TextLabel((0, 0), language.info.false_out_point_selector.name, ui_font=True)
            true_container = Container(
                pg.Rect(0, 0, 0, 0),
                [true_label, self.arrow1_out_selector],
                ContainerDirection.TOP_TO_BOTTOM,
                ContainerAlignment.CENTER,
                INFO_BAR_ARROW_SELECTOR_PADDING
            )
            (true_container
                .add_constraint(MatchMaxWidth(true_container.components))
                .add_constraint(MatchSumHeights(true_container.components, true_container.padding)))
            false_container = Container(
                pg.Rect(0, 0, 0, 0),
                [false_label, self.arrow2_out_selector],
                ContainerDirection.TOP_TO_BOTTOM,
                ContainerAlignment.CENTER,
                INFO_BAR_ARROW_SELECTOR_PADDING
            )
            (false_container
                .add_constraint(MatchMaxWidth(false_container.components))
                .add_constraint(MatchSumHeights(false_container.components, false_container.padding)))
            arrows_out_container = Container(
                pg.Rect(0, 0, 0, 0),
                [true_container, false_container],
                ContainerDirection.H_SPACED_LR,
                ContainerAlignment.CENTER
            )
            (arrows_out_container
                .add_constraint(MatchWidth(self))
                .add_constraint(MatchMaxHeight(arrows_out_container.components)))
            components.append(arrows_out_container)

        self.__link_selectors()

        self.container = Container(
            pg.Rect(0, 0, 0, 0),
            components,
            ContainerDirection.TOP_TO_BOTTOM,
            ContainerAlignment.CENTER,
            INFO_BAR_ARROW_SELECTOR_PADDING
        )
        (self.container
            .add_constraint(MatchX(self))
            .add_constraint(MatchWidth(self))
            .add_constraint(MatchSumHeights(components, self.container.padding)))

        if block.editable:
            self.tb_content: TextBox | None = TextBox(
                pg.Rect(0, 0, INFO_BAR_WIDTH - PROPERTY_TEXTBOX_PADDING * 2, TEXTBOX_MIN_HEIGHT),
                self.language.info.content_textbox.placeholder,
                on_update=self.__update_block_text,
                on_update_args=(self.block,)
            )
            self.tb_content.set_text(block.content.text)
            (self.tb_content
                .add_constraint(Anchor(self.container, AnchorPoint.BC, AnchorPoint.TC))
                .add_constraint(Offset((0, PROPERTY_TEXTBOX_PADDING)))
                .add_constraint(MatchWidth(self))
                .add_constraint(SizeDiff((-PROPERTY_TEXTBOX_PADDING * 2, 0))))
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

    @staticmethod
    def __update_block_text(textbox, block):
        block.content.text = textbox.text

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN \
           and event.button == pg.BUTTON_LEFT \
           and self.tb_content is not None \
           and not self.tb_content.focused:
            if self.tb_content.rect.collidepoint(event.pos):
                self.tb_content.focused = True
                return True

        if self.tb_content is not None and self.tb_content.focused:
            if self.tb_content.handle_event(event):
                return True
            elif event.type == pg.MOUSEBUTTONUP:
                self.tb_content.focused = False

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
        if self.tb_content is None:
            return self.container.h
        return self.container.h + TEXTBOX_MIN_HEIGHT + PROPERTY_TEXTBOX_PADDING

    def _draw(self, screen, *args, **kwargs):
        if self.arrows_in_selector is not None:
            self.block.in_point = self.arrows_in_selector.direction
        if self.arrow1_out_selector is not None and self.arrow2_out_selector is None:
            self.block.out_point = self.arrow1_out_selector.direction
        elif self.arrow1_out_selector is not None and self.arrow2_out_selector is not None:
            self.block: CondBlock
            self.block.on_true.out_point = self.arrow1_out_selector.direction
            self.block.on_false.out_point = self.arrow2_out_selector.direction
        self.__update_table_values()

        if self.y_offset > 0:
            self.y_offset = 0
        elif -self.y_offset > self.__get_ui_height() - self.h > 0:
            self.y_offset = -self.__get_ui_height() + self.h
        elif self.__get_ui_height() < self.h:
            self.y_offset = 0

        self.container.y = self.y_offset

        pg.draw.rect(screen, INFO_BAR_BG, self.rect)
        self.container.draw(screen)
        pg.draw.line(screen, PROPERTY_BORDER_COLOR, self.table.rect.bottomleft, self.table.rect.bottomright, 2)

        if self.tb_content is not None:
            new_height = self.rect.bottom - self.container.rect.bottom - PROPERTY_TEXTBOX_PADDING * 2
            self.tb_content.h = max(TEXTBOX_MIN_HEIGHT, new_height)
            self.tb_content.draw(screen)

        pg.draw.line(screen, PROPERTY_BORDER_COLOR, (self.x - 2, 0), (self.x - 2, self.h), 2)

    def __block_name(self):
        return self.language[self.block.__class__.__name__].name

    def __update_table_values(self):
        self.table[0, 1] = self.language.info.type.value.format(name=self.__block_name())
        self.table[1, 1] = self.language.info.position.value.format(x=self.block.pos.x, y=self.block.pos.y)
        self.table[2, 1] = self.language.info.size.value.format(
            w=self.block.w,
            h=self.block.h
        )

        if isinstance(self.block, IOBlock):
            if self.block.is_input:
                self.table[3, 1] = self.language.info.input.value_true
            else:
                self.table[3, 1] = self.language.info.input.value_false
