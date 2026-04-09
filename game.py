import sys
import pygame

from scenes.manager import SceneManager


class Game:
    def __init__(self, width=800, height=600, name="Лесник"):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(name)
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene_manager = SceneManager(self)
        self.scene_manager.change_scene("Main menu")  # было "Game"
        self.dt = 0

    def on_close(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.handle_events()
            self.update(dt)
            self.render()
        self.cleanup()

    def update(self, dt):
        self.scene_manager.current_scene.update(dt)

    def handle_events(self):
        #метод обработки событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_close()
            self.scene_manager.current_scene.handle_events(event)

    def render(self):
        #метод отрисовки игровых объектов
        self.screen.fill((0, 0, 0))
        self.scene_manager.current_scene.render(self.screen)
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()
        sys.exit()
