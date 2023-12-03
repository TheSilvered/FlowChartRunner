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
    ERROR_BORDER_COLOR
)
from typing import Iterable
from enum import Enum, auto
from dataclasses import dataclass
from asset_manager import get_image


@dataclass
class Pos:
    x: int
    y: int

    def __add__(self, other):
        try:
            return Pos(self.x + other[0], self.y + other[1])
        except Exception:
            raise NotImplemented

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            return Pos(self.x - other[0], self.y - other[1])
        except Exception:
            raise NotImplemented

    def __isub__(self, other):
        return self.__sub__(other)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError(f"index {item} out of Pos")

    def __iter__(self):
        return iter((self.x, self.y))


class BlockState(Enum):
    IDLE = auto()
    SELECTED = auto()
    RUNNING = auto()
    ERROR = auto()


_block_state_colors = {
    BlockState.IDLE: BLOCK_BORDER_COLOR,
    BlockState.SELECTED: SELECTION_BORDER_COLOR,
    BlockState.RUNNING: RUNNING_BORDER_COLOR,
    BlockState.ERROR: ERROR_BORDER_COLOR
}


class BlockBase(ABC):
    def __init__(self, content: str, prev_block: _prev_block_t = None):
        self.content: str = content
        self._next_block: BlockBase | None = None
        self._pos: Pos = Pos(0, 0)
        self.in_point = "top"
        self.out_point = ["bottom"]
        self._editable = True

        if prev_block is None:
            return

        if isinstance(prev_block, BlockBase):
            prev_block.next_block = self
        else:
            for block in prev_block:
                block.next_block = self

    @property
    def editable(self):
        return self._editable

    def __str__(self):
        return f"{self.__class__.__name__}(next: {', '.join(b.__class__.__name__ for b in self.next_block)})"

    def __hash__(self):
        return id(self)

    @abstractmethod
    def execute(self) -> BlockBase | None:
        pass

    @abstractmethod
    def draw(self, screen, state, global_offset):
        pass

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        pass

    @property
    def rect(self):
        return pg.Rect(*self.pos, *self.get_size())

    @property
    def next_block(self) -> tuple[BlockBase] | tuple:
        if self._next_block is None:
            return ()
        else:
            return self._next_block,

    @next_block.setter
    def next_block(self, value):
        self._next_block = value

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, new_pos: list[int] | tuple[int, int] | Pos):
        if isinstance(new_pos, Pos):
            self._pos = new_pos
        else:
            self._pos = Pos(*new_pos)

    def add_pos(self, point: list[int] | tuple[int, int] | Pos):
        self._pos += point

    def sub_pos(self, point: list[int] | tuple[int, int] | Pos):
        self._pos -= point

    def inside(self, rect: pg.Rect) -> bool:
        br = self.rect
        return br.x >= rect.x and br.y >= rect.y and br.x + br.w <= rect.x + rect.w and br.y + br.h <= rect.y + rect.h


_prev_block_t = BlockBase | Iterable[BlockBase] | None


class StartBlock(BlockBase):
    def __init__(self, content: str = "START"):
        super().__init__(content)
        self._surf_cache = None
        self._editable = False

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state: BlockState, global_offset):
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

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 20, text_size[1] + 20


class EndBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str = "END"):
        super().__init__(content, prev_block)
        self._surf_cache = None
        self._editable = False

    def execute(self):
        return None

    def draw(self, screen, state, global_offset):
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

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 20, text_size[1] + 20


class IOBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str, input_: bool = False):
        super().__init__(content, prev_block)
        self.is_input = input_

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state, global_offset):
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

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 35, text_size[1] + 20


class _OptionBlock(BlockBase):
    def __init__(self):
        super().__init__("")

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state, global_offset):
        raise NotImplementedError("an option block cannot be drawn")

    def get_size(self):
        raise NotImplementedError("an option block does not have a size")


class CondBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)
        self.on_true = _OptionBlock()
        self.on_false = _OptionBlock()
        self.out_point = ["left", "right"]

    @property
    def next_block(self):
        if self.on_true.next_block == ():
            on_true_next_block = None
        else:
            on_true_next_block = self.on_true.next_block[0]
        if self.on_false.next_block == ():
            on_false_next_block = None
        else:
            on_false_next_block = self.on_false.next_block[0]
        return on_true_next_block, on_false_next_block

    @next_block.setter
    def next_block(self, value):
        if value is None:
            return
        raise ValueError("cannot set the next block of a conditional block directly")

    def execute(self) -> BlockBase:
        return self.on_true.next_block[0]

    def draw(self, screen, state, global_offset):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_rombus((text_w * 2 + 20, text_h * 2 + 20), BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, list(self.pos + global_offset))
        screen.blit(text_surf, list(self.pos + (text_w // 2 + 10, text_h // 2 + 10) + global_offset))
        f_pos = Pos(*getattr(self.rect, "mid" + self.out_point[1]))
        f_pos.y -= line_height()
        f_pos.x += 2
        t_pos = Pos(*getattr(self.rect, "mid" + self.out_point[0]))
        t_pos.y -= line_height()
        t_pos.x -= 10
        screen.blit(write_text("F"), list(f_pos + global_offset))
        screen.blit(write_text("T"), list(t_pos + global_offset))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] * 2 + 20, text_size[1] * 2 + 20


class InitBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state, global_offset):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_hexagon(
            (text_w + 40, text_h + 20),
            10, BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, list(self.pos + global_offset))
        screen.blit(text_surf, list(self.pos + (20, 10) + global_offset))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 40, text_size[1] + 20


class CalcBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state, global_offset):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        draw_rect(
            screen,
            pg.Rect(list(self.pos + global_offset), (text_w + 20, text_h + 20)),
            BLOCK_BG_COLOR,
            0, 2, _block_state_colors[state])
        screen.blit(text_surf, list(self.pos + (10, 10)))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 20, text_size[1] + 20
