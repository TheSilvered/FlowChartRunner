from abc import ABC, abstractmethod
from .base_component import UIBaseComponent


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


class AnchorConstraint(Constraint):
    def __init__(self, parent_object: UIBaseComponent, parent_point: AnchorPoint, child_point: AnchorPoint):
        self.parent_object = parent_object
        self.parent_point = parent_point
        self.child_point = child_point

    def apply(self, ui_comp: UIBaseComponent):
        rect = ui_comp.rect.copy()
        setattr(rect, str(self.child_point), getattr(self.parent_object.rect, str(self.parent_point)))
        ui_comp.pos = rect.topleft
