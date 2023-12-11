from __future__ import annotations

import pygame as pg
from abc import ABC, abstractmethod
from typing import Iterable
from enum import Enum, auto

from draw_utils import *
from text_rendering import write_mono_text
from asset_manager import get_icon

from .constants import (
    BLOCK_BG_COLOR,
    BLOCK_BORDER_COLOR,
    SELECTION_BORDER_COLOR,
    RUNNING_BORDER_COLOR,
    ERROR_BORDER_COLOR,
    PENDING_NEXT_BLOCK_BORDER_COLOR
)
from .arrow_point_selector import ArrowDirection
from .base_component import UIBaseComponent, Pos, pos_t
from .text_label import TextLabel
from .constraint import Anchor, AnchorPoint, Offset


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
        self.content: TextLabel = TextLabel((0, 0), content, True, "center")
        self.content.add_constraint(Anchor(self, AnchorPoint.CC, AnchorPoint.CC))

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
        self.state = BlockState.IDLE

    @abstractmethod
    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
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
        self._editable = False

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        draw_rect(screen, self.rect, BLOCK_BG_COLOR, self.content.hi + 20, 2, _block_state_colors[self.state])
        self.content.draw(screen)

    @property
    def size(self) -> Pos:
        return self.content.size + (20, 20)


class EndBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str = "END"):
        super().__init__(content, prev_block)
        self._editable = False

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        draw_rect(screen, self.rect, BLOCK_BG_COLOR, self.content.hi + 20, 2, _block_state_colors[self.state])
        self.content.draw(screen)

    @property
    def size(self) -> Pos:
        return self.content.size + (20, 20)


class IOBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str, input_: bool = False):
        super().__init__(content, prev_block)
        self.content.add_constraint(Offset((-5, 0)))
        self.is_input = input_

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        block = draw_parallelogram(
            (self.content.size + (35, 20)).ti,
            10,
            BLOCK_BG_COLOR,
            _block_state_colors[self.state]
        )
        screen.blit(block, self.pos.ti)
        info_x = self.x + self.content.size.x + 22
        info_y = self.y + 2
        if self.is_input:
            screen.blit(get_icon("input.png", _block_state_colors[self.state]), (info_x, info_y))
        else:
            screen.blit(get_icon("output.png", _block_state_colors[self.state]), (info_x, info_y))
        self.content.draw(screen)

    @property
    def size(self) -> Pos:
        return self.content.size + (35, 20)


class _OptionBlock(BlockBase):
    def __init__(self, out_point):
        super().__init__("")
        self.out_point = out_point

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
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

    def __draw_branch(self, screen, name, direction):
        text = write_mono_text(name)
        text_rect = pg.Rect((0, 0), text.get_size())
        if direction == ArrowDirection.TOP:
            text_rect.bottomleft = self.rect.midtop
        elif direction == ArrowDirection.BOTTOM:
            text_rect.topleft = self.rect.midbottom
        elif direction == ArrowDirection.LEFT:
            text_rect.bottomright = self.rect.midleft
        else:
            text_rect.bottomleft = self.rect.midright
        screen.blit(text, text_rect)

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        block = draw_rombus(
            (self.content.size * (2, 2) + (20, 20)).ti,
            BLOCK_BG_COLOR,
            _block_state_colors[self.state]
        )
        screen.blit(block, self.pos.ti)
        self.content.draw(screen)
        self.__draw_branch(screen, self.true_branch, self.on_true.out_point)
        self.__draw_branch(screen, self.false_branch, self.on_false.out_point)

    @property
    def size(self) -> Pos:
        return self.content.size * (2, 2) + (20, 20)


class InitBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        block = draw_hexagon(
            (self.content.size + (40, 20)).ti,
            10, BLOCK_BG_COLOR, _block_state_colors[self.state]
        )
        screen.blit(block, self.pos.ti)
        self.content.draw(screen)

    @property
    def size(self) -> Pos:
        return self.content.size + (40, 20)


class CalcBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        draw_rect(
            screen,
            self.rect,
            BLOCK_BG_COLOR,
            0, 2,
            _block_state_colors[self.state]
        )
        self.content.draw(screen)

    @property
    def size(self) -> Pos:
        return self.content.size + (20, 20)
