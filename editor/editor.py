from ui_components import StartBlock, EndBlock, BlockBase, IOBlock, CondBlock, InitBlock, CalcBlock, BlockState
from ui_components.blocks import Pos, _OptionBlock
from .constants import GUIDELINE_COLOR, AXIS_COLOR, EDITOR_BG_COLOR, SELECTION_BORDER_COLOR
from text_rendering import line_height
from ui_components import InfoBar, draw_arrows
import pygame as pg


class Editor:
    def __init__(self, language):
        self.start_block = StartBlock(language.StartBlock.content)
        end_block = EndBlock(self.start_block, language.EndBlock.content)
        self.langauge = language

        self.start_block.pos = [0, 0]
        end_block_x = (self.start_block.get_size()[0] - end_block.get_size()[0]) / 2 + self.start_block.pos[0]
        end_block.pos = [end_block_x, self.start_block.get_size()[1] + line_height() * 3]

        self.blocks: list[BlockBase] = [self.start_block, end_block]
        self.dragging_blocks: list[BlockBase] | None = None
        self.has_moved = False
        self.dragging_global = False
        self.selecting = False
        self._pending_next_block = None
        self.fake_pending_next_block = None
        self.executing = False
        self.select_start = (0, 0)
        self.select_area = pg.Rect(-1, -1, 0, 0)
        self.selected_blocks: list[BlockBase] = []
        self.global_offset = [0, 0]
        self.info_bar: InfoBar | None = None

    @property
    def pending_next_block(self):
        return self._pending_next_block

    @pending_next_block.setter
    def pending_next_block(self, value):
        self._pending_next_block = value
        self.fake_pending_next_block = value

    def intersect_point(self, point) -> BlockBase | None:
        point = list(Pos(*point) - self.global_offset)
        for b in reversed(self.blocks):
            if b.rect.collidepoint(point):
                return b
        return None

    def intersect_all_point(self, point) -> list[BlockBase]:
        blocks = []
        point = list(Pos(*point) - self.global_offset)
        for b in reversed(self.blocks):
            if b.rect.collidepoint(point):
                blocks.append(b)
        return blocks

    def intersect_rect(self, rect: pg.Rect) -> BlockBase | None:
        rect.x -= self.global_offset[0]
        rect.y -= self.global_offset[1]
        for b in reversed(self.blocks):
            if b.inside(rect):
                return b
        return None

    def intersect_all_rect(self, rect: pg.Rect) -> list[BlockBase]:
        blocks = []
        rect.x -= self.global_offset[0]
        rect.y -= self.global_offset[1]
        for b in self.blocks:
            if b.inside(rect):
                blocks.append(b)
        return blocks

    def update_select_area(self):
        mp = pg.mouse.get_pos()
        self.select_area = pg.Rect(
            min(self.select_start[0], mp[0]),
            min(self.select_start[1], mp[1]),
            abs(self.select_start[0] - mp[0]),
            abs(self.select_start[1] - mp[1])
        )

    def __handle_mouse_button_down_event(self, event):
        if event.button == pg.BUTTON_RIGHT:
            self.dragging_global = True
            self.pending_next_block = None
            return
        elif event.button != pg.BUTTON_LEFT:
            return

        block = self.intersect_point(event.pos)
        if block is not None:
            if self.pending_next_block is not None:
                if not isinstance(block, StartBlock):
                    self.pending_next_block.next_block = block
                self.pending_next_block = None
                return

            if block not in self.selected_blocks:
                self.selected_blocks = [block]
            self.dragging_blocks = self.selected_blocks
            return
        self.selected_blocks = []
        self.selecting = True
        self.select_start = event.pos
        self.select_area = pg.Rect(event.pos, (0, 0))
        self.pending_next_block = None

    def __handle_mouse_button_up_event(self, event):
        self.pending_next_block = None
        if event.button == pg.BUTTON_RIGHT:
            self.dragging_global = False
            return
        elif event.button != pg.BUTTON_LEFT:
            return

        if self.selecting:
            self.selected_blocks = self.intersect_all_rect(self.select_area)
        elif not self.has_moved:
            block = self.intersect_point(event.pos)
            if block is not None:
                self.selected_blocks = [block]
        self.selecting = False
        self.dragging_blocks = None
        self.has_moved = False

    def __handle_mouse_motion_event(self, event):
        if self.dragging_blocks is not None:
            self.has_moved = True
            for block in self.dragging_blocks:
                block.add_pos(event.rel)
        elif self.dragging_global:
            self.global_offset[0] += event.rel[0]
            self.global_offset[1] += event.rel[1]
        elif self.selecting:
            self.update_select_area()

    def handle_event(self, event: pg.event.Event):
        if self.info_bar is not None and self.info_bar.handle_event(event):
            self.pending_next_block = None
            return

        if event.type == pg.MOUSEBUTTONDOWN:
            self.__handle_mouse_button_down_event(event)
        elif event.type == pg.MOUSEBUTTONUP:
            self.__handle_mouse_button_up_event(event)
        elif event.type == pg.MOUSEMOTION:
            self.__handle_mouse_motion_event(event)
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_i:
                input_block = IOBlock(None, "", True)
                self.blocks.append(input_block)
            elif event.key == pg.K_o:
                output_block = IOBlock(None, "", False)
                self.blocks.append(output_block)
            elif event.key == pg.K_c:
                cond_block = CondBlock(
                    None, "",
                    self.langauge.CondBlock.true_branch.name,
                    self.langauge.CondBlock.false_branch.name
                )
                self.blocks.append(cond_block)
            elif event.key == pg.K_n:
                calc_block = CalcBlock(None, "")
                self.blocks.append(calc_block)
            elif event.key == pg.K_v:
                var_block = InitBlock(None, "")
                self.blocks.append(var_block)
            elif event.key == pg.K_w and len(self.selected_blocks) == 1:
                self.pending_next_block = self.selected_blocks[0]
                if isinstance(self.selected_blocks[0], EndBlock) or isinstance(self.selected_blocks[0], CondBlock):
                    self.pending_next_block = None
                else:
                    self.selected_blocks = []
            elif event.key == pg.K_t and len(self.selected_blocks) == 1:
                if not isinstance(self.selected_blocks[0], CondBlock):
                    return
                self.pending_next_block = self.selected_blocks[0].on_true
                self.fake_pending_next_block = self.selected_blocks[0]
                self.selected_blocks = []
            elif event.key == pg.K_f and len(self.selected_blocks) == 1:
                if not isinstance(self.selected_blocks[0], CondBlock):
                    return
                self.pending_next_block = self.selected_blocks[0].on_false
                self.fake_pending_next_block = self.selected_blocks[0]
                self.selected_blocks = []
            elif event.key in (pg.K_DELETE, pg.K_BACKSPACE):
                if len(self.selected_blocks) == 1:
                    self.delete_block(self.selected_blocks[0])
                elif self.pending_next_block is not None:
                    self.pending_next_block.next_block = None
                    self.pending_next_block = None
            elif event.key == pg.K_r:
                pass

    def delete_block(self, block):
        # These blocks cannot be deleted
        if isinstance(block, StartBlock) or isinstance(block, EndBlock) or isinstance(block, _OptionBlock):
            return

        for b in self.blocks:
            try:
                if block is b.next_block:
                    b.next_block = None
            except ValueError:
                b: CondBlock
                if block is b.on_true.next_block:
                    b.on_true.next_block = None
                if block is b.on_false.next_block:
                    b.on_false.next_block = None

        self.blocks.remove(block)
        self.selected_blocks.pop()

    def __update_info_bar(self):
        if len(self.selected_blocks) != 1:
            self.info_bar = None
        elif self.info_bar != self.selected_blocks[0]:
            self.info_bar = InfoBar(self.selected_blocks[0], self.langauge)

    def __draw_background_grid(self, screen):
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        offset_x = self.global_offset[0] % 50
        offset_y = self.global_offset[1] % 50
        if 0 <= self.global_offset[1] <= screen_w:
            pg.draw.line(screen, AXIS_COLOR, (0, self.global_offset[1]), (screen_w, self.global_offset[1]))
        if 0 <= self.global_offset[0] <= screen_w:
            pg.draw.line(screen, AXIS_COLOR, (self.global_offset[0], 0), (self.global_offset[0], screen_h))

        for x in range(offset_x, screen_w + offset_x, 50):
            for y in range(offset_y, screen_h + offset_y, 50):
                screen.set_at((x, y), GUIDELINE_COLOR)

    def draw(self, screen: pg.Surface):
        screen.fill(EDITOR_BG_COLOR)

        self.__update_info_bar()
        self.__draw_background_grid(screen)
        draw_arrows(screen, self.blocks, self.global_offset)

        for block in self.blocks:
            state = BlockState.IDLE
            if block in self.selected_blocks:
                state = BlockState.SELECTED
            elif block is self.fake_pending_next_block:
                state = BlockState.PENDING_NEXT_BLOCK
            block.draw(screen, state, self.global_offset)

        if self.info_bar is not None:
            self.info_bar.draw(screen)

        if self.selecting:
            pg.draw.rect(screen, SELECTION_BORDER_COLOR, self.select_area, 1)
