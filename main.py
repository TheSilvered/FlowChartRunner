import sys
from constants import EDITOR_BG_COLOR
from blocks import *
from editor import Editor


def main():
    pg.init()
    screen = pg.display.set_mode((1280, 720), pg.RESIZABLE)
    pg.display.set_caption("FlowChart Runner")
    load_font()

    start_block = StartBlock()
    io_block = IOBlock(start_block, "", True)
    EndBlock(io_block)

    editor = Editor(start_block)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            else:
                editor.handle_event(event)

        screen.fill(EDITOR_BG_COLOR)
        editor.draw(screen)
        pg.display.update()


if __name__ == "__main__":
    main()
