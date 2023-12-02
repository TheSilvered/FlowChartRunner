from blocks import BlockBase, StartBlock, BlockState
from constants import (
    SELECTION_BORDER_COLOR, ARROW_COLOR, INFO_BG_DARK, INFO_BG_LIGHT, GUIDELINE_COLOR, AXIS_COLOR, BLOCK_BORDER_COLOR,
    PROPERTY_NAME_COL_WIDTH, PROPERTY_VALUE_COL_WIDTH, PROPERTY_H_PADDING, PROPERTY_V_PADDING
)
from draw_utils import write_text, line_height, get_image
import pygame as pg
from textbox import TextBox


class Editor:
    def __init__(self, start_block: StartBlock):
        self.blocks = []
        self.__add_blocks(start_block)
        self.dragging_blocks: list[BlockBase] | None = None
        self.has_moved = False
        self.dragging_global = False
        self.selecting = False
        self.select_start = (0, 0)
        self.select_area = pg.Rect(-1, -1, 0, 0)
        self.selected_blocks: list[BlockBase] = []
        self.global_offset = [0, 0]
        self.test_textbox = TextBox(pg.Rect(100, 100, 300, 500), None, None, False, False)

        self.test_textbox.text = "dup = 2 * sin(a) * cos(a)"

        y = 20
        for i, block in enumerate(self.blocks):
            block_size = block.get_size()
            block.pos = (10 * i + 30, y)
            y += block_size[1] + 40

    def __add_blocks(self, start_block):
        block_set = set()
        queue = [start_block]
        for block in queue:
            if block in block_set:
                continue
            self.blocks.append(block)
            block_set.add(block)
            for next_block in block.next_block:
                queue.append(next_block)

    def intersect_point(self, point) -> BlockBase | None:
        for b in reversed(self.blocks):
            if b.rect.collidepoint(point):
                return b
        return None

    def intersect_all_point(self, point) -> list[BlockBase]:
        blocks = []
        for b in reversed(self.blocks):
            if b.rect.collidepoint(point):
                blocks.append(b)
        return blocks

    def intersect_rect(self, rect: pg.Rect) -> BlockBase | None:
        for b in reversed(self.blocks):
            if b.inside(rect):
                return b
        return None

    def intersect_all_rect(self, rect: pg.Rect) -> list[BlockBase]:
        blocks = []
        for b in self.blocks:
            if b.inside(rect):
                blocks.append(b)
        return blocks

    def update_select_area(self):
        mp = pg.mouse.get_pos()
        self.select_area = pg.Rect(
            min(self.select_start[0], mp[0]),
            min(self.select_start[1], mp[1]),
            abs(self.select_start[0] - mp[0]),
            abs(self.select_start[1] - mp[1])
        )

    def handle_event(self, event: pg.event.Event):
        if self.test_textbox.focused:
            self.test_textbox.handle_event(event)
            return

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                block = self.intersect_point(event.pos)
                if block is not None:
                    if block not in self.selected_blocks:
                        self.selected_blocks = [block]
                    self.dragging_blocks = self.selected_blocks
                    return
                self.selected_blocks = []
                self.selecting = True
                self.select_start = event.pos
                self.select_area = pg.Rect(event.pos, (0, 0))
            elif event.button == pg.BUTTON_RIGHT:
                self.dragging_global = True
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == pg.BUTTON_LEFT:
                if self.selecting:
                    self.selected_blocks = self.intersect_all_rect(self.select_area)
                elif not self.has_moved:
                    block = self.intersect_point(event.pos)
                    if block is not None:
                        self.selected_blocks = [block]
                self.selecting = False
                self.dragging_blocks = None
                self.has_moved = False
            elif event.button == pg.BUTTON_RIGHT:
                self.dragging_global = False
        elif event.type == pg.MOUSEMOTION:
            if self.dragging_blocks is not None:
                self.has_moved = True
                for block in self.dragging_blocks:
                    block.add_pos(event.rel)
            elif self.dragging_global:
                for block in self.blocks:
                    block.add_pos(event.rel)
                self.global_offset[0] += event.rel[0]
                self.global_offset[1] += event.rel[1]
            elif self.selecting:
                self.update_select_area()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_t:
                self.test_textbox.focused = True
                return
            if len(self.selected_blocks) != 1:
                return

            block = self.selected_blocks[0]
            if event.key == pg.K_UP:
                block.out_point[0] = "top"
            elif event.key == pg.K_DOWN:
                block.out_point[0] = "bottom"
            elif event.key == pg.K_LEFT:
                block.out_point[0] = "left"
            elif event.key == pg.K_RIGHT:
                block.out_point[0] = "right"
            elif event.key == pg.K_KP8:
                block.in_point = "top"
            elif event.key == pg.K_KP2:
                block.in_point = "bottom"
            elif event.key == pg.K_KP4:
                block.in_point = "left"
            elif event.key == pg.K_KP6:
                block.in_point = "right"

    @staticmethod
    def draw_arrow(screen, p1_rect: pg.Rect, p1_dir, p2_rect: pg.Rect, p2_dir):
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

        pg.draw.line(screen, ARROW_COLOR, p1, orig_p1, 2)
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
        pg.draw.lines(screen, ARROW_COLOR, False, points, 2)

        arrow_image = get_image("arrow.png")
        if p2_dir == "left":
            arrow_image = pg.transform.rotate(arrow_image, 90)
            screen.blit(arrow_image, (orig_p2[0] - margin, orig_p2[1] - margin // 2))
        elif p2_dir == "right":
            arrow_image = pg.transform.rotate(arrow_image, -90)
            screen.blit(arrow_image, (orig_p2[0], orig_p2[1] - margin // 2 + 1))
        elif p2_dir == "top":
            screen.blit(arrow_image, (orig_p2[0] - margin // 2 + 1, orig_p2[1] - margin))
        elif p2_dir == "bottom":
            arrow_image = pg.transform.rotate(arrow_image, 180)
            screen.blit(arrow_image, (orig_p2[0] - margin // 2, orig_p2[1]))

    def draw_arrows(self, screen):
        for b in self.blocks:
            for i, nb in enumerate(b.next_block):
                in_p_name = nb.in_point
                out_p_name = b.out_point[i]
                self.draw_arrow(screen, b.rect, out_p_name, nb.rect, in_p_name)

    def draw_block_info(self, block, screen):
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        property_name_col = pg.Rect(
            screen_w - PROPERTY_NAME_COL_WIDTH - PROPERTY_VALUE_COL_WIDTH, 0,
            PROPERTY_NAME_COL_WIDTH, screen_h)
        property_value_col = pg.Rect(
            screen_w - PROPERTY_VALUE_COL_WIDTH, 0,
            PROPERTY_VALUE_COL_WIDTH, screen_h)
        lh = line_height() + PROPERTY_V_PADDING * 2

        properties = [
            ("Type", block.__class__.__name__),
            ("Position", f"x: {block.pos[0] - self.global_offset[0]}, y: {block.pos[1] - self.global_offset[1]}"),
            ("Size", f"w: {block.get_size()[0]}, h: {block.get_size()[1]}"),
        ]

        for i, (p_name, p_val) in enumerate(properties):
            line_rect = pg.Rect(property_name_col.x, lh * i, property_name_col.w + property_value_col.w, lh)
            if i % 2 == 0:
                pg.draw.rect(screen, INFO_BG_DARK, line_rect)
            else:
                pg.draw.rect(screen, INFO_BG_LIGHT, line_rect)

            p_name_surf = write_text(p_name)
            p_val_surf = write_text(p_val)
            p_name_rect = pg.Rect(0, 0, property_name_col.w, lh)
            p_val_rect = pg.Rect(0, 0, property_value_col.w, lh)
            screen.blit(
                p_name_surf,
                (property_name_col.x + PROPERTY_H_PADDING, lh * i + PROPERTY_V_PADDING),
                p_name_rect
            )
            screen.blit(
                p_val_surf,
                (property_value_col.x + PROPERTY_H_PADDING, lh * i + PROPERTY_V_PADDING),
                p_val_rect
            )

        pg.draw.rect(
            surface=screen,
            color=BLOCK_BORDER_COLOR,
            rect=pg.Rect(
                property_name_col.x - 2, -2,
                PROPERTY_NAME_COL_WIDTH + PROPERTY_VALUE_COL_WIDTH + 4, len(properties) * lh + 4),
            width=2
        )

    def draw(self, screen: pg.Surface):
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        offset_x = self.global_offset[0] % 50
        offset_y = self.global_offset[1] % 50

        if 0 <= self.global_offset[1] <= screen_w:
            pg.draw.line(screen, AXIS_COLOR, (0, self.global_offset[1]), (screen_w, self.global_offset[1]))
        if 0 <= self.global_offset[0] <= screen_w:
            pg.draw.line(screen, AXIS_COLOR, (self.global_offset[0], 0), (self.global_offset[0], screen_h))

        for x in range(offset_x, screen_w + offset_x, 50):
            for y in range(offset_y, screen_h + offset_y, 50):
                screen.set_at((x, y), GUIDELINE_COLOR)

        self.draw_arrows(screen)
        for block in self.blocks:
            block.draw(screen, BlockState.SELECTED if block in self.selected_blocks else BlockState.IDLE)

        if len(self.selected_blocks) == 1:
            self.draw_block_info(self.selected_blocks[0], screen)

        if self.selecting:
            pg.draw.rect(screen, SELECTION_BORDER_COLOR, self.select_area, 1)

        self.test_textbox.draw(screen)
