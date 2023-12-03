import pygame as pg
from math import hypot, ceil, floor, sqrt

_rect_cache = {}
_parallelogram_cache = {}
_rombus_cache = {}
_hexagon_cache = {}

_col_type = pg.color.Color | tuple[int, int, int] | tuple[int, int, int, int] | list[int]
_point_t = tuple[float | int, float | int] | list[float | int]
_half_sqrt_2 = (2 ** 0.5) / 2


def calc_alpha(new_color: _col_type, prev_color: _col_type, alpha: float) -> list[int]:
    return [alpha * c1 + (1 - alpha) * c2 for c1, c2 in zip(new_color, prev_color)]


def draw_rect(surface: pg.Surface | None,
              rect: pg.Rect,
              color: _col_type,
              corner_radius: int = 0,
              border: int = 0,
              border_color: _col_type | None = None) -> pg.Surface:

    corner_radius = round(corner_radius)
    if corner_radius > min(rect.width, rect.height) / 2:
        corner_radius = int(min(rect.width, rect.height) / 2)

    if border > min(rect.width, rect.height) / 2:
        border = int(min(rect.width, rect.height) / 2)

    key = (rect.size, color, corner_radius, border, border_color)

    surf = _rect_cache.get(key, None)
    if surface is not None and surf is not None:
        surface.blit(surf, rect.topleft)
        return surf

    new_surf = pg.Surface(rect.size, flags=pg.SRCALPHA)
    new_surf.set_colorkey((0, 0, 0))
    line_rect = pg.Rect(0, 0, rect.w, rect.h)
    inner_rect = pg.Rect(border, border, rect.w - border*2, rect.h - border*2)
    inner_radius = corner_radius - border

    if border:
        pg.draw.rect(new_surf, border_color, line_rect, 0, corner_radius)
    pg.draw.rect(new_surf, color, inner_rect, 0, inner_radius)

    _draw_quarters(
        new_surf,
        corner_radius,
        color,
        border,
        border_color,
        rect.w,
        rect.h
    )

    if surface is not None:
        surface.blit(new_surf, rect.topleft)
    _rect_cache[key] = new_surf
    return new_surf


def _draw_quarters(surf, rad, col, border, b_col, w, h) -> None:
    in_rad = rad - border
    alpha_col = len(col) == 4
    alpha_b_col = b_col and len(b_col) == 4

    for x in range(rad):
        for y in range(rad):
            inv_x = w - x - 1
            inv_y = h - y - 1

            distance = hypot(x - rad, y - rad)

            if distance < in_rad:
                surf.set_at((x, y), col)
                surf.set_at((inv_x, y), col)
                surf.set_at((x, inv_y), col)
                surf.set_at((inv_x, inv_y), col)

            elif border and distance < in_rad + 1:
                alpha = 1 - (distance - in_rad)
                new_color = calc_alpha(col, b_col, alpha)
                surf.set_at((x, y), new_color)
                surf.set_at((inv_x, y), new_color)
                surf.set_at((x, inv_y), new_color)
                surf.set_at((inv_x, inv_y), new_color)

            elif distance < rad:
                surf.set_at((x, y), b_col)
                surf.set_at((inv_x, y), b_col)
                surf.set_at((x, inv_y), b_col)
                surf.set_at((inv_x, inv_y), b_col)

            elif distance < rad + 1:
                if border:
                    alpha = (b_col[3] if alpha_b_col else 255) * (1 - (distance - rad))
                    new_color = list(b_col[:3])
                else:
                    alpha = (col[3] if alpha_col else 255) * (1 - (distance - rad))
                    new_color = list(col[:3])
                new_color.append(alpha)

                surf.set_at((x, y), new_color)
                surf.set_at((inv_x, y), new_color)
                surf.set_at((x, inv_y), new_color)
                surf.set_at((inv_x, inv_y), new_color)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return 2

    def __getitem__(self, idx):
        if idx == 0 or idx == -2:
            return self.x
        elif idx == 1 or idx == -1:
            return self.y
        raise IndexError(f"index {idx} out of range for point")

    def __setitem__(self, idx, value):
        if idx == 0 or idx == -2:
            self.x = value
        elif idx == 1 or idx == -1:
            self.y = value
        raise IndexError(f"index {idx} out of range for point")


def draw_pixel(surf, color, ap, x, y, p1, d_x, d_y, h, max_dist, thickness):
    try:
        prev_alpha = surf.get_at((x, y))[3]
    except IndexError:
        return

    p_dist = abs(d_x * (p1.y - y) - (p1.x - x) * d_y) / h

    # the pixel is fully outside
    if p_dist > thickness + max_dist:
        return

    # the pixel is fully inside
    if p_dist + max_dist <= thickness:
        color[3] = 255 * ap
        surf.set_at((x, y), color)
        return

    if p_dist >= thickness:
        color[3] = 127 * (1 - (p_dist - thickness) / max_dist)
    else:
        color[3] = 128 + (127 * (thickness - p_dist) / max_dist)
    color[3] *= ap
    if prev_alpha > color[3]:
        return
    surf.set_at((x, y), color)


def draw_pixel_steep(surf, color, ap, x, y, p1, d_x, d_y, h, max_dist, thickness):
    try:
        prev_alpha = surf.get_at((x, y))[3]
    except IndexError:
        return

    p_dist = abs(d_x * (p1.y - x) - (p1.x - y) * d_y) / h

    # the pixel is fully outside
    if p_dist > thickness + max_dist:
        return

    # the pixel is fully inside
    if p_dist + max_dist <= thickness:
        color[3] = 255 * ap
        surf.set_at((x, y), color)
        return

    if p_dist >= thickness:
        color[3] = 127 * (1 - (p_dist - thickness) / max_dist)
    else:
        color[3] = 128 + (127 * (thickness - p_dist) / max_dist)
    color[3] *= ap
    if prev_alpha > color[3]:
        return
    surf.set_at((x, y), color)


