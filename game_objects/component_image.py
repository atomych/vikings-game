from typing import Optional

import pygame

from game_objects.component import Component


class ImageComponent(Component):
    def __init__(self, filename, offset: tuple = (0, 0)):
        super().__init__("image")
        self.surface = pygame.image.load(filename).convert_alpha()
        self.transform: Optional['TransformComponent'] = None
        self.offset: pygame.math.Vector2 = pygame.math.Vector2(offset)

    def on_attach(self, game_object: 'GameObject') -> None:
        super().on_attach(game_object)
        self.transform = game_object.get_component("transform")
        if self.transform is None:
            print(f"Не найден компонент для позиционирования в GameObject: {game_object.name}")

    def render(self, surface: pygame.Surface,  offset) -> None:
        if self.enabled and self.surface:
            pos = self.transform.get_screen_position() + self.offset - offset
            surface.blit(self.surface, pos)


