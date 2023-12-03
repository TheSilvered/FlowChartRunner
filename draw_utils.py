import pygame as pg
from math import hypot, ceil, floor, sqrt
from constants import HC_COLORS, FONT_SIZE, ARROW_COLOR, SELECTION_COLOR, SELECTION_NEWLINE_WIDTH
from highlighter import highlight_text


_rect_cache = {}
_text_cache = {}
_parallelogram_cache = {}
_rombus_cache = {}
_hexagon_cache = {}
_text_size_cache = {}
_images = {}

_col_type = pg.color.Color | tuple[int, int, int] | tuple[int, int, int, int] | list[int]
_point_t = tuple[float | int, float | int] | list[float | int]
_half_sqrt_2 = (2 ** 0.5) / 2

_font: pg.font.Font | None = None


def load_font():
    global _font
    _font = pg.font.Font("jbm.ttf", FONT_SIZE)


def calc_alpha(new_color: _col_type, prev_color: _col_type, alpha: float) -> list[int]:
    return [alpha * c1 + (1 - alpha) * c2 for c1, c2 in zip(new_color, prev_color)]


def aa_rect(surface: pg.Surface | None,
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


def line_height() -> int:
    return _font.get_linesize()


def write_text_highlighted(
        text: str,
        align: str = "left",
        width: int = -1,
        selection_range: tuple[int, int] | None = None,
        add_newline_width: bool = False):
    text = highlight_text(text)
    return write_text(text, align, width, selection_range, add_newline_width)


def _parse_highlight(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    color_ranges = text.split("~c`")
    color_ranges = [(HC_COLORS["default"], color_ranges[0])] \
                 + [(HC_COLORS.get(r[0], HC_COLORS["default"]), r[1:]) for r in color_ranges[1:] if r]

    final_lines = []
    current_line = []
    for cr in color_ranges:
        lines = cr[1].split("\n")
        current_line.append((cr[0], lines[0]))

        for line in lines[1:]:
            final_lines.append(current_line)
            current_line = [(cr[0], line)]

    if len(current_line) != 0:
        final_lines.append(current_line)

    return final_lines


def draw_selection(surface: pg.Surface, text: str, selection_range: tuple[int, int]):
    text_before_selection = text[:selection_range[0]]
    text_inside_selection = text[selection_range[0]:selection_range[1]]
    lines_before = text_before_selection.count("\n")
    lines_inside = text_inside_selection.count("\n")
    line_before = text_before_selection[text_before_selection.rfind("\n") + 1:]

    rect_x = get_text_size(line_before)[0]
    rect_y = lines_before * line_height()

    if lines_inside == 0:
        rect_w = get_text_size(text_inside_selection)[0]
        pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(rect_x, rect_y, rect_w, line_height()))
        return

    prev_line_end = text_inside_selection.find("\n")
    rect_w = get_text_size(text_inside_selection[:prev_line_end])[0] + SELECTION_NEWLINE_WIDTH
    pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(rect_x, rect_y, rect_w, line_height()))

    for i in range(lines_before + 1, lines_before + lines_inside):
        rect_y = i * line_height()
        next_line_end = text_inside_selection.find("\n", prev_line_end + 1)
        rect_w = get_text_size(text_inside_selection[prev_line_end:next_line_end])[0] + SELECTION_NEWLINE_WIDTH
        prev_line_end = next_line_end
        pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(0, rect_y, rect_w, line_height()))

    rect_w = get_text_size(text_inside_selection[prev_line_end:])[0]
    rect_y = (lines_before + lines_inside) * line_height()
    pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(0, rect_y, rect_w, line_height()))


