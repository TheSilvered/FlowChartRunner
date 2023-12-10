from __future__ import annotations
import pygame as pg
from abc import ABC, abstractmethod
from draw_utils import *
from text_rendering import *
from .constants import (
    BLOCK_BG_COLOR,
    BLOCK_BORDER_COLOR,
    SELECTION_BORDER_COLOR,
    RUNNING_BORDER_COLOR,
    ERROR_BORDER_COLOR,
    PENDING_NEXT_BLOCK_BORDER_COLOR
)
from typing import Iterable
from enum import Enum, auto
from asset_manager import get_image
from .arrow_point_selector import ArrowDirection
from .base_component import UIBaseComponent, Pos, pos_t


class BlockState(Enum):
    IDLE = auto()
    SELECTED = auto()
    RUNNING = auto()
    ERROR = auto()
    PENDING_NEXT_BLOCK = auto()


_block_state_colors = {
    BlockState.IDLE: BLOCK_BORDER_COLOR,
    BlockState.SELECTED: SELECTION_BORDER_COLOR,
    BlockState.RUNNING: RUNNING_BORDER_COLOR,
    BlockState.ERROR: ERROR_BORDER_COLOR,
    BlockState.PENDING_NEXT_BLOCK: PENDING_NEXT_BLOCK_BORDER_COLOR
}


class BlockBase(UIBaseComponent, ABC):
    def __init__(self, content: str, prev_block: _prev_block_t = None):
        super().__init__(pg.Rect(0, 0, 0, 0))
        self.content: str = content
        self._next_block: BlockBase | None = None
        self.in_point: ArrowDirection = ArrowDirection.TOP
        try:
            self.out_point: ArrowDirection = ArrowDirection.BOTTOM
        except ValueError:
            pass
        self._editable = True

        if prev_block is None:
            return

        if isinstance(prev_block, BlockBase):
            prev_block.next_block = self
        else:
            for block in prev_block:
                block.next_block = self

    @abstractmethod
    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        pass

    @property
    @abstractmethod
    def size(self) -> Pos:
        pass

    @size.setter
    def size(self, value: pos_t):
        raise ValueError("cannot set the size of a block")

    @property
    def rect(self) -> pg.Rect:
        return pg.Rect(self.pos.t, self.size.t)

    @property
    def editable(self):
        return self._editable

    @property
    def next_block(self) -> BlockBase | None:
        return self._next_block

    @next_block.setter
    def next_block(self, value):
        self._next_block = value

    def __str__(self):
        return f"{self.__class__.__name__}(next: {self.next_block.__class__.__name__})"

    def __hash__(self):
        return id(self)

    def inside(self, rect: pg.Rect) -> bool:
        br = self.rect
        return br.x >= rect.x and br.y >= rect.y and br.x + br.w <= rect.x + rect.w and br.y + br.h <= rect.y + rect.h

    def handle_event(self, event: pg.event.Event) -> bool:
        return False


_prev_block_t = BlockBase | Iterable[BlockBase] | None


class StartBlock(BlockBase):
    def __init__(self, content: str = "START"):
        super().__init__(content)
        self._surf_cache = None
        self._editable = False

    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        text = write_text_highlighted(self.content, "center")
        text_size = list(text.get_size())
        text_size[0] += 20
        text_size[1] += 20
        draw_rect(
            screen,
            pg.Rect(list(self.pos + global_offset), text_size),
            BLOCK_BG_COLOR,
            text_size[1],
            2,
            _block_state_colors[state])
        screen.blit(text, list(self.pos + (10, 10) + global_offset))

    @property
    def size(self) -> Pos:
        text_size = get_text_size(self.content)
        return Pos(text_size[0] + 20, text_size[1] + 20)


class EndBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str = "END"):
        super().__init__(content, prev_block)
        self._surf_cache = None
        self._editable = False

    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        text = write_text_highlighted(self.content, "center")
        text_size = list(text.get_size())
        text_size[0] += 20
        text_size[1] += 20
        draw_rect(
            screen,
            pg.Rect(list(self.pos + global_offset), text_size),
            BLOCK_BG_COLOR,
            text_size[1],
            2,
            _block_state_colors[state])
        screen.blit(text, list(self.pos + (10, 10) + global_offset))

    @property
    def size(self) -> Pos:
        text_size = get_text_size(self.content)
        return Pos(text_size[0] + 20, text_size[1] + 20)


class IOBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str, input_: bool = False):
        super().__init__(content, prev_block)
        self.is_input = input_

    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_parallelogram((text_w + 35, text_h + 20), 10, BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, list(self.pos + global_offset))
        info_x = self.pos[0] + text_w + 22
        info_y = self.pos[1] + 2
        if self.is_input:
            screen.blit(get_image("input.png"), (info_x + global_offset[0], info_y + global_offset[1]))
        else:
            screen.blit(get_image("output.png"), (info_x + global_offset[0], info_y + global_offset[1]))
        screen.blit(text_surf, list(self.pos + (15, 10) + global_offset))

    @property
    def size(self) -> Pos:
        text_size = get_text_size(self.content)
        return Pos(text_size[0] + 35, text_size[1] + 20)


class _OptionBlock(BlockBase):
    def __init__(self, out_point):
        super().__init__("")
        self.out_point = out_point

    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        raise NotImplementedError("an option block cannot be drawn")

    @property
    def size(self) -> Pos:
        raise NotImplementedError("an option block does not have a size")


class CondBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str, true_branch: str = "T", false_branch: str = "F"):
        super().__init__(content, prev_block)
        self.on_true = _OptionBlock(ArrowDirection.LEFT)
        self.on_false = _OptionBlock(ArrowDirection.RIGHT)
        self.true_branch = true_branch
        self.false_branch = false_branch

    @property
    def next_block(self):
        raise ValueError("cannot get the next block of a conditional block directly")

    @next_block.setter
    def next_block(self, value):
        if value is None:
            return
        raise ValueError("cannot set the next block of a conditional block directly")

    @property
    def out_point(self):
        raise ValueError("cannot get the out_point of a conditional block directly")

    @out_point.setter
    def out_point(self, value):
        raise ValueError("cannot set the out_point of a conditional block directly")

    def __str__(self):
        return f"{self.__class__.__name__}(on_true: {self.on_true.next_block.__class__.__name__}," \
               f" on_false: {self.on_false.next_block.__class__.__name__})"

    def __draw_branch(self, screen, name, direction, global_offset):
        text = write_text(name)
        text_rect = pg.Rect((0, 0), text.get_size())
        if direction == ArrowDirection.TOP:
            text_rect.bottomleft = self.rect.midtop
        elif direction == ArrowDirection.BOTTOM:
            text_rect.topleft = self.rect.midbottom
        elif direction == ArrowDirection.LEFT:
            text_rect.bottomright = self.rect.midleft
        else:
            text_rect.bottomleft = self.rect.midright
        text_rect.x += global_offset[0]
        text_rect.y += global_offset[1]
        screen.blit(text, text_rect)

    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_rombus((text_w * 2 + 20, text_h * 2 + 20), BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, list(self.pos + global_offset))
        screen.blit(text_surf, list(self.pos + (text_w // 2 + 10, text_h // 2 + 10) + global_offset))
        self.__draw_branch(screen, self.true_branch, self.on_true.out_point, global_offset)
        self.__draw_branch(screen, self.false_branch, self.on_false.out_point, global_offset)

    @property
    def size(self) -> Pos:
        text_size = get_text_size(self.content)
        return Pos(text_size[0] * 2 + 20, text_size[1] * 2 + 20)


class InitBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_hexagon(
            (text_w + 40, text_h + 20),
            10, BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, list(self.pos + global_offset))
        screen.blit(text_surf, list(self.pos + (20, 10) + global_offset))

    @property
    def size(self) -> Pos:
        text_size = get_text_size(self.content)
        return Pos(text_size[0] + 40, text_size[1] + 20)


class CalcBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def draw(self, screen, state: BlockState = BlockState.IDLE, global_offset=(0, 0)):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        draw_rect(
            screen,
            pg.Rect(list(self.pos + global_offset), (text_w + 20, text_h + 20)),
            BLOCK_BG_COLOR,
            0, 2, _block_state_colors[state])
        screen.blit(text_surf, list(self.pos + (10, 10) + global_offset))

    @property
    def size(self) -> Pos:
        text_size = get_text_size(self.content)
        return Pos(text_size[0] + 20, text_size[1] + 20)
