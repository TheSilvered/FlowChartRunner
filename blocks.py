from __future__ import annotations
from abc import ABC, abstractmethod
from draw_utils import *
from constants import (
    BLOCK_BG_COLOR,
    BLOCK_BORDER_COLOR,
    SELECTION_BORDER_COLOR,
    RUNNING_BORDER_COLOR,
    ERROR_BORDER_COLOR
)
from typing import Iterable
from enum import Enum, auto


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
        self._pos: list[int, int] = [0, 0]
        self.in_point = "top"
        self.out_point = ["bottom"]

        if prev_block is None:
            return

        if isinstance(prev_block, BlockBase):
            prev_block.next_block = self
        else:
            for block in prev_block:
                block.next_block = self

    def __str__(self):
        return f"{self.__class__.__name__}(next: {', '.join(b.__class__.__name__ for b in self.next_block)})"

    def __hash__(self):
        return id(self)

    @abstractmethod
    def execute(self) -> BlockBase | None:
        pass

    @abstractmethod
    def draw(self, screen, state):
        pass

    @abstractmethod
    def get_size(self) -> tuple[int, int]:
        pass

    @property
    def rect(self):
        return pg.Rect(self.pos, self.get_size())

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
        return tuple(self._pos)

    @pos.setter
    def pos(self, new_pos: list[int] | tuple[int, int]):
        self._pos = list(new_pos)

    def add_pos(self, point: list[int] | tuple[int, int]):
        self._pos = [self._pos[0] + point[0], self._pos[1] + point[1]]

    def sub_pos(self, point: list[int] | tuple[int, int]):
        self._pos = [self._pos[0] - point[0], self._pos[1] - point[1]]

    def inside(self, rect: pg.Rect) -> bool:
        br = self.rect
        return br.x >= rect.x and br.y >= rect.y and br.x + br.w <= rect.x + rect.w and br.y + br.h <= rect.y + rect.h


_prev_block_t = BlockBase | Iterable[BlockBase] | None


class StartBlock(BlockBase):
    def __init__(self, content: str = "START"):
        super().__init__(content)
        self._surf_cache = None

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state: BlockState):
        text = write_text_highlighted(self.content, "center")
        text_size = list(text.get_size())
        text_size[0] += 20
        text_size[1] += 20
        aa_rect(
            screen,
            pg.Rect(self.pos, text_size),
            BLOCK_BG_COLOR,
            text_size[1],
            2,
            _block_state_colors[state])
        screen.blit(text, (self.pos[0] + 10, self.pos[1] + 10))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 20, text_size[1] + 20


class EndBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str = "END"):
        super().__init__(content, prev_block)
        self._surf_cache = None

    def execute(self):
        return None

    def draw(self, screen, state):
        text = write_text_highlighted(self.content, "center")
        text_size = list(text.get_size())
        text_size[0] += 20
        text_size[1] += 20
        aa_rect(
            screen,
            pg.Rect(self.pos, text_size),
            BLOCK_BG_COLOR,
            text_size[1],
            2,
            _block_state_colors[state])
        screen.blit(text, (self.pos[0] + 10, self.pos[1] + 10))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 20, text_size[1] + 20


class IOBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str, input_: bool = False):
        super().__init__(content, prev_block)
        self.is_input = input_

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_parallelogram((text_w + 35, text_h + 20), 10, BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, self.pos)
        info_x = self.pos[0] + text_w + 22
        info_y = self.pos[1] + 2
        if self.is_input:
            screen.blit(get_image("input.png"), (info_x, info_y))
        else:
            screen.blit(get_image("output.png"), (info_x, info_y))
        screen.blit(text_surf, (self.pos[0] + 15, self.pos[1] + 10))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 35, text_size[1] + 20


class _OptionBlock(BlockBase):
    def __init__(self):
        super().__init__("")

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state):
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
        return self.on_true.next_block[0], self.on_false.next_block[0]

    @next_block.setter
    def next_block(self, value):
        if value is None:
            return
        raise ValueError("cannot set the next block of a conditional block directly")

    def execute(self) -> BlockBase:
        return self.on_true.next_block[0]

    def draw(self, screen, state):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_rombus((text_w * 2 + 20, text_h * 2 + 20), BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, self.pos)
        screen.blit(text_surf, (self.pos[0] + text_w // 2 + 10, self.pos[1] + text_h // 2 + 10))
        f_pos = list(getattr(self.rect, "mid" + self.out_point[1]))
        f_pos[1] -= line_height()
        f_pos[0] += 2
        t_pos = list(getattr(self.rect, "mid" + self.out_point[0]))
        t_pos[1] -= line_height()
        t_pos[0] -= 10
        screen.blit(write_text("F"), f_pos)
        screen.blit(write_text("T"), t_pos)

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] * 2 + 20, text_size[1] * 2 + 20


class InitBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = draw_hexagon(
            (text_w + 40, text_h + 20),
            10, BLOCK_BG_COLOR, _block_state_colors[state])
        screen.blit(block, self.pos)
        screen.blit(text_surf, (self.pos[0] + 20, self.pos[1] + 10))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 40, text_size[1] + 20


class CalcBlock(BlockBase):
    def __init__(self, prev_block: _prev_block_t, content: str):
        super().__init__(content, prev_block)

    def execute(self) -> BlockBase:
        return self.next_block[0]

    def draw(self, screen, state):
        text_surf = write_text_highlighted(self.content, "center")

        text_w, text_h = text_surf.get_size()
        block = aa_rect(
            None,
            pg.Rect(0, 0, text_w + 20, text_h + 20),
            BLOCK_BG_COLOR,
            0, 2, _block_state_colors[state])
        screen.blit(block, self.pos)
        screen.blit(text_surf, (self.pos[0] + 10, self.pos[1] + 10))

    def get_size(self):
        text_size = get_text_size(self.content)
        return text_size[0] + 20, text_size[1] + 20
