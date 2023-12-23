import pygame as pg

from text_rendering import write_ui_text, ui_line_height
from draw_utils import draw_rect

from .base_component import UIBaseComponent
from .button import Button
from .constants import (
    MENU_BAR_BUTTON_PADDING, MENU_BAR_BUTTON_COLOR_CLICK, MENU_BAR_BUTTON_COLOR_HOVER, MENU_BAR_BUTTON_COLOR_IDLE,
    MENU_BAR_BORDER_COLOR, MENU_BAR_CORNER_RADIUS, SEPARATOR_THICKNESS
)
from .constraint import Anchor, AnchorWindow, AnchorPoint, MatchWindowWidth, MatchMaxWidth, MatchSumHeights, Constraint
from .container import Container, ContainerDirection, ContainerAlignment


class DropdownConstraint(Constraint):
    def __init__(self, menu_bar: UIBaseComponent, button: UIBaseComponent):
        self.menu_bar = menu_bar
        self.button = button

    def apply(self, ui_comp: UIBaseComponent):
        if self.button.x + ui_comp.w > self.menu_bar.rect.right:
            ui_comp.rect.topright = self.button.rect.bottomright
        else:
            ui_comp.rect.topleft = self.button.rect.bottomleft


class MenuBarButton(Button):
    def __init__(self, text, on_click, on_click_args, is_last, draw_border=False):
        self.text_surf = write_ui_text(text)
        width = self.text_surf.get_width() + MENU_BAR_BUTTON_PADDING * 2
        super().__init__(pg.Rect(0, 0, width, ui_line_height() + MENU_BAR_BUTTON_PADDING * 2), on_click, on_click_args)
        self.__is_last = is_last
        self.__draw_border = draw_border

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        if self.pressed:
            color = MENU_BAR_BUTTON_COLOR_CLICK
        elif self.collide_clickable(pg.mouse.get_pos()):
            color = MENU_BAR_BUTTON_COLOR_HOVER
        else:
            color = MENU_BAR_BUTTON_COLOR_IDLE

        left = self.rect.x + SEPARATOR_THICKNESS // 2
        right = self.rect.right - SEPARATOR_THICKNESS // 2 - 1
        top = self.rect.y
        bottom = self.rect.bottom

        if not self.__draw_border:
            pg.draw.rect(screen, color, self.rect)
        elif self.__is_last:
            draw_rect(screen, self.rect, color, MENU_BAR_CORNER_RADIUS, SEPARATOR_THICKNESS, MENU_BAR_BORDER_COLOR)
            pg.draw.rect(screen, color, pg.Rect(self.x, self.y, self.w, self.h // 2))
            bottom = self.rect.centery
        else:
            pg.draw.rect(screen, color, self.rect)

        if self.__draw_border:
            pg.draw.line(screen, MENU_BAR_BORDER_COLOR, (left, top), (left, bottom), SEPARATOR_THICKNESS)
            pg.draw.line(screen, MENU_BAR_BORDER_COLOR, (right, top), (right, bottom), SEPARATOR_THICKNESS)

        screen.blit(self.text_surf, (self.pos + (MENU_BAR_BUTTON_PADDING, MENU_BAR_BUTTON_PADDING)).t)


class MenuBar(UIBaseComponent):
    def __init__(self, options: dict):
        self.options = options
        super().__init__(pg.Rect(0, 0, 0, ui_line_height() + MENU_BAR_BUTTON_PADDING * 2))
        self.add_constraint(AnchorWindow(AnchorPoint.TL, AnchorPoint.TL))
        self.add_constraint(MatchWindowWidth())
        self.menu_buttons = {}
        prev_button = None
        for category in options:
            button = MenuBarButton(category, self.__show_category, (category,), False)
            self.menu_buttons[category] = button
            if prev_button is None:
                button.add_constraint(Anchor(self, AnchorPoint.TL, AnchorPoint.TL))
            else:
                button.add_constraint(Anchor(prev_button, AnchorPoint.TR, AnchorPoint.TL))
            prev_button = button

        self.menus = {}
        self.build_menus()
        self.__current_category = None

    def __show_category(self, category):
        if self.__current_category == category:
            self.__current_category = None
        else:
            self.__current_category = category

    def __run_action(self, action, arguments):
        action(*arguments)
        self.__current_category = None

    def build_menus(self):
        for category, contents in self.options.items():
            menu = self.build_menu(contents)
            menu.add_constraint(DropdownConstraint(self, self.menu_buttons[category]))
            self.menus[category] = menu

    def build_menu(self, contents):
        buttons = []
        for i, (name, func) in enumerate(contents.items()):
            if not isinstance(func, tuple):
                func = (func, ())
            button = MenuBarButton(name, self.__run_action, func, i + 1 == len(contents), True)
            button.add_constraint(MatchMaxWidth(buttons))
            buttons.append(button)

        container = Container(
            pg.Rect(0, 0, 0, 0),
            buttons,
            ContainerDirection.TOP_TO_BOTTOM,
            ContainerAlignment.LEFT_TOP
        )

        container.add_constraint(MatchMaxWidth(buttons))
        container.add_constraint(MatchSumHeights(buttons, 0))
        return container

    def handle_event(self, event: pg.event.Event) -> bool:
        for button in self.menu_buttons.values():
            if button.handle_event(event):
                return True

        if self.__current_category is not None and self.menus[self.__current_category].handle_event(event):
            return True

        if event.type == pg.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                return False
            if self.__current_category is not None and self.menus[self.__current_category].rect.collidepoint(event.pos):
                return False
            self.__current_category = None
        return False

    def _draw(self, screen: pg.Surface, *args, **kwargs) -> None:
        pg.draw.rect(screen, MENU_BAR_BUTTON_COLOR_IDLE, self.rect)
        for button in self.menu_buttons.values():
            button.draw(screen)
        bottom = self.rect.bottom + SEPARATOR_THICKNESS // 2
        left = self.rect.left
        right = self.rect.right
        pg.draw.line(screen, MENU_BAR_BORDER_COLOR, (left, bottom), (right, bottom), SEPARATOR_THICKNESS)
        if self.__current_category is not None:
            self.menus[self.__current_category].draw(screen)
