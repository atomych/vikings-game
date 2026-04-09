from abc import ABC
from typing import Optional, Callable
import pygame
from enum import Enum


class Component(ABC):
    def __init__(self, name: str):
        self.name = name
        self.game_object: Optional['GameObject'] = None
        self.enabled = True

    def on_attach(self, game_object: 'GameObject') -> None:
        """Вызывается при присоединении к GameObject"""
        self.game_object = game_object

    def on_detach(self) -> None:
        """Вызывается при отсоединении от GameObject"""
        self.game_object = None

    def update(self, delta_time: float) -> None:
        """Обновление логики компонента"""
        pass

    def render(self, surface: pygame.Surface, offset: Optional[pygame.math.Vector2] = None) -> None:
        """Отрисовка компонента (необязательная)"""
        pass

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий компонентом (необязательная)"""
        return False
