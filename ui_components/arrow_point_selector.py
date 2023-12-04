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
            0, 0,
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

    def __get_image_rect(self, direction):
        if direction == self.direction or direction in [s.direction for s in self.links]:
            return None

        arrow_image = self.__get_image(direction)

        if direction == ArrowDirection.TOP:
            pos = (self.rect.centerx - arrow_image.get_width() // 2, self.rect.top)
        elif direction == ArrowDirection.LEFT:
            pos = (self.rect.left, self.rect.centery - arrow_image.get_height() // 2)
        elif direction == ArrowDirection.BOTTOM:
            pos = (self.rect.centerx - arrow_image.get_width() // 2, self.rect.bottom - arrow_image.get_height())
        else:
            pos = (self.rect.right - arrow_image.get_width(), self.rect.centery - arrow_image.get_height() // 2)
        return pg.Rect(pos, arrow_image.get_size())

    def handle_event(self, event):
        if event.type != pg.MOUSEBUTTONDOWN:
            return False
        if not self.rect.collidepoint(event.pos):
            return False

        top_rect = self.__get_image_rect(ArrowDirection.TOP)
        if top_rect is not None and top_rect.collidepoint(event.pos):
            self.direction = ArrowDirection.TOP
            return True
        bottom_rect = self.__get_image_rect(ArrowDirection.BOTTOM)
        if bottom_rect is not None and bottom_rect.collidepoint(event.pos):
            self.direction = ArrowDirection.BOTTOM
            return True
        left_rect = self.__get_image_rect(ArrowDirection.LEFT)
        if left_rect is not None and left_rect.collidepoint(event.pos):
            self.direction = ArrowDirection.LEFT
            return True
        right_rect = self.__get_image_rect(ArrowDirection.RIGHT)
        if right_rect is not None and right_rect.collidepoint(event.pos):
            self.direction = ArrowDirection.RIGHT
            return True
        return False

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