def write_text(
        text: str,
        align: str = "left",
        width: int = -1,
        selection_range: tuple[int, int] | None = None,
        add_newline_width: bool = False):
    lines = _parse_highlight(text)
    raw_lines = list("".join(map(lambda y: y[1], cr)) for cr in lines)
    lh = _font.get_linesize()
    surf_height = len(raw_lines) * lh
    surf_width = max((_font.size(line)[0] for line in raw_lines))
    if width > surf_width:
        surf_width = width
    else:
        width = -1

    surface = _text_cache.get((text, align, width, selection_range), None)
    if surface is not None:
        return surface
    if add_newline_width:
        surface = pg.Surface((surf_width + SELECTION_NEWLINE_WIDTH, surf_height), pg.SRCALPHA)
    else:
        surface = pg.Surface((surf_width, surf_height), pg.SRCALPHA)

    if selection_range is not None:
        draw_selection(surface, "\n".join(raw_lines), selection_range)

    if align not in ("left", "right", "center"):
        raise ValueError(f"alignment {align!r} is not valid")

    for i, line in enumerate(lines):
        if align == "left":
            x = 0
        elif align == "right":
            x = surf_width - _font.size(raw_lines[i])[0]
        else:
            x = (surf_width - _font.size(raw_lines[i])[0]) / 2

        for cr in line:
            text_surf = _font.render(cr[1], True, cr[0])
            surface.blit(text_surf, (x, lh * i))
            x += text_surf.get_width()

    _text_cache[(text, align, width, selection_range)] = surface
    return surface


def get_text_size(text: str):
    size = _text_size_cache.get(text, None)
    if size is not None:
        return size

    lines = _parse_highlight(text)
    raw_lines = list("".join(map(lambda y: y[1], cr)) for cr in lines)
    lh = _font.get_linesize()
    height = len(raw_lines) * lh
    width = max((_font.size(line)[0] for line in raw_lines))

    if text == "":
        print("Hello")
    _text_size_cache[text] = (width, height)
    return width, height


def get_image(path, is_transparent=False):
    image = _images.get(path, None)
    if image is not None:
        return image
    image = pg.image.load(path)
    if is_transparent:
        image.convert_alpha()
    else:
        image.convert()
    return image


