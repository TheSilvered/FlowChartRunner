import pygame as pg
from editor import Editor
from text_rendering import load_font
from asset_manager import set_asset_path, full_asset_path
from language_manager import Language


class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((1280, 720), pg.RESIZABLE)
        pg.display.set_caption("FlowChart Runner")
        set_asset_path("_assets")
        load_font()
        language = Language(full_asset_path("lang/italian.txt"))
        self.editor = Editor(language)
        self.running = True

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                break
            else:
                self.editor.handle_event(event)

    def run(self):
        while self.running:
            self.handle_events()
            self.editor.draw(self.screen)
            pg.display.update()
        pg.quit()
