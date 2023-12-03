import pygame as pg
import os.path

_images = {}
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
