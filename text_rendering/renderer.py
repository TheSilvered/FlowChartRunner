import pygame as pg
from .constants import HC_COLORS, MONO_FONT_SIZE, SELECTION_COLOR, SELECTION_NEWLINE_WIDTH
from .highlighter import highlight_text
from asset_manager import get_font

_text_cache = {}
_text_size_cache = {}

_mono_font: pg.font.Font | None = None
_ui_font: pg.font.Font | None = None


def load_fonts():
    global _mono_font, _ui_font
    _mono_font = get_font("jbm.ttf", MONO_FONT_SIZE)
    _ui_font = get_font("inter.ttf", MONO_FONT_SIZE)


def mono_line_height() -> int:
    return _mono_font.get_linesize()


def ui_line_height() -> int:
    return _ui_font.get_linesize()


def write_mono_text_hlt(text: str, *args, **kwargs):
    text = highlight_text(text)
    return _write_text(_mono_font, text, *args, **kwargs)


def write_ui_text_hlt(text: str, *args, **kwargs):
    text = highlight_text(text)
    return _write_text(_ui_font, text, *args, **kwargs)


def write_mono_text(text: str, *args, **kwargs):
    return _write_text(_mono_font, text, *args, **kwargs)


def write_ui_text(text: str, *args, **kwargs):
    return _write_text(_ui_font, text, *args, **kwargs)


def get_mono_text_size(text: str):
    return _get_text_size(text, _mono_font)


def get_ui_text_size(text: str):
    return _get_text_size(text, _ui_font)


def _write_text(
        font: pg.font.Font,
        text: str,
        align: str = "left",
        width: int = -1,
        selection_range: tuple[int, int] | None = None,
        add_newline_width: bool = False):
    lines = _parse_highlight(text)
    raw_lines = list("".join(map(lambda y: y[1], cr)) for cr in lines)
    lh = font.get_linesize()
    surf_height = len(raw_lines) * lh
    surf_width = max((font.size(line)[0] for line in raw_lines))
    if width > surf_width:
        surf_width = width
    else:
        width = -1

    surface = _text_cache.get((text, align, width, selection_range), None)
    if surface is not None:
        return surface

    if len(_text_cache) > 100:
        _text_cache.clear()

    if add_newline_width:
        surface = pg.Surface((surf_width + SELECTION_NEWLINE_WIDTH, surf_height), pg.SRCALPHA)
    else:
        surface = pg.Surface((surf_width, surf_height), pg.SRCALPHA)

    if selection_range is not None:
        _draw_selection(surface, "\n".join(raw_lines), selection_range, font)

    if align not in ("left", "right", "center"):
        raise ValueError(f"alignment {align!r} is not valid")

    for i, line in enumerate(lines):
        if align == "left":
            x = 0
        elif align == "right":
            x = surf_width - font.size(raw_lines[i])[0]
        else:
            x = (surf_width - font.size(raw_lines[i])[0]) / 2

        for cr in line:
            text_surf = font.render(cr[1], True, cr[0])
            surface.blit(text_surf, (x, lh * i))
            x += text_surf.get_width()

    _text_cache[(text, align, width, selection_range)] = surface
    return surface


def _get_text_size(text: str, font: pg.font.Font):
    size = _text_size_cache.get(text, None)
    if size is not None:
        return size

    lines = _parse_highlight(text)
    raw_lines = list("".join(map(lambda y: y[1], cr)) for cr in lines)
    lh = font.get_linesize()
    height = len(raw_lines) * lh
    width = max((font.size(line)[0] for line in raw_lines))

    _text_size_cache[text] = (width, height)
    return width, height


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


def _draw_selection(surface: pg.Surface, text: str, selection_range: tuple[int, int], font: pg.font.Font):
    text_before_selection = text[:selection_range[0]]
    text_inside_selection = text[selection_range[0]:selection_range[1]]
    lines_before = text_before_selection.count("\n")
    lines_inside = text_inside_selection.count("\n")
    line_before = text_before_selection[text_before_selection.rfind("\n") + 1:]

    line_height = font.get_linesize()

    rect_x = _get_text_size(line_before, font)[0]
    rect_y = lines_before * line_height

    if lines_inside == 0:
        rect_w = _get_text_size(text_inside_selection, font)[0]
        pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(rect_x, rect_y, rect_w, line_height))
        return

    prev_line_end = text_inside_selection.find("\n")
    rect_w = _get_text_size(text_inside_selection[:prev_line_end], font)[0] + SELECTION_NEWLINE_WIDTH
    pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(rect_x, rect_y, rect_w, line_height))

    for i in range(lines_before + 1, lines_before + lines_inside):
        rect_y = i * line_height
        next_line_end = text_inside_selection.find("\n", prev_line_end + 1)
        rect_w = _get_text_size(text_inside_selection[prev_line_end:next_line_end], font)[0] + SELECTION_NEWLINE_WIDTH
        prev_line_end = next_line_end
        pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(0, rect_y, rect_w, line_height))

    rect_w = _get_text_size(text_inside_selection[prev_line_end:], font)[0]
    rect_y = (lines_before + lines_inside) * line_height
    pg.draw.rect(surface, SELECTION_COLOR, pg.Rect(0, rect_y, rect_w, line_height))