def draw_arrow(screen, p1_rect: pg.Rect, p1_dir, p2_rect: pg.Rect, p2_dir, global_offset):
    p1 = list(getattr(p1_rect, "mid" + p1_dir))
    p2 = list(getattr(p2_rect, "mid" + p2_dir))
    margin = 15

    orig_p1 = p1.copy()
    if p1_dir == "left":
        p1[0] -= margin
    elif p1_dir == "right":
        p1[0] += margin
    elif p1_dir == "top":
        p1[1] -= margin
    elif p1_dir == "bottom":
        p1[1] += margin

    orig_p2 = p2.copy()
    if p2_dir == "left":
        p2[0] -= margin
    elif p2_dir == "right":
        p2[0] += margin
    elif p2_dir == "top":
        p2[1] -= margin
    elif p2_dir == "bottom":
        p2[1] += margin

    pg.draw.line(
        screen,
        ARROW_COLOR,
        (p1[0] + global_offset[0], p1[1] + global_offset[1]),
        (orig_p1[0] + global_offset[0], orig_p1[1] + global_offset[1]),
        2
    )
    points = [p1]
    inverted = False

    if (p1_dir == "right" and p2_dir == "left") or (p1_dir == "top" and p2_dir == "left") or \
       (p1_dir == "bottom" and p2_dir == "left") or (p1_dir == "top" and p2_dir == "right") or \
       (p1_dir == "bottom" and p2_dir == "right") or (p1_dir == "bottom" and p2_dir == "top"):
        p1, p2 = p2, p1
        p1_rect, p2_rect = p2_rect, p1_rect
        p1_dir, p2_dir = p2_dir, p1_dir
        inverted = True

    if p1_dir == p2_dir == "left":
        if p1[0] < p2[0]:
            p_x = (p2[0] - p1_rect.right) // 2 + p1_rect.right
            p_y = min(p2[1], p1_rect.top - margin) if p1[1] > p2[1] else max(p2[1], p1_rect.bottom + margin)
            points += [(p1[0], p_y), (p_x, p_y), (p_x, p2[1])]
        else:
            p_x = (p1[0] - p2_rect.right) // 2 + p2_rect.right
            p_y = min(p1[1], p2_rect.top - margin) if p1[1] < p2[1] else max(p1[1], p2_rect.bottom + margin)
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]

    elif p1_dir == p2_dir == "right":
        if p1[0] > p2[0]:
            p_x = (p1[0] - p2_rect.left) // 2 + p2_rect.left
            p_y = min(p2[1], p1_rect.top - margin) if p1[1] > p2[1] else max(p2[1], p1_rect.bottom + margin)
            points += [(p1[0], p_y), (p_x, p_y), (p_x, p2[1])]
        else:
            p_x = (p2[0] - p1_rect.left) // 2 + p1_rect.left
            p_y = min(p1[1], p2_rect.top - margin) if p1[1] < p2[1] else max(p1[1], p2_rect.bottom + margin)
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]

    elif p1_dir == p2_dir == "top":
        if p1[1] < p2[1]:
            p_x = min(p2[0], p1_rect.left - margin) if p1[0] > p2[0] else max(p2[0], p1_rect.right + margin)
            p_y = (p2[1] - p1_rect.bottom) // 2 + p1_rect.bottom
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]
        else:
            p_x = min(p1[0], p2_rect.left - margin) if p1[0] < p2[0] else max(p1[0], p2_rect.right + margin)
            p_y = (p1[1] - p2_rect.bottom) // 2 + p2_rect.bottom
            points += [(p1[0], p_y), (p_x, p_y), (p_x, p2[1])]

    elif p1_dir == p2_dir == "bottom":
        if p1[1] < p2[1]:
            p_x = min(p1[0], p2_rect.left - margin) if p1[0] < p2[0] else max(p1[0], p2_rect.right + margin)
            p_y = (p2_rect.top - p1[1]) // 2 + p1[1]
            points += [(p1[0], p_y), (p_x, p_y), (p_x, p2[1])]
        else:
            p_x = min(p2[0], p1_rect.left - margin) if p1[0] > p2[0] else max(p2[0], p1_rect.right + margin)
            p_y = (p2[1] - p1_rect.top) // 2 + p1_rect.top
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]

    elif p1_dir == "left" and p2_dir == "right":
        if p1[0] > p2[0]:
            points += [(p1[0] + (p2[0] - p1[0]) // 2, p1[1]), (p1[0] + (p2[0] - p1[0]) // 2, p2[1])]
        elif p1_rect.top - p2_rect.bottom >= 4 or p2_rect.top - p1_rect.bottom >= 4:
            points += [(p1[0], p1[1] + (p2[1] - p1[1]) // 2), (p2[0], p1[1] + (p2[1] - p1[1]) // 2)]
        else:
            p_x = max(p1_rect.right, p2_rect.right) + margin
            p_y = max(p1_rect.bottom, p2_rect.bottom) + margin
            points += [(p1[0], p_y), (p_x, p_y), (p_x, p2[1])]

    elif p1_dir == "left" and p2_dir == "top":
        if p1[0] > p2[0] and p1[1] < p2[1]:
            points += [(p2[0], p1[1])]
        elif p1_rect.left - p2_rect.right > margin:
            p_x = (p1[0] - p2_rect.right) // 2 + p2_rect.right
            points += [(p_x, p1[1]), (p_x, p2[1])]
        elif p2_rect.top - p1_rect.bottom > margin:
            p_y = (p2[1] - p1_rect.bottom) // 2 + p1_rect.bottom
            points += [(p1[0], p_y), (p2[0], p_y)]
        else:
            p_x = min(p1_rect.left, p2_rect.left) - margin
            p_y = min(p1_rect.top, p2_rect.top) - margin
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]

    elif p1_dir == "left" and p2_dir == "bottom":
        if p1[0] > p2[0] and p1[1] > p2[1]:
            points += [(p2[0], p1[1])]
        elif p1_rect.left - p2_rect.right > margin:
            p_x = (p1[0] - p2_rect.right) // 2 + p2_rect.right
            points += [(p_x, p1[1]), (p_x, p2[1])]
        elif p1_rect.top - p2_rect.bottom > margin:
            p_y = (p1_rect.top - p2[1]) // 2 + p2[1]
            points += [(p1[0], p_y), (p2[0], p_y)]
        else:
            p_x = min(p1_rect.left, p2_rect.left) - margin
            p_y = max(p1_rect.bottom, p2_rect.bottom) + margin
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]

    elif p1_dir == "right" and p2_dir == "top":
        if p1[0] < p2[0] and p1[1] < p2[1]:
            points += [(p2[0], p1[1])]
        elif p2_rect.left - p1_rect.right > margin:
            p_x = (p2_rect.left - p1[0]) // 2 + p1[0]
            points += [(p_x, p1[1]), (p_x, p2[1])]
        elif p2_rect.top - p1_rect.bottom > margin:
            p_y = (p2[1] - p1_rect.bottom) // 2 + p1_rect.bottom
            points += [(p1[0], p_y), (p2[0], p_y)]
        else:
            p_x = max(p1_rect.right, p2_rect.right) + margin
            p_y = min(p1_rect.top, p2_rect.top) - margin
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]

    elif p1_dir == "right" and p2_dir == "bottom":
        if p1[0] < p2[0] and p1[1] > p2[1]:
            points += [(p2[0], p1[1])]
        elif p2_rect.left - p1_rect.right > margin:
            p_x = (p2_rect.left - p1[0]) // 2 + p1[0]
            points += [(p_x, p1[1]), (p_x, p2[1])]
        elif p1_rect.top - p2_rect.bottom > margin:
            p_y = (p1_rect.top - p2[1]) // 2 + p2[1]
            points += [(p1[0], p_y), (p2[0], p_y)]
        else:
            p_x = max(p1_rect.right, p2_rect.right) + margin
            p_y = max(p1_rect.bottom, p2_rect.bottom) + margin
            points += [(p_x, p1[1]), (p_x, p_y), (p2[0], p_y)]

    elif p1_dir == "top" and p2_dir == "bottom":
        if p1[1] > p2[1]:
            points += [(p1[0], p1[1] + (p2[1] - p1[1]) // 2), (p2[0], p1[1] + (p2[1] - p1[1]) // 2)]
        elif p1_rect.left - p2_rect.right >= 4 or p2_rect.left - p1_rect.right >= 4:
            points += [(p1[0] + (p2[0] - p1[0]) // 2, p1[1]), (p1[0] + (p2[0] - p1[0]) // 2, p2[1])]
        else:
            p_x = max(p1_rect.right, p2_rect.right) + margin
            p_y = min(p1_rect.top, p2_rect.top) - margin
            points += [(p1[0], p_y), (p_x, p_y), (p_x, p2[1])]

    if inverted:
        points += [p1]
        points[0], points[-1] = points[-1], points[0]
        p1_dir, p2_dir = p2_dir, p1_dir
    else:
        points += [p2]
    for i in range(len(points)):
        points[i] = [points[i][0] + global_offset[0], points[i][1] + global_offset[1]]
    pg.draw.lines(screen, ARROW_COLOR, False, points, 2)

    arrow_image = get_image("arrow.png")
    if p2_dir == "left":
        arrow_image = pg.transform.rotate(arrow_image, 90)
        screen.blit(arrow_image, (orig_p2[0] - margin + global_offset[0], orig_p2[1] - margin // 2 + global_offset[1]))
    elif p2_dir == "right":
        arrow_image = pg.transform.rotate(arrow_image, -90)
        screen.blit(arrow_image, (orig_p2[0] + global_offset[0], orig_p2[1] - margin // 2 + 1 + global_offset[1]))
    elif p2_dir == "top":
        screen.blit(arrow_image, (orig_p2[0] - margin // 2 + 1 + global_offset[0], orig_p2[1] - margin + global_offset[1]))
    elif p2_dir == "bottom":
        arrow_image = pg.transform.rotate(arrow_image, 180)
        screen.blit(arrow_image, (orig_p2[0] - margin // 2 + global_offset[0], orig_p2[1] + global_offset[1]))
