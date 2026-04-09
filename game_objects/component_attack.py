"""
AttackComponent — компонент атаки.
Отвечает за: кулдаун, хитбокс, нанесение урона, спавн FX-эффекта.
"""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

import pygame

from game_objects.component import Component
from game_objects.movement_state import MovementState

if TYPE_CHECKING:
    from game_objects.gobject import GameObject
    from game_objects.component_transform import TransformComponent
    from game_objects.component_character_stats import CharacterStatsComponent
    from game_objects.component_controller import ControllerComponent
    from fx_effect import FXPool


class AttackComponent(Component):
    """
    Параметры:
        damage      — урон за удар
        range_px    — радиус поражения (пиксели)
        cooldown    — минимальное время между ударами (сек)
        attack_duration — как долго стоит состояние ATTACK (сек)
    """

    def __init__(self,
                 damage: float = 25.0,
                 range_px: float = 130.0,
                 cooldown: float = 0.8,
                 attack_duration: float = 0.35):
        super().__init__("attack")

        self.damage           = damage
        self.range_px         = range_px
        self.cooldown         = cooldown
        self.attack_duration  = attack_duration

        self._cooldown_timer  = cooldown        # начинаем готовым к атаке
        self._anim_timer      = 0.0
        self.is_attacking     = False

        # Заполняется снаружи
        self._targets: List['GameObject'] = []
        self._fx_pool: Optional['FXPool'] = None
        self._fx_frames: list = []

        # Ссылки на братские компоненты (заполняются в on_attach)
        self._transform:   Optional['TransformComponent']      = None
        self._stats:       Optional['CharacterStatsComponent'] = None
        self._controller:  Optional['ControllerComponent']     = None

    # ── инициализация ──────────────────────────────────────────────────────

    def on_attach(self, game_object: 'GameObject') -> None:
        super().on_attach(game_object)
        self._transform  = game_object.get_component("transform")
        self._stats      = game_object.get_component("stats")
        self._controller = game_object.get_component("controller")

    def set_targets(self, targets: List['GameObject']) -> None:
        """Передаём список объектов, которые можно атаковать."""
        self._targets = targets

    def set_fx(self, fx_pool: 'FXPool', fx_frames: list) -> None:
        """Подключаем FX-систему сцены."""
        self._fx_pool   = fx_pool
        self._fx_frames = fx_frames

    # ── публичный API ──────────────────────────────────────────────────────

    def can_attack(self) -> bool:
        return (not self.is_attacking and
                self._cooldown_timer >= self.cooldown)

    def try_attack(self) -> bool:
        """
        Пытается нанести удар. Возвращает True если атака началась.
        """
        if not self.can_attack():
            return False
        if not self._transform or not self._stats:
            return False
        if not self._stats.is_alive():
            return False

        # Старт атаки
        self.is_attacking    = True
        self._cooldown_timer = 0.0
        self._anim_timer     = 0.0

        # Переводим контроллер в ATTACK — останавливаем движение
        if self._controller:
            self._controller.stop()
            self._controller.set_state(MovementState.ATTACK)

        # Спавн FX
        self._spawn_fx()

        # Хитбокс
        self._deal_damage()

        return True

    # ── внутренние методы ──────────────────────────────────────────────────

    def _spawn_fx(self) -> None:
        if self._fx_pool is None or not self._fx_frames:
            return
        origin    = self._transform.get_screen_position()
        dir_vec   = self._transform.direction.to_vector()
        fx_pos    = origin + dir_vec * 90
        self._fx_pool.spawn(self._fx_frames, fx_pos, frame_duration=0.06, scale=1.2)

    def _deal_damage(self) -> None:
        my_pos = self._transform.get_screen_position()
        for target in self._targets:
            if not target.enabled:
                continue
            t_transform = target.get_component("transform")
            t_stats     = target.get_component("stats")
            if not t_transform or not t_stats:
                continue
            if not t_stats.is_alive():
                continue
            dist = (t_transform.get_screen_position() - my_pos).length()
            if dist <= self.range_px:
                t_stats.take_damage(self.damage)

    # ── update ─────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        # Кулдаун
        if self._cooldown_timer < self.cooldown:
            self._cooldown_timer += dt

        # Сбрасываем состояние ATTACK когда анимация закончилась
        if self.is_attacking:
            self._anim_timer += dt
            if self._anim_timer >= self.attack_duration:
                self.is_attacking = False
                if self._controller:
                    self._controller.set_state(MovementState.IDLE)