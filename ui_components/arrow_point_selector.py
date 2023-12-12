import pygame as pg
from asset_manager import get_icon
from .constants import (
    ARROW_POINT_SELECTOR_RECT_W, ARROW_POINT_SELECTOR_RECT_H, ARROW_POINT_SELECTOR_RECT_COLOR,
    ARROW_POINT_SELECTOR_PADDING, ARROW_POINT_ACTIVE_COLOR, ARROW_POINT_SELECTED_COLOR, ARROW_POINT_DISABLED_COLOR
)
from draw_utils import draw_rect
from .base_component import UIBaseComponent
from .button import Button
from .constraint import Anchor, AnchorPoint


class ArrowDirection:
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class _ArrowPointButton(Button):
    def __init__(self, selector, direction, inward):
        self.selector = selector
        self.inward = inward
        self.direction = direction
        self.arrow_image_active: pg.Surface | None   = None
        self.arrow_image_occupied: pg.Surface | None = None
        self.arrow_image_normal: pg.Surface | None   = None
        self.__set_images()
        super().__init__(
            rect=pg.Rect((0, 0), self.arrow_image_normal.get_size()),
            on_click=selector.set_direction,
            on_click_args=(direction,),
            extra_padding=10
        )
        self.__apply_constraints()

    def __rotate_images(self, angle):
        self.arrow_image_active = pg.transform.rotate(self.arrow_image_active, angle)
        self.arrow_image_occupied = pg.transform.rotate(self.arrow_image_occupied, angle)
        self.arrow_image_normal = pg.transform.rotate(self.arrow_image_normal, angle)

    def __set_images(self):
        self.arrow_image_active   = get_icon("arrow_button.png", ARROW_POINT_SELECTED_COLOR)
        self.arrow_image_occupied = get_icon("arrow_button.png", ARROW_POINT_DISABLED_COLOR)
        self.arrow_image_normal   = get_icon("arrow_button.png", ARROW_POINT_ACTIVE_COLOR)

        if self.inward:
            self.__rotate_images(180)

        if self.direction == ArrowDirection.BOTTOM:
            self.__rotate_images(180)
        elif self.direction == ArrowDirection.LEFT:
            self.__rotate_images(90)
        elif self.direction == ArrowDirection.RIGHT:
            self.__rotate_images(-90)

    def __apply_constraints(self):
        if self.direction == ArrowDirection.TOP:
            self.add_constraint(Anchor(self.selector, AnchorPoint.TC, AnchorPoint.TC))
        elif self.direction == ArrowDirection.BOTTOM:
            self.add_constraint(Anchor(self.selector, AnchorPoint.BC, AnchorPoint.BC))
        elif self.direction == ArrowDirection.LEFT:
            self.add_constraint(Anchor(self.selector, AnchorPoint.CL, AnchorPoint.CL))
        elif self.direction == ArrowDirection.RIGHT:
            self.add_constraint(Anchor(self.selector, AnchorPoint.CR, AnchorPoint.CR))

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        if self.direction == self.selector.direction:
            image = self.arrow_image_active
        elif self.direction in [sel.direction for sel in self.selector.links]:
            image = self.arrow_image_occupied
        else:
            image = self.arrow_image_normal
        screen.blit(image, self.rect)


class ArrowPointSelector(UIBaseComponent):
    def __init__(self, direction: ArrowDirection, inward: bool):
        self.direction = direction
        self.inward = inward
        arrow_image = get_icon("arrow_button.png", ARROW_POINT_ACTIVE_COLOR)

        self.links: list[ArrowPointSelector] = []

        super().__init__(pg.Rect(
            0, 0,
            # get_height because image is rotated
            arrow_image.get_height() * 2 + ARROW_POINT_SELECTOR_RECT_W + ARROW_POINT_SELECTOR_PADDING * 2,
            # get_width  because image is rotated
            arrow_image.get_width() * 2 + ARROW_POINT_SELECTOR_RECT_H + ARROW_POINT_SELECTOR_PADDING * 2
        ))

        self.top_arrow    = _ArrowPointButton(self, ArrowDirection.TOP,    self.inward)
        self.bottom_arrow = _ArrowPointButton(self, ArrowDirection.BOTTOM, self.inward)
        self.left_arrow   = _ArrowPointButton(self, ArrowDirection.LEFT,   self.inward)
        self.right_arrow  = _ArrowPointButton(self, ArrowDirection.RIGHT,  self.inward)

    def link_selector(self, selector):
        self.links.append(selector)

    def handle_event(self, event):
        if self.top_arrow.handle_event(event):
            return True
        if self.bottom_arrow.handle_event(event):
            return True
        if self.left_arrow.handle_event(event):
            return True
        if self.right_arrow.handle_event(event):
            return True
        return False

    def set_direction(self, direction):
        self.direction = direction
        if self.direction not in [sel.direction for sel in self.links]:
            return
        for selector in self.links:
            if selector.direction != self.direction:
                continue
            if self.direction == ArrowDirection.TOP:
                selector.direction = ArrowDirection.BOTTOM
            elif self.direction == ArrowDirection.BOTTOM:
                selector.direction = ArrowDirection.TOP
            elif self.direction == ArrowDirection.LEFT:
                selector.direction = ArrowDirection.RIGHT
            else:
                selector.direction = ArrowDirection.LEFT
            break

    def _draw(self, screen, *args, **kwargs):
        self.top_arrow.draw(screen)
        self.bottom_arrow.draw(screen)
        self.left_arrow.draw(screen)
        self.right_arrow.draw(screen)

        draw_rect(
            screen,
            pg.Rect(
                self.rect.x + self.top_arrow.h + ARROW_POINT_SELECTOR_PADDING,
                self.rect.y + self.left_arrow.w + ARROW_POINT_SELECTOR_PADDING,
                ARROW_POINT_SELECTOR_RECT_W,
                ARROW_POINT_SELECTOR_RECT_H
            ),
            ARROW_POINT_SELECTOR_RECT_COLOR[:3] + (0,),
            2,
            2,
            ARROW_POINT_SELECTOR_RECT_COLOR
        )
