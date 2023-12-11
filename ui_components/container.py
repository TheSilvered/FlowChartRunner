import pygame as pg
from enum import Enum, auto
from .base_component import UIBaseComponent, DummyComponent
from .constraint import Anchor, AnchorPoint, DynamicOffset


class ContainerDirection(Enum):
    TOP_TO_BOTTOM = auto()
    BOTTOM_TO_TOP = auto()
    V_SPACED_TB = auto()
    V_SPACED_BT = auto()
    LEFT_TO_RIGHT = auto()
    RIGHT_TO_LEFT = auto()
    H_SPACED_LR = auto()
    H_SPACED_RL = auto()


class ContainerAlignment(Enum):
    LEFT_TOP = auto()
    RIGHT_BOTTOM = auto()
    CENTER = auto()


class Container(UIBaseComponent):
    def __init__(
            self,
            rect: pg.Rect,
            components: list[UIBaseComponent],
            direction: ContainerDirection,
            align: ContainerAlignment,
            padding: int = 0
    ):
        super().__init__(rect)
        self.components = components
        self.direction = direction
        self.align = align
        self.padding = padding
        self.__drawn_components = []

        self.apply_constraints()

    def _w_diff(self):
        return self.w - sum(map(lambda c: c.w, self.components))

    def _h_diff(self):
        return self.h - sum(map(lambda c: c.h, self.components))

    def apply_constraints(self):
        if len(self.components) == 0:
            return

        if self.direction == ContainerDirection.TOP_TO_BOTTOM:
            self.__apply_tb_constraints()
        elif self.direction == ContainerDirection.BOTTOM_TO_TOP:
            self.__apply_bt_constraints()
        elif self.direction == ContainerDirection.V_SPACED_TB:
            self.__apply_vs_constraints()
        elif self.direction == ContainerDirection.V_SPACED_BT:
            self.components.reverse()
            self.__apply_vs_constraints()
        elif self.direction == ContainerDirection.LEFT_TO_RIGHT:
            self.__apply_lr_constraints()
        elif self.direction == ContainerDirection.RIGHT_TO_LEFT:
            self.__apply_rl_constraints()
        elif self.direction == ContainerDirection.H_SPACED_LR:
            self.__apply_hs_constraints()
        else:
            self.components.reverse()
            self.__apply_hs_constraints()

    def __apply_stacked_constraints(self, parent_point, child_point):
        self.__drawn_components = [self.components[0]]

        self.components[0].add_constraint(Anchor(self, child_point, child_point))
        prev_comp = self.components[0]
        for comp in self.components[1:]:
            if self.padding:
                padding_element = DummyComponent(pg.Rect(0, 0, self.padding, self.padding))
                padding_element.add_constraint(Anchor(prev_comp, parent_point, child_point))
                self.__drawn_components.append(padding_element)
                prev_comp = padding_element
            self.__drawn_components.append(comp)
            comp.add_constraint(Anchor(prev_comp, parent_point, child_point))
            prev_comp = comp

    def __apply_tb_constraints(self):
        if self.align == ContainerAlignment.LEFT_TOP:
            self.__apply_stacked_constraints(AnchorPoint.BL, AnchorPoint.TL)
        elif self.align == ContainerAlignment.RIGHT_BOTTOM:
            self.__apply_stacked_constraints(AnchorPoint.BR, AnchorPoint.TR)
        else:
            self.__apply_stacked_constraints(AnchorPoint.BC, AnchorPoint.TC)

    def __apply_bt_constraints(self):
        if self.align == ContainerAlignment.LEFT_TOP:
            self.__apply_stacked_constraints(AnchorPoint.TL, AnchorPoint.BL)
        elif self.align == ContainerAlignment.RIGHT_BOTTOM:
            self.__apply_stacked_constraints(AnchorPoint.TR, AnchorPoint.BR)
        else:
            self.__apply_stacked_constraints(AnchorPoint.TC, AnchorPoint.BC)

    def get_v_offset(self, i, frac):
        return 0, self._h_diff() * frac + sum(map(lambda c: c.w, self.components[:i]))

    def __apply_vs_constraints(self):
        n = 1
        d = len(self.components) * 2
        if self.align == ContainerAlignment.LEFT_TOP:
            ac = AnchorPoint.TL
        elif self.align == ContainerAlignment.RIGHT_BOTTOM:
            ac = AnchorPoint.TR
        else:
            ac = AnchorPoint.TC

        for i, comp in enumerate(self.components):
            comp.add_constraint(Anchor(self, ac, ac))
            comp.add_constraint(DynamicOffset(self.get_v_offset, (i, n / d)))
            n += 2
        self.__drawn_components = self.components

    def __apply_lr_constraints(self):
        if self.align == ContainerAlignment.LEFT_TOP:
            self.__apply_stacked_constraints(AnchorPoint.TR, AnchorPoint.TL)
        elif self.align == ContainerAlignment.RIGHT_BOTTOM:
            self.__apply_stacked_constraints(AnchorPoint.BR, AnchorPoint.BL)
        else:
            self.__apply_stacked_constraints(AnchorPoint.CR, AnchorPoint.CL)

    def __apply_rl_constraints(self):
        if self.align == ContainerAlignment.LEFT_TOP:
            self.__apply_stacked_constraints(AnchorPoint.TL, AnchorPoint.TR)
        elif self.align == ContainerAlignment.RIGHT_BOTTOM:
            self.__apply_stacked_constraints(AnchorPoint.BL, AnchorPoint.BR)
        else:
            self.__apply_stacked_constraints(AnchorPoint.CL, AnchorPoint.CR)

    def get_h_offset(self, i, frac):
        return self._w_diff() * frac + sum(map(lambda c: c.w, self.components[:i])), 0

    def __apply_hs_constraints(self):
        n = 1
        d = len(self.components) * 2
        if self.align == ContainerAlignment.LEFT_TOP:
            ac = AnchorPoint.TL
        elif self.align == ContainerAlignment.RIGHT_BOTTOM:
            ac = AnchorPoint.BL
        else:
            ac = AnchorPoint.CL

        for i, comp in enumerate(self.components):
            comp.add_constraint(Anchor(self, ac, ac))
            comp.add_constraint(DynamicOffset(self.get_h_offset, (i, n/d)))
            n += 2
        self.__drawn_components = self.components

    def handle_event(self, event: pg.event.Event) -> bool:
        for component in self.components:
            if component.handle_event(event):
                return True
        return False

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        for component in self.__drawn_components:
            component.draw(screen, *args, **kwargs)
