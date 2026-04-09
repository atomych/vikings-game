from __future__ import annotations

from typing import List, Optional
import pygame

import settings
from fx_effect import FXPool
from game_objects.camera import Camera
from game_objects.gobject import GameObject
from game_objects.ground import Map
from game_objects.player import Player, Enemy, House, Tree
from scenes.scene import Scene

# ── Константы ──────────────────────────────────────────────────────────────
MAP_SIZE      = 25

HOUSE_ROW     = 8
HOUSE_COL     = 8

FENCE_R_MIN   = HOUSE_ROW
FENCE_R_MAX   = HOUSE_ROW + 4
FENCE_C_MIN   = HOUSE_COL - 3
FENCE_C_MAX   = HOUSE_COL + 1
FENCE_ENTRANCE = (FENCE_R_MAX, (FENCE_C_MIN + FENCE_C_MAX) // 2)   # (12, 7)

PLAYER_START  = (FENCE_ENTRANCE[0] + 2, FENCE_ENTRANCE[1])

ENEMY_CONFIGS = [
    {"row": 3,  "col": 3,  "speed": 85, "patrol": [(3,3),(3,10),(6,10),(6,3)]},
    {"row": 3,  "col": 20, "speed": 90, "patrol": [(3,20),(3,14),(6,14),(6,20)]},
    {"row": 20, "col": 3,  "speed": 80, "patrol": [(20,3),(20,10),(17,10),(17,3)]},
    {"row": 20, "col": 20, "speed": 95, "patrol": [(20,20),(17,20),(17,14),(20,14)]},
]

FX_FOLDER = "assets/image/Sprite"
FX_PREFIX = "FX001_"

COLOR_HP_BG     = (60,  0,  0)
COLOR_HP_FILL   = (0, 210, 60)
COLOR_HP_ENEMY  = (210, 40, 40)
COLOR_HP_BORDER = (200, 200, 200)


class GameScene(Scene):
    def __init__(self, scene_manager):
        super().__init__("Game", scene_manager)

        self.world  = Map(MAP_SIZE, MAP_SIZE)
        self.player: Optional[Player] = Player(self.world)
        self.enemies: List[Enemy] = []

        self.camera = Camera(0, 0)
        self.camera.attach(self.player)

        self.fx_pool    = FXPool()
        self._fx_frames = self.fx_pool.load_frames(FX_FOLDER, FX_PREFIX)

        self._hud_font  = pygame.font.SysFont("Arial", 18, bold=True)
        self._hint_font = pygame.font.SysFont("Arial", 14)

        self._setup_world()
        self._connect_attack_fx()

    # ── Инициализация ─────────────────────────────────────────────────────

    def _setup_world(self):
        rows = self.world.rows
        cols = self.world.cols

        for r in range(rows):
            for c in range(cols):
                if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                    self.world.add_static_object(Tree(), r, c)
                    self.world.walk_grid[r][c] = 0

        self.world.add_static_object(House(), HOUSE_ROW, HOUSE_COL)

        for r in range(FENCE_R_MIN, FENCE_R_MAX + 1):
            for c in range(FENCE_C_MIN, FENCE_C_MAX + 1):
                on_perimeter = (r == FENCE_R_MIN or r == FENCE_R_MAX or
                                c == FENCE_C_MIN or c == FENCE_C_MAX)
                if not on_perimeter:
                    continue
                if (r, c) == FENCE_ENTRANCE:
                    continue
                if (r, c) == (HOUSE_ROW, HOUSE_COL):
                    continue
                self.world.add_static_object(Tree(), r, c)

        self.world.add_dinamic_object(self.player, *PLAYER_START)

        for cfg in ENEMY_CONFIGS:
            enemy = Enemy(self.world, speed=cfg["speed"])
            enemy.set_target(self.player)
            enemy.add_patrol("main", cfg["patrol"])
            self.world.add_dinamic_object(enemy, cfg["row"], cfg["col"])
            self.enemies.append(enemy)

    def _connect_attack_fx(self):
        """Подключает FXPool и списки целей ко всем AttackComponent."""
        p_atk = self.player.get_component("attack")
        if p_atk:
            p_atk.set_fx(self.fx_pool, self._fx_frames)
            p_atk.set_targets(self.enemies)

        for enemy in self.enemies:
            e_atk = enemy.get_component("attack")
            if e_atk:
                e_atk.set_fx(self.fx_pool, self._fx_frames)
                e_atk.set_targets([self.player])

    # ── Scene interface ────────────────────────────────────────────────────

    def on_enter(self) -> None:
        pass

    def handle_events(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.ref_scene_manager.change_scene("Main menu")

        if self.player:
            self.player.handle_event(event)

    def update(self, delta_time: float):
        if self.world:
            self.world.update(delta_time)
        if self.camera:
            self.camera.update(delta_time)
        self.fx_pool.update(delta_time)
        self._remove_dead_enemies()

    def _remove_dead_enemies(self):
        dead = [e for e in self.enemies
                if not e.get_component("stats").is_alive()]
        for enemy in dead:
            enemy.enabled = False
            self.world.all_dynamic_objects.discard(enemy)
            self.enemies.remove(enemy)
            # Обновляем список целей у игрока
            p_atk = self.player.get_component("attack")
            if p_atk:
                p_atk.set_targets(self.enemies)

    # ── Render ────────────────────────────────────────────────────────────

    def render(self, surface: pygame.Surface) -> None:
        if self.world:
            self.world.render(surface, self.camera.offset)

        self.fx_pool.render(surface, self.camera.offset)
        self._render_all_health_bars(surface)
        self._render_player_hud(surface)

    def _render_all_health_bars(self, surface: pygame.Surface) -> None:
        """Полоски HP над всеми персонажами прямо над спрайтом."""
        for enemy in self.enemies:
            self._draw_world_bar(surface, enemy,
                                 bar_color=COLOR_HP_ENEMY, y_offset=-220)
        # Маленькая полоска над самим игроком
        self._draw_world_bar(surface, self.player,
                             bar_color=COLOR_HP_FILL, y_offset=-235, width=50)

    def _draw_world_bar(self, surface: pygame.Surface, obj: GameObject,
                        bar_color, y_offset: int = -220, width: int = 60):
        stats     = obj.get_component("stats")
        transform = obj.get_component("transform")
        if not stats or not transform:
            return
        ratio = max(0.0, stats.current_health / stats.max_health)
        pos   = transform.get_screen_position() - self.camera.offset
        bar_h = 7
        bx    = int(pos.x) - width // 2
        by    = int(pos.y) + y_offset
        pygame.draw.rect(surface, COLOR_HP_BG,    (bx, by, width, bar_h))
        pygame.draw.rect(surface, bar_color,       (bx, by, int(width * ratio), bar_h))
        pygame.draw.rect(surface, COLOR_HP_BORDER, (bx, by, width, bar_h), 1)

    def _render_player_hud(self, surface: pygame.Surface) -> None:
        """Большая полоска HP игрока в левом нижнем углу."""
        stats = self.player.get_component("stats")
        if not stats:
            return

        sw, sh  = surface.get_size()
        bar_w   = 220
        bar_h   = 22
        margin  = 20
        bx      = margin
        by      = sh - margin - bar_h

        # Полупрозрачный фон
        bg = pygame.Surface((bar_w + 80, bar_h + 16), pygame.SRCALPHA)
        bg.fill((20, 20, 20, 160))
        surface.blit(bg, (bx - 4, by - 20))

        # Подсказка
        hint = self._hint_font.render("F / ЛКМ — атака", True, (180, 180, 180))
        surface.blit(hint, (bx, by - 16))

        ratio = max(0.0, stats.current_health / stats.max_health)

        # Цвет: зелёный → жёлтый → красный
        if ratio > 0.5:
            r = int(255 * (1 - ratio) * 2)
            g = 210
        else:
            r = 210
            g = int(210 * ratio * 2)

        pygame.draw.rect(surface, (60, 0, 0),      (bx, by, bar_w, bar_h))
        pygame.draw.rect(surface, (r, g, 30),      (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, COLOR_HP_BORDER, (bx, by, bar_w, bar_h), 2)

        # Текст HP
        hp_text = self._hud_font.render(
            f"HP  {int(stats.current_health)} / {int(stats.max_health)}",
            True, (240, 240, 240))
        surface.blit(hp_text, (bx + bar_w + 8, by + 2))

    def on_exit(self):
        if self.world:
            del self.world
        self.enemies.clear()