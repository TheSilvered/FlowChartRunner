import pygame as pg
from .constants import ARROW_COLOR
from asset_manager import get_image


def draw_arrows(screen: pg.Surface, blocks, offset):
    arrow_tips = set()
    for b in blocks:
        try:
            if b.next_block is None:
                continue
            in_p_name = b.next_block.in_point
            out_p_name = b.out_point
            _draw_arrow(screen, b.rect, out_p_name, b.next_block.rect, in_p_name, offset, arrow_tips)
        except ValueError:
            if b.on_true.next_block is not None:
                in_p_name = b.on_true.next_block.in_point
                out_p_name = b.on_true.out_point
                _draw_arrow(screen, b.rect, out_p_name, b.on_true.next_block.rect, in_p_name, offset, arrow_tips)
            if b.on_false.next_block is not None:
                in_p_name = b.on_false.next_block.in_point
                out_p_name = b.on_false.out_point
                _draw_arrow(screen, b.rect, out_p_name, b.on_false.next_block.rect, in_p_name, offset, arrow_tips)

    arrow_image = get_image("arrow.png")
    for pos, rotation in arrow_tips:
        rotated_image = pg.transform.rotate(arrow_image, rotation)
        screen.blit(rotated_image, pos)


def _draw_arrow(screen, p1_rect: pg.Rect, p1_dir, p2_rect: pg.Rect, p2_dir, global_offset, arrow_tips: set):
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

    if p2_dir == "left":
        pos = (orig_p2[0] - margin + global_offset[0], orig_p2[1] - margin // 2 + global_offset[1])
        arrow_tips.add((pos, 90))
    elif p2_dir == "right":
        pos = (orig_p2[0] - margin + global_offset[0], orig_p2[1] - margin // 2 + global_offset[1])
        arrow_tips.add((pos, -90))
    elif p2_dir == "top":
        pos = (orig_p2[0] - margin//2 + 1 + global_offset[0], orig_p2[1] - margin + global_offset[1])
        arrow_tips.add((pos, 0))
    elif p2_dir == "bottom":
        pos = (orig_p2[0] - margin // 2 + global_offset[0], orig_p2[1] + global_offset[1])
        arrow_tips.add((pos, 180))
