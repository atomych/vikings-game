import pygame

from scenes.scene import Scene
from widgets.button import PushButton
from widgets.layout import Layout, VerticalLayout


class MainMenuScene(Scene):

    def __init__(self, scene_manager):
        super().__init__("Main menu", scene_manager)
        self.buttons = []
        self.backgroud_image = None
        self.backgroud_sound = None
        self.main_layout = Layout()

    def on_enter(self):
        button_start = PushButton((50, 500), (250, 80), "Старт", ui_btn_name="btn01", font_size=36)
        button_settings = PushButton((50, 600), (250, 80), "Настройки", ui_btn_name="btn01", font_size=36)
        button_exit = PushButton((50, 700), (250, 80), "Выход", ui_btn_name="btn01", font_size=36)

        button_start.on_click = lambda: self.ref_scene_manager.change_scene("Intro")
        button_exit.on_click = self.ref_scene_manager.ref_game.on_close

        self.vertical_layout = VerticalLayout((50, 500))
        self.vertical_layout.spacing = -20

        self.vertical_layout.add_child(button_start)
        self.vertical_layout.add_child(button_settings)
        self.vertical_layout.add_child(button_exit)

        self.main_layout.add_child(self.vertical_layout)

        self.backgroud_image = pygame.image.load("assets/image/mode_placeholders/2.png")


    def on_exit(self):
        del self.vertical_layout
        del self.backgroud_image


    def handle_events(self, event):
        self.main_layout.handle_event(event)

    def update(self, dt):
        self.main_layout.update(dt)

    def render(self, surface: pygame.Surface):
        surface.blit(self.backgroud_image, (0, 0))
        self.main_layout.render(surface)


