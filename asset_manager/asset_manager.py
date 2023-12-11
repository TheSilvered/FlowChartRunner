import pygame as pg
import os.path

_images = {}
_icons = {}
_fonts = {}
_asset_path = ""


def set_asset_path(path):
    global _asset_path
    _asset_path = os.path.abspath(path)


def get_asset_path(path, base_folder):
    return os.path.join(os.path.join(_asset_path, base_folder), path)


def get_image(path, is_transparent=False):
    image = _images.get(path, None)
    if image is not None:
        return image
    image = pg.image.load(get_asset_path(path, "images"))
    if is_transparent:
        image.convert_alpha()
    else:
        image.convert()
    _images[path] = image
    return image


def get_icon(path, color):
    color = tuple(color[:3])
    icon = _icons.get((path, color), None)
    if icon is not None:
        return icon
    icon = pg.image.load(get_asset_path(path, "icons"))
    icon.convert_alpha()
    for x in range(icon.get_width()):
        for y in range(icon.get_height()):
            alpha = icon.get_at((x, y))[3]
            icon.set_at((x, y), color + (alpha,))
    _icons[(path, color)] = icon
    return icon


def get_language(path):
    return get_asset_path(path, "langs")


def get_font(path, size):
    font = _fonts.get((path, size), None)
    if font is not None:
        return font
    font = pg.font.Font(get_asset_path(path, "fonts"), size)
    _fonts[(path, size)] = font
    return font
