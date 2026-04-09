import math
from enum import Enum
import pygame

import settings
from game_objects.component import Component
import utils

from managers.event_manager import event_manager


class Direction(Enum):
    """Перечисление направлений для 8-стороннего движения"""
    N = 'N'  # Север
    NE = 'NE'  # Северо-восток
    E = 'E'  # Восток
    SE = 'SE'  # Юго-восток
    S = 'S'  # Юг
    SW = 'SW'  # Юго-запад
    W = 'W'  # Запад
    NW = 'NW'  # Северо-запад

    @classmethod
    def from_vector(cls, vector: pygame.math.Vector2) -> 'Direction':
        """Конвертирует вектор движения в направление"""
        if vector.length() == 0:
            return cls.S  # Направление по умолчанию

            # Нормализуем вектор
        normalized = vector.normalize()

        # Определяем основные направления по осям
        if normalized.y < -0.5:  # Вверх
            if normalized.x < -0.5:  # Влево
                return cls.NW
            elif normalized.x > 0.5:  # Вправо
                return cls.NE
            else:  # Прямо вверх
                return cls.N
        elif normalized.y > 0.5:  # Вниз
            if normalized.x < -0.5:  # Влево
                return cls.SW
            elif normalized.x > 0.5:  # Вправо
                return cls.SE
            else:  # Прямо вниз
                return cls.S
        else:  # Горизонтальное движение
            if normalized.x < 0:  # Влево
                return cls.W
            else:  # Вправо
                return cls.E

    def to_vector(self) -> pygame.math.Vector2:
        """Конвертирует направление в единичный вектор"""
        vectors = {
            Direction.SW: pygame.math.Vector2(-1, 1).normalize(),
            Direction.NE: pygame.math.Vector2(1, -1).normalize(),
            Direction.E: pygame.math.Vector2(1, 0),
            Direction.SE: pygame.math.Vector2(1, 1).normalize(),
            Direction.S: pygame.math.Vector2(0, 1),
            Direction.W: pygame.math.Vector2(-1, 0),
            Direction.N: pygame.math.Vector2(0, -1),
            Direction.NW: pygame.math.Vector2(-1, -1).normalize(),
        }
        return vectors[self]


class TransformComponent(Component):
    """
        Хранит позицию в экранных координатах (для отрисовки и простого движения)
    Предоставляет методы для работы с изометрическими координатами
    """

    class EventType(Enum):
        """Типы событий, специфичные для TransformComponent"""
        POSITION_CHANGED = "position_changed"
        SCALE_CHANGED = "scale_changed"
        DIRECTION_CHANGED = "direction_changed"

    def __init__(self, row: int = 0, col: int = 0):
        super().__init__("transform")
        # Позиция в экранных координатах (пиксели)
        self.set_cart(row, col)

        # Направление (для анимаций)
        self.direction = Direction.S

        self.scale = pygame.math.Vector2(1.0, 1.0)

        for event_type in self.EventType:
            event_manager.register_event_type(event_type)

    def get_cart(self) -> tuple[int, int]:
        return self.row, self.col

    def set_cart(self, row, col):
        self.row = row
        self.col = col
        pos = utils.cart_to_iso(row, col, settings.tile_size)
        self.screen_position = pygame.math.Vector2(pos)
        event_manager.emit(self.EventType.POSITION_CHANGED, self.screen_position, reuse_cache=True )

    def get_iso(self) -> pygame.math.Vector2:
        return self.screen_position

    def set_direction(self, direction: Direction):
        self.direction = direction
        event_manager.emit(self.EventType.DIRECTION_CHANGED, reuse_cache=True)

    def get_direction(self) -> Direction:
        return self.direction

    def get_screen_position(self) -> pygame.math.Vector2:
        """Возвращает экранную позицию (для отрисовки)"""
        return self.screen_position.copy()

    def set_screen_position(self, x: float, y: float):
        """Устанавливает экранную позицию"""
        self.screen_position.x = x
        self.screen_position.y = y
        self.row, self.col = utils.iso_to_cart(x, y)
        event_manager.emit(self.EventType.POSITION_CHANGED, reuse_cache=True)

    def move_screen(self, x, y):
        self.screen_position.x += x
        self.screen_position.y += y
        self.row, self.col = utils.iso_to_cart(self.screen_position.x, self.screen_position.y)
        event_manager.emit(self.EventType.POSITION_CHANGED, reuse_cache=True)
