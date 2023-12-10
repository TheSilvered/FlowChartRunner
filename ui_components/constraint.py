import pygame as pg
from abc import ABC, abstractmethod
from .base_component import UIBaseComponent, pos_t


class AnchorPoint:
    TL = "topleft"
    TC = "midtop"
    TR = "topright"
    CL = "midleft"
    CC = "center"
    CR = "midright"
    BL = "bottomleft"
    BC = "midbottom"
    BR = "bottomright"


class Constraint(ABC):
    @abstractmethod
    def apply(self, ui_comp: UIBaseComponent):
        pass


class Anchor(Constraint):
    def __init__(self, parent_object: UIBaseComponent, parent_point: AnchorPoint, child_point: AnchorPoint):
        self.parent_object = parent_object
        self.parent_point = parent_point
        self.child_point = child_point

    def apply(self, ui_comp: UIBaseComponent):
        rect = ui_comp.rect.copy()
        setattr(rect, str(self.child_point), getattr(self.parent_object.rect, str(self.parent_point)))
        ui_comp.pos = rect.topleft


class AnchorWindow(Constraint):
    def __init__(self, parent_point: AnchorPoint, child_point: AnchorPoint):
        self.parent_point = parent_point
        self.child_point = child_point

    def apply(self, ui_comp: UIBaseComponent):
        rect = ui_comp.rect.copy()
        window_rect = pg.Rect((0, 0), pg.display.get_window_size())
        setattr(rect, str(self.child_point), getattr(window_rect, str(self.parent_point)))
        ui_comp.pos = rect.topleft


class Offset(Constraint):
    def __init__(self, offset: pos_t):
        self.offset = offset

    def apply(self, ui_comp: UIBaseComponent):
        if self.offset[0] != 0:
            ui_comp.x += self.offset[0]
        if self.offset[1] != 0:
            ui_comp.y += self.offset[1]


class DynamicOffset(Constraint):
    def __init__(self, func, args=()):
        self.func = func
        self.args = args

    def apply(self, ui_comp: UIBaseComponent):
        offset = self.func(*self.args)
        ui_comp.pos += offset


class MatchX(Constraint):
    def __init__(self, parent_object: UIBaseComponent):
        self.parent_object = parent_object

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.x = self.parent_object.x


class MatchY(Constraint):
    def __init__(self, parent_object: UIBaseComponent):
        self.parent_object = parent_object

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.y = self.parent_object.y


class MatchWidth(Constraint):
    def __init__(self, parent_object: UIBaseComponent):
        self.parent_object = parent_object

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.w = self.parent_object.w


class MatchHeight(Constraint):
    def __init__(self, parent_object: UIBaseComponent):
        self.parent_object = parent_object

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.h = self.parent_object.h


class SizeDiff(Constraint):
    def __init__(self, diff: pos_t):
        self.diff = diff

    def apply(self, ui_comp: UIBaseComponent):
        if self.diff[0] != 0:
            ui_comp.w += self.diff[0]
        if self.diff[1] != 0:
            ui_comp.h += self.diff[1]


class MatchMaxWidth(Constraint):
    def __init__(self, components):
        self.components = components

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.w = max(map(lambda c: c.w, self.components))


class MatchMaxHeight(Constraint):
    def __init__(self, components):
        self.components = components

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.h = max(map(lambda c: c.h, self.components))


class MatchSumWidths(Constraint):
    def __init__(self, components, padding):
        self.components = components
        self.padding = padding

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.w = sum(map(lambda c: c.w, self.components)) + self.padding * (len(self.components) - 1)


class MatchSumHeights(Constraint):
    def __init__(self, components, padding):
        self.components = components
        self.padding = padding

    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.h = sum(map(lambda c: c.h, self.components)) + self.padding * (len(self.components) - 1)


class MatchWindowWidth(Constraint):
    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.h = pg.display.get_window_size()[1]


class MatchWindowHeight(Constraint):
    def apply(self, ui_comp: UIBaseComponent):
        ui_comp.h = pg.display.get_window_size()[1]
