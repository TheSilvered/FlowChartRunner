import pygame as pg
from asset_manager import get_image
from .constants import (
    ARROW_POINT_SELECTOR_RECT_W, ARROW_POINT_SELECTOR_RECT_H, ARROW_POINT_SELECTOR_RECT_COLOR,
    ARROW_POINT_SELECTOR_PADDING
)


class ArrowDirection:
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class ArrowPointSelector:
    def __init__(self, direction: ArrowDirection, inward: bool):
        self.direction = direction
        self.inward = inward
        arrow_image = get_image("arrow_button.png", True)

        self.links: list[ArrowPointSelector] = []

        self.rect = pg.Rect(
            0,
            0,
            # get_height because image is rotated
            arrow_image.get_height() * 2 + ARROW_POINT_SELECTOR_RECT_W + ARROW_POINT_SELECTOR_PADDING * 2,
            # get_width  because image is rotated
            arrow_image.get_width() * 2 + ARROW_POINT_SELECTOR_RECT_H + ARROW_POINT_SELECTOR_PADDING * 2
        )

    @property
    def pos(self):
        return self.rect.topleft

    @pos.setter
    def pos(self, pos):
        self.rect.topleft = pos

    @property
    def size(self):
        return self.rect.size

    def link_selector(self, selector):
        self.links.append(selector)

    def __get_image(self, direction):
        if direction == self.direction:
            arrow_image = get_image("arrow_button_selected.png", True)
        elif direction in [s.direction for s in self.links]:
            arrow_image = get_image("arrow_button_disabled.png", True)
        else:
            arrow_image = get_image("arrow_button.png", True)

        if self.inward:
            arrow_image = pg.transform.rotate(arrow_image, 180)

        if direction == ArrowDirection.TOP:
            return arrow_image
        elif direction == ArrowDirection.BOTTOM:
            return pg.transform.rotate(arrow_image, 180)
        elif direction == ArrowDirection.LEFT:
            return pg.transform.rotate(arrow_image, 90)
        else:
            return pg.transform.rotate(arrow_image, -90)

    def draw(self, screen):
        arrow_image = self.__get_image(ArrowDirection.TOP)

        pg.draw.rect(
            screen,
            ARROW_POINT_SELECTOR_RECT_COLOR,
            pg.Rect(
                self.rect.x + arrow_image.get_height() + ARROW_POINT_SELECTOR_PADDING,
                self.rect.y + arrow_image.get_width() + ARROW_POINT_SELECTOR_PADDING,
                ARROW_POINT_SELECTOR_RECT_W,
                ARROW_POINT_SELECTOR_RECT_H
            ),
            2
        )

        pos = (self.rect.centerx - arrow_image.get_width() // 2, self.rect.top)
        screen.blit(arrow_image, pos)

        arrow_image = self.__get_image(ArrowDirection.LEFT)
        pos = (self.rect.left, self.rect.centery - arrow_image.get_height() // 2)
        screen.blit(arrow_image, pos)

        arrow_image = self.__get_image(ArrowDirection.BOTTOM)
        pos = (self.rect.centerx - arrow_image.get_width() // 2, self.rect.bottom - arrow_image.get_height())
        screen.blit(arrow_image, pos)

        arrow_image = self.__get_image(ArrowDirection.RIGHT)
        pos = (self.rect.right - arrow_image.get_width(), self.rect.centery - arrow_image.get_height() // 2)
        screen.blit(arrow_image, pos)
