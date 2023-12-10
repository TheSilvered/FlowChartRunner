import pygame as pg
import os.path

_images = {}
_icons = {}
_asset_path = ""


def set_asset_path(path):
    global _asset_path
    _asset_path = os.path.abspath(path)


def full_asset_path(path):
    return os.path.join(_asset_path, path)


def get_image(path, is_transparent=False):
    image = _images.get(path, None)
    if image is not None:
        return image
    image = pg.image.load(full_asset_path(path))
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
    icon = pg.image.load(full_asset_path(path))
    icon.convert_alpha()
    for x in range(icon.get_width()):
        for y in range(icon.get_height()):
            alpha = icon.get_at((x, y))[3]
            icon.set_at((x, y), color + (alpha,))
    _icons[(path, color)] = icon
    return icon
