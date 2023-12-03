from ui_components.blocks import *
from .constants import GUIDELINE_COLOR, AXIS_COLOR, EDITOR_BG_COLOR
from text_rendering import line_height
from ui_components import InfoBar, draw_arrows
import pygame as pg


class Editor:
    def __init__(self):
        start_block = StartBlock()
        end_block = EndBlock(start_block)

        start_block.pos = [0, 0]
        end_block_x = (start_block.get_size()[0] - end_block.get_size()[0]) / 2 + start_block.pos[0]
        end_block.pos = [end_block_x, start_block.get_size()[1] + line_height() * 3]

        self.blocks: list[BlockBase] = [start_block, end_block]
        self.dragging_blocks: list[BlockBase] | None = None
        self.has_moved = False
        self.dragging_global = False
        self.selecting = False
        self.select_start = (0, 0)
        self.select_area = pg.Rect(-1, -1, 0, 0)
        self.selected_blocks: list[BlockBase] = []
        self.global_offset = [0, 0]
        self.info_bar: InfoBar | None = None

    def __add_blocks(self, start_block):
        block_set = set()
        queue = [start_block]
        for block in queue:
            if block in block_set:
                continue
            self.blocks.append(block)
            block_set.add(block)
            for next_block in block.next_block:
                queue.append(next_block)

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
            return
        elif event.button != pg.BUTTON_LEFT:
            return

        block = self.intersect_point(event.pos)
        if block is not None:
            if block not in self.selected_blocks:
                self.selected_blocks = [block]
            self.dragging_blocks = self.selected_blocks
            return
        self.selected_blocks = []
        self.selecting = True
        self.select_start = event.pos
        self.select_area = pg.Rect(event.pos, (0, 0))

    def __handle_mouse_button_up_event(self, event):
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
                cond_block = CondBlock(None, "")
                self.blocks.append(cond_block)
            elif event.key == pg.K_n:
                calc_block = CalcBlock(None, "")
                self.blocks.append(calc_block)
            elif event.key == pg.K_v:
                var_block = InitBlock(None, "")
                self.blocks.append(var_block)

            if len(self.selected_blocks) != 1:
                return

            block = self.selected_blocks[0]
            if event.key == pg.K_UP:
                block.out_point[0] = "top"
            elif event.key == pg.K_DOWN:
                block.out_point[0] = "bottom"
            elif event.key == pg.K_LEFT:
                block.out_point[0] = "left"
            elif event.key == pg.K_RIGHT:
                block.out_point[0] = "right"
            elif event.key == pg.K_KP8:
                block.in_point = "top"
            elif event.key == pg.K_KP2:
                block.in_point = "bottom"
            elif event.key == pg.K_KP4:
                block.in_point = "left"
            elif event.key == pg.K_KP6:
                block.in_point = "right"

    def __update_info_bar(self):
        if len(self.selected_blocks) != 1:
            self.info_bar = None
        elif self.info_bar != self.selected_blocks[0]:
            self.info_bar = InfoBar(self.selected_blocks[0])

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
            block.draw(
                screen,
                BlockState.SELECTED if block in self.selected_blocks else BlockState.IDLE,
                self.global_offset
            )

        if self.info_bar is not None:
            self.info_bar.draw(screen)

        if self.selecting:
            pg.draw.rect(screen, SELECTION_BORDER_COLOR, self.select_area, 1)