def draw_line(surf: pg.Surface, color: _col_type, p1: _point_t, p2: _point_t, thickness: float | int):
    p1 = Point(*p1)
    p2 = Point(*p2)

    d_x = p2[0] - p1[0]
    d_y = p2[1] - p1[1]
    steep = abs(d_y) > abs(d_x)

    if steep:
        p1.x, p1.y = p1.y, p1.x
        p2.x, p2.y = p2.y, p2.x

    if p1.x > p2.x:
        p1.x, p2.x = p2.x, p1.x
        p1.y, p2.y = p2.y, p1.y

    d_x = p2[0] - p1[0]
    d_y = p2[1] - p1[1]
    max_px = int(ceil(thickness*_half_sqrt_2 + 1))

    try:
        slope = d_y / d_x
    # The points overlap
    except ZeroDivisionError:
        return

    thickness = thickness / 2
    if len(color) == 4:
        color = [color[0], color[1], color[2], 0]
        ap = color[3] / 255
    else:
        color = [color[0], color[1], color[2], 0]
        ap = 1

    max_dist = sqrt(1 + slope*slope) / 2
    h = sqrt(d_x*d_x + d_y*d_y)

    if steep:
        for y in range(floor(p1.x), ceil(p2.x + 1)):
            base_x = int(round(p1.y + int(slope * (y - p1.x))))
            draw_pixel_steep(surf, color, ap, base_x, y, p1, d_x, d_y, h, max_dist, thickness)
            for i in range(1, max_px):
                draw_pixel_steep(surf, color, ap, base_x + i, y, p1, d_x, d_y, h, max_dist, thickness)
                draw_pixel_steep(surf, color, ap, base_x - i, y, p1, d_x, d_y, h, max_dist, thickness)
    else:
        for x in range(floor(p1.x), ceil(p2.x + 1)):
            base_y = int(round(p1.y + int(slope * (x - p1.x))))
            draw_pixel(surf, color, ap, x, base_y, p1, d_x, d_y, h, max_dist, thickness)
            for i in range(1, max_px):
                draw_pixel(surf, color, ap, x, base_y + i, p1, d_x, d_y, h, max_dist, thickness)
                draw_pixel(surf, color, ap, x, base_y - i, p1, d_x, d_y, h, max_dist, thickness)


def draw_lines(surf, color, closed, points, thickness):
    points2 = list(points[1:])
    if closed:
        points2.append(points[0])
    for p1, p2 in zip(points, points2):
        draw_line(surf, color, p1, p2, thickness)


def draw_parallelogram(size: tuple[int, int], slant: int, color: _col_type, border_color: _col_type | None):
    surf = _parallelogram_cache.get((size, slant, color, border_color), None)
    if surf is not None:
        return surf

    surf = pg.Surface(size, pg.SRCALPHA)
    lines_surf = pg.Surface(size, pg.SRCALPHA)

    poly_points = [(slant, 0), (size[0] - 1, 0), (size[0] - slant, size[1] - 1), (0, size[1] - 1)]
    lines_points = [(slant + 0.5, 0.5), (size[0] - 1.5, 0.5),
                    (size[0] - slant - 0.5, size[1] - 1.5), (0.5, size[1] - 1.5)]

    pg.draw.polygon(surf, color, poly_points)
    draw_lines(lines_surf, border_color or color, True, lines_points, 2)
    surf.blit(lines_surf, (0, 0))
    _parallelogram_cache[(size, slant, color, border_color)] = surf
    return surf


def draw_rombus(size: tuple[int, int], color: _col_type, border_color: _col_type | None):
    surf = _rombus_cache.get((size, color, border_color), None)
    if surf is not None:
        return surf

    surf = pg.Surface(size, pg.SRCALPHA)
    lines_surf = pg.Surface(size, pg.SRCALPHA)

    poly_points = [(size[0] // 2, 0), (size[0] - 1, size[1] // 2), (size[0] // 2, size[1] - 1), (0, size[1] // 2)]
    lines_points = [(size[0] // 2, 0.5), (size[0] - 1.5, size[1] // 2),
                    (size[0] // 2, size[1] - 1.5), (0.5, size[1] // 2)]

    pg.draw.polygon(surf, color, poly_points)
    draw_lines(lines_surf, border_color or color, True, lines_points, 2)
    surf.blit(lines_surf, (0, 0))
    _rombus_cache[(size, color, border_color)] = surf
    return surf


def draw_hexagon(size: tuple[int, int], slant: int, color: _col_type, border_color: _col_type | None):
    surf = _hexagon_cache.get((size, slant, color, border_color), None)
    if surf is not None:
        return surf

    surf = pg.Surface(size, pg.SRCALPHA)
    lines_surf = pg.Surface(size, pg.SRCALPHA)

    poly_points = [(slant, 0), (size[0] - slant - 1, 0), (size[0] - 1, size[1] // 2),
                   (size[0] - slant - 1, size[1] - 1), (slant, size[1] - 1), (0, size[1] // 2)]
    lines_points = [(slant, 0.5), (size[0] - slant - 1.5, 0.5), (size[0] - 1.5, size[1] // 2),
                    (size[0] - slant - 1.5, size[1] - 1.5), (slant, size[1] - 1.5), (0.5, size[1] // 2)]

    pg.draw.polygon(surf, color, poly_points)
    draw_lines(lines_surf, border_color or color, True, lines_points, 2)
    surf.blit(lines_surf, (0, 0))
    _hexagon_cache[(size, slant, color, border_color)] = surf
    return surf
