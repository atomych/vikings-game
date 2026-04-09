import random
from typing import Dict, Optional

import pygame

import utils
from game_objects.camera import Camera
from utils import iso_to_cart, cart_to_iso


class TileType:
    """Тип тайла с его свойствами"""

    def __init__(self, tile_id: int, name: str, walkable: bool, image_path: str = None):
        self.tile_id = tile_id
        self.name = name
        self.walkable = walkable
        self.image_path = image_path
        self.surface: Optional['pygame.surface.Surface'] = None

    def load_image(self):
        self.surface = pygame.image.load(self.image_path).convert_alpha()


class Map:
    """
    Компонент карты, хранящий двумерную сетку тайлов
    и обеспечивающий отрисовку в изометрической проекции
    """

    def __init__(self, rows, cols, tile_size: tuple = (256, 128)):

        self.tile_size = tile_size  # Размер тайла в пикселях (для спрайтов)

        self.rows = rows
        self.cols = cols
        # Двумерный массив индексов тайлов [y][x]
        self.tile_grid: list[list[int]] = [[0 for _ in range(0, self.cols)] for _ in range(0, self.rows)]

        # Словарь типов тайлов: tile_id -> TileType
        self.tile_types: Dict[int, TileType] = {}

        # Позиция карты в мире (изометрические координаты)
        self.offset = pygame.math.Vector2(0, 0)
        self._register_tiles()
        self.fill_random_grid(0, 1)


    def _register_tiles(self):
        self.add_tile_type(TileType(0, "Grass", True, "assets/image/Ground/Grass_3.png"))
        self.add_tile_type(TileType(1, "Dirt", True, "assets/image/Ground/Dirt_1.png"))

    def add_tile_type(self, tile_type: TileType):
        """Добавляет тип тайла"""
        self.tile_types[tile_type.tile_id] = tile_type
        tile_type.load_image()

    def set_tile(self, x: int, y: int, tile_id: int):
        """Устанавливает тайл в позицию (x, y)"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.tile_grid[y][x] = tile_id

    def get_tile(self, x: int, y: int) -> int:
        """Возвращает ID тайла в позиции (x, y)"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.tile_grid[y][x]
        return 0

    def fill_random_grid(self, min_range_val: int, max_range_val: int):
        for row in range(self.rows):
            for col in range(self.cols):
                self.tile_grid[row][col] = random.randint(min_range_val, max_range_val)

    def region_to_draw(self, row, col, reg_size):
        r_top_left = row - reg_size // 2
        c_top_left = col - reg_size // 2
        r_bot_right = r_top_left + reg_size
        c_bot_right = c_top_left + reg_size

        if r_top_left < 0:
            r_top_left = 0
        elif r_top_left > self.rows:
            r_top_left = self.rows

        if r_bot_right < 0:
            r_bot_right = 0
        elif r_bot_right > self.rows:
            r_bot_right = self.rows

        if c_top_left < 0:
            c_top_left = 0
        elif c_top_left > self.cols:
            c_top_left = self.cols

        if c_bot_right < 0:
            c_bot_right = 0
        elif c_bot_right > self.cols:
            c_bot_right = self.cols

        return (r_top_left, c_top_left, r_bot_right, c_bot_right)

    def render(self, surface: pygame.Surface, camera_offset: Optional[pygame.math.Vector2] = pygame.math.Vector2(0, 0)):

        map_offset = (self.tile_size[0] // 2, self.tile_size[1] // 2)
        self.offset = -camera_offset - map_offset if camera_offset is not None else self.offset - map_offset
        """
        iso = utils.iso_to_cart(self.offset.x, self.offset.y)
        reg = self.region_to_draw(iso[0], iso[1], 7)

        for r in range(reg[0], reg[2]):
            for c in range(reg[1], reg[3]):
                id = self.tile_grid[r][c]
                pos = utils.cart_to_iso(r, c)

                surface.blit(self.tile_types[id].surface, self.offset + pos)
        """

        for r in range(0, self.rows):
            for c in range(0, self.cols):
                id = self.tile_grid[r][c]
                pos = utils.cart_to_iso(r, c)

                surface.blit(self.tile_types[id].surface, self.offset + pos)

    def update(self, delta_time):
        pass
