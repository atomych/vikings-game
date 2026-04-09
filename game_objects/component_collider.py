import pygame

import settings
from game_objects.component import Component
from game_objects.component_transform import TransformComponent
from typing import Tuple, List, Optional, Callable, Dict, Any
from enum import Enum, auto

from game_objects.gobject import GameObject
from pygame.rect import Rect


class ColliderShape(Enum):
    CIRCLE = auto()
    RECTANGLE = auto()


class CollisionBehavior(Enum):
    BLOCK = auto()  # Блокирует движение
    TRIGGER = auto()  # Вызывает событие, но не блокирует
    COLLECT = auto()  # Ресурс для сбора
    DAMAGE = auto()  # Наносит урон


class ColliderComponent(Component):

    def __init__(self,
                 shape: ColliderShape = ColliderShape.RECTANGLE,
                 size: tuple[int, int] = settings.tile_size,
                 behavior: CollisionBehavior = CollisionBehavior.BLOCK,
                 trigger_events: bool = False,
                 on_collision: Optional[Callable] = None,
                 stride=0
                 ):
        super().__init__("collider")
        self.shape = shape
        self.size = size
        self.behavior = behavior
        self.trigger_events = trigger_events
        self.on_collision = on_collision
        self.stride = stride

        self.transform: Optional[TransformComponent] = None

        self._bounds_cache: Optional[Rect] = None
        self._last_position = None




    def on_attach(self, game_object: 'GameObject') -> None:
        self.transform = game_object.get_component("transform")
        if not self.transform:
            print("Для компонента Collider прежде нужно добавить TransformComponent")

    def get_bounds(self) -> Rect:
        position = self.transform.screen_position
        pos = position + self.transform.direction.to_vector() * self.stride
        x, y = pos

        if self._bounds_cache and self._last_position == (x, y):
            return self._bounds_cache

        if self.shape == ColliderShape.CIRCLE:
            radius = self.size[0]
            if self._bounds_cache:
                self._bounds_cache.move(x - radius, y - radius)
            else:
                self._bounds_cache = Rect((x - radius, y - radius), (2 * radius, 2 * radius))
        elif self.shape == ColliderShape.RECTANGLE:

            half_w, half_h = self.size[0] / 2, self.size[1] / 2
            if self._bounds_cache:
                self._bounds_cache.topleft = (x - half_w, y - half_h)
            else:
                self._bounds_cache = Rect((x - half_w, y - half_h), self.size)

        self._last_position = (x, y)
        return self._bounds_cache

    def contains_point(self, point: Tuple[float, float],
                       position: Tuple[float, float]) -> bool:
        px, py = point
        x, y = self.transform.screen_position
        if self.shape == ColliderShape.CIRCLE:
            radius = self.size[0]
            dx, dy = px - x, py - y
            return dx * dx + dy * dy <= radius * radius

        elif self.shape == ColliderShape.RECTANGLE:
            half_w, half_h = self.size[0] / 2, self.size[1] / 2
            return (x - half_w <= px <= x + half_w and
                    y - half_h <= py <= y + half_h)

    def check_collision(self, other: 'ColliderComponent') -> bool:
        bounds1 = self.get_bounds()
        bounds2 = other.get_bounds()

        return bounds1.colliderect(bounds2)

        #if not self._bounds_intersect(bounds1, bounds2):
        #    return False
        #else:
        #    return True
        #TODO Добавить точную проверку для разных форм

    def _bounds_intersect(self, bounds1: Tuple, bounds2: Tuple) -> bool:
        x1_min, y1_min, x1_max, y1_max = bounds1
        x2_min, y2_min, x2_max, y2_max = bounds2

        return not (x1_max < x2_min or x1_min > x2_max or
                    y1_max < y2_min or y1_min > y2_max)

    def handle_collision(self, other_obj: GameObject):
        if self.on_collision:
            self.on_collision(self.parent, other_obj)

    def render(self, surface: pygame.Surface, offset: Optional[pygame.math.Vector2] = None) -> None:

        r = self.get_bounds()
        pygame.draw.rect(surface, (255, 0, 0, 255), Rect((r.x - offset.x, r.y - offset.y), (r.w, r.h)), 2)


