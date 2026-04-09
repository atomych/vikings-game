import random
from typing import Dict, Optional, List, Set, Tuple

import pygame

import settings
import utils
from game_objects.camera import Camera
from game_objects.gobject import GameObject
from game_objects.component_collider import CollisionBehavior
from uuid import UUID


class TileType:
    """Тип тайла с его свойствами"""

    def __init__(self, tile_id: int, name: str, walkable: bool, image_path: str = None, walkable_speed: float = 1):
        self.tile_id = tile_id
        self.name = name
        self.is_walkable = walkable
        self.walkable_speed = walkable_speed
        self.image_path = image_path
        self.surface: Optional['pygame.surface.Surface'] = None

    def load_image(self):
        self.surface = pygame.image.load(self.image_path).convert_alpha()


class Map:
    def __init__(self, rows, cols, tile_size: tuple = (256, 128)):

        self.tile_size = tile_size
        self.rows = rows
        self.cols = cols

        self.tile_grid: list[list[int]] = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.walk_grid: list[list[float]] = [[1 for _ in range(cols)] for _ in range(rows)]
        self.static_objects: list[list[Optional['GameObject']]] = [[None for _ in range(cols)] for _ in range(rows)]

        self.all_static_objects: Set[GameObject] = set()
        self.all_dynamic_objects: Set[GameObject] = set()
        self.render_stack: List[Tuple[UUID, int, GameObject]] = []

        self.tile_types: Dict[float, TileType] = {}

        self._register_tiles()
        self.fill_random_grid(0, 1)

    def is_walkable(self, row: int, col: int) -> bool:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        if self.walk_grid[row][col] == 0:
            return False
        return True

    def add_static_object(self, game_object: GameObject, row: int, col: int):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return

        transform = game_object.get_component("transform")
        if transform:
            transform.set_cart(row, col)
            self.static_objects[row][col] = game_object
            self.all_static_objects.add(game_object)

            if game_object.name == "House":
                for i in range(3):
                    for j in range(3):
                        if 0 <= row + i + 1 < self.rows and 0 <= col - j < self.cols:
                            self.walk_grid[row + i + 1][col - j] = 0

    def add_dinamic_object(self, game_object: GameObject, row: int, col: int):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        game_object.get_component("transform").set_cart(row, col)
        self.all_dynamic_objects.add(game_object)

    def _register_tiles(self):
        self.add_tile_type(TileType(0, "Grass", True, "assets/image/Ground/Grass_3.png"))
        self.add_tile_type(TileType(1, "Dirt", True, "assets/image/Ground/Dirt_1.png"))

    def add_tile_type(self, tile_type: TileType):
        self.tile_types[tile_type.tile_id] = tile_type
        tile_type.load_image()

    def set_tile(self, x: int, y: int, tile_id: int):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.tile_grid[y][x] = tile_id

    def get_tile(self, x: int, y: int) -> int:
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.tile_grid[y][x]
        return 0

    def fill_random_grid(self, min_range_val: int, max_range_val: int):
        for row in range(self.rows):
            for col in range(self.cols):
                self.tile_grid[row][col] = random.randint(min_range_val, max_range_val)

    def region_to_draw(self, row, col, reg_size):
        r_top_left = max(0, row - reg_size // 2)
        c_top_left = max(0, col - reg_size // 2)
        r_bot_right = min(self.rows, r_top_left + reg_size)
        c_bot_right = min(self.cols, c_top_left + reg_size)
        return r_top_left, c_top_left, r_bot_right, c_bot_right

    def update_render_stack(self, row, col, offset):
        rtl, ctl, rbr, cbr = self.region_to_draw(row, col, 17)
        for r in range(rtl, rbr):
            for c in range(ctl, cbr):
                z = utils.z_stack_value(r, c) - offset.y
                if self.static_objects[r][c]:
                    self.render_stack.append((self.static_objects[r][c].id, z, self.static_objects[r][c]))

        for obj in self.all_dynamic_objects:
            if obj:
                x, y = obj.get_component('transform').screen_position
                z = y - offset.y
                self.render_stack.append((obj.id, z, obj))

        self.render_stack.sort(key=lambda item: item[1])

    def render(self, surface: pygame.Surface, offset: Optional[pygame.math.Vector2] = pygame.math.Vector2(0, 0)):
        map_offset = (self.tile_size[0] // 2, self.tile_size[1] // 2)
        self.offset = -offset - map_offset if offset is not None else self.offset - map_offset
        r, c = utils.iso_to_cart(offset.x + settings.screen_width // 2, offset.y + settings.screen_height // 2)

        self.update_render_stack(r, c, offset)

        # ── Рисуем тайлы с отступом за границы карты ─────────────────────────
        # Тайлы вне карты рисуются как трава — так не будет чёрной рамки
        screen_w, screen_h = surface.get_size()
        grass_surf = self.tile_types[0].surface
        extra = 6   # сколько тайлов рисовать за пределами видимой области

        reg = self.region_to_draw(r, c, 17)
        r_min = reg[0] - extra
        c_min = reg[1] - extra
        r_max = reg[2] + extra
        c_max = reg[3] + extra

        for draw_r in range(r_min, r_max):
            for draw_c in range(c_min, c_max):
                if 0 <= draw_r < self.rows and 0 <= draw_c < self.cols:
                    tile_surf = self.tile_types[self.tile_grid[draw_r][draw_c]].surface
                else:
                    tile_surf = grass_surf  # за границей карты — трава

                pos = utils.cart_to_iso(draw_r, draw_c)
                screen_pos = self.offset + pos

                # Отсечение тайлов вне экрана
                if (screen_pos[0] > screen_w or screen_pos[1] > screen_h or
                        screen_pos[0] < -self.tile_size[0] or screen_pos[1] < -self.tile_size[1]):
                    continue

                surface.blit(tile_surf, screen_pos)

        # ── Рисуем объекты в порядке z-буфера ────────────────────────────────
        for _, _, obj in self.render_stack:
            if obj:
                obj.render(surface, offset)

        self.render_stack.clear()

    def update(self, delta_time):
        for obj in self.all_dynamic_objects:
            obj.update(delta_time)