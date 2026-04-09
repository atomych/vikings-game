from abc import abstractmethod, ABC
from typing import Optional, Tuple

import pygame


class Widget(ABC):
    def __init__(self, name: str = ""):
        self.name = name
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.parent: Optional['Layout'] = None
        self.surface: Optional['pygame.Surface'] = None

        self.background_color: Optional[Tuple[int, int, int, int]] = None
        self.border_color: Optional[Tuple[int, int, int, int]] = None
        self.border_width: int = 0

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Отрисовка виджета"""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий. Возвращает True, если событие обработано."""
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Обновление состояния виджета"""
        pass

    def get_absolute_rect(self) -> pygame.Rect:
        if self.parent:
            parent_rect = self.parent.get_absolute_rect()
            x = parent_rect.x + self.rect.x
            y = parent_rect.y + self.rect.y

            return pygame.Rect((x, y), self.rect.size)
        else:
            return self.rect.copy()

    def collide_to_point(self, point: Tuple[int, int]) -> bool:
        return self.get_absolute_rect().collidepoint(point)

    def collide_point_with_mask(self, point: Tuple[int, int]):
        mask = pygame.mask.from_surface(self.surface)
        return mask.get_at((point[0] - self.get_absolute_rect().x, point[1] - self.get_absolute_rect().y))

    def update_background(self):
        if self.surface is None:
            return

        self.surface.fill((0, 0, 0, 0))

        if self.background_color:
            pygame.draw.rect(self.surface, self.background_color, self.surface.get_rect())

        if self.border_color and self.border_width > 0:
            pygame.draw.rect(self.surface, self.border_color, self.surface.get_rect(), self.border_width)


