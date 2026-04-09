import pygame
from typing import Optional, Tuple

from widgets.widget import Widget


class FrameWidget(Widget):

    def __init__(
        self,
        rect: pygame.Rect,
        name: str = "",
        sprite_path: str = "",
        corner_rect: pygame.Rect = None,  # Прямоугольник уголка на спрайте
        edge_rect: pygame.Rect = None,    # Прямоугольник линии на спрайте
    ):
        super().__init__(name)
        self.rect = rect
        self.sprite_surface = pygame.image.load(sprite_path).convert_alpha()

        self.corner_rect = corner_rect  # pygame.Rect для уголка
        self.edge_rect = edge_rect  # pygame.Rect для линии рамки

    def render(self, surface: pygame.Surface) -> None:
        if not self.sprite_surface or not self.corner_rect or not self.edge_rect:
            return

        corner_w, corner_h = self.corner_rect.size
        edge_w, edge_h = self.edge_rect.size


        top_edge = self.sprite_surface.subsurface(self.edge_rect)
        x, y, w, h = self.rect

        top_edge = self.sprite_surface.subsurface(self.edge_rect)
        for i in range(x + corner_w, x + w - corner_w, edge_w):
            # Рисуем сверху
            surface.blit(top_edge, (i, y))
            # Рисуем снизу
            surface.blit(top_edge, (i, y + h - edge_h))

        # Левая и правая линии
        left_edge = pygame.transform.rotate(top_edge, -90)
        left_edge_rect = left_edge.get_rect()
        for i in range(y + corner_h, y + h - corner_h, left_edge_rect.height):
            surface.blit(left_edge, (x, i-20))
            surface.blit(left_edge, (x + w - left_edge_rect.width, i-20))


        # Левый верхний
        surface.blit(self.sprite_surface, (x, y), self.corner_rect)
        # Правый верхний
        flipped_corner = pygame.transform.flip(self.sprite_surface.subsurface(self.corner_rect), True, False)
        surface.blit(flipped_corner, (x + w - corner_w, y))
        # Левый нижний
        flipped_corner = pygame.transform.flip(self.sprite_surface.subsurface(self.corner_rect), False, True)
        surface.blit(flipped_corner, (x, y + h - corner_h))
        # Правый нижний
        flipped_corner = pygame.transform.flip(self.sprite_surface.subsurface(self.corner_rect), True, True)
        surface.blit(flipped_corner, (x + w - corner_w, y + h - corner_h))

    def handle_event(self, event: pygame.event.Event) -> bool:
        return True

    def update(self, delta_time: float) -> None:
        return