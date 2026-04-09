from __future__ import annotations

from typing import Optional, Dict, List, Tuple

import pygame
import os

from game_objects.component import Component
from game_objects.component_transform import Direction, TransformComponent
from game_objects.component_controller import ControllerComponent
from game_objects.frame_sequence import FrameSequence
from game_objects.movement_state import MovementState


class CharacterAnimationComponent(Component):
    """
    Проигрывает покадровую анимацию персонажа.
    Спрайты именуются: {char}_{state}_{direction}_{frame}.png
    Пример: Forester_walk_S_0.png
    """

    def __init__(self, path: str, offset: tuple = (0, 0)):
        super().__init__("animation")

        # sprite_list[state][direction] = [(Surface, frame_no), ...]
        self.sprite_list: Dict[MovementState, Dict[Direction, List[Tuple[pygame.Surface, int]]]] = {}
        # animations[state] = FrameSequence
        self.animations: Dict[MovementState, FrameSequence] = {}
        self.surface: Optional[pygame.Surface] = None
        self.offset = pygame.math.Vector2(offset)

        self._init_animations(path)

        # Заполняются в on_attach
        self.controller: Optional[ControllerComponent] = None
        self.transform:  Optional[TransformComponent]  = None

    # ── инициализация ──────────────────────────────────────────────────────

    def on_attach(self, game_object) -> None:
        super().on_attach(game_object)
        self.controller = game_object.get_component("controller")
        self.transform  = game_object.get_component("transform")

    def _init_animations(self, path: str) -> None:
        if not os.path.isdir(path):
            print(f"[Animation] Папка не найдена: {path}")
            return

        for filename in sorted(os.listdir(path)):
            if not filename.endswith(".png"):
                continue
            try:
                char_name, state_str, dir_str, frame_no = self._parse_filename(filename)
            except ValueError as e:
                print(f"[Animation] Пропускаем {filename}: {e}")
                continue

            try:
                state     = MovementState(state_str)
                direction = Direction(dir_str)
            except ValueError:
                # Неизвестное состояние или направление — пропускаем
                continue

            try:
                image = pygame.image.load(f"{path}/{filename}").convert_alpha()
            except pygame.error as e:
                print(f"[Animation] Ошибка загрузки {filename}: {e}")
                continue

            self.sprite_list.setdefault(state, {}).setdefault(direction, [])
            self.sprite_list[state][direction].append((image, frame_no))

        # Сортируем кадры по номеру
        for state_dict in self.sprite_list.values():
            for direction in state_dict:
                state_dict[direction].sort(key=lambda x: x[1])

        # Создаём FrameSequence для каждого состояния
        for state, dirs in self.sprite_list.items():
            first_dir   = next(iter(dirs))
            frame_count = len(dirs[first_dir])
            # ATTACK — однократная; остальные — зацикленные
            loop     = (state != MovementState.ATTACK)
            duration = 0.07 if state == MovementState.ATTACK else 0.1333
            seq = FrameSequence(state.name, frame_count, duration, loop=loop)
            seq.run()
            self.animations[state] = seq

    @staticmethod
    def _parse_filename(filename: str) -> Tuple[str, str, str, int]:
        base  = filename.rsplit(".", 1)[0]
        parts = base.split("_")
        # Поддерживаем два формата:
        #   4 части: char_state_dir_frame  (Forester_walk_S_0.png)
        #   3 части: state_dir_frame       (walk_E_001.png)
        if len(parts) == 4:
            return parts[0], parts[1], parts[2], int(parts[3])
        elif len(parts) == 3:
            return "", parts[0], parts[1], int(parts[2])
        else:
            raise ValueError(
                f"Ожидается формат state_dir_frame или char_state_dir_frame, получено: {filename}"
            )

    # ── update / render ────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        if not self.controller or not self.transform:
            return

        state     = self.controller.movement_state
        direction = self.transform.direction

        if state not in self.sprite_list:
            # Для неизвестного состояния показываем IDLE или оставляем последний кадр
            state = MovementState.IDLE
            if state not in self.sprite_list:
                return

        dirs = self.sprite_list[state]

        # Если нет кадра для этого направления — берём S как запасной
        if direction not in dirs:
            direction = Direction.S
        if direction not in dirs:
            return

        seq = self.animations[state]

        # ATTACK-анимация: перезапускаем при начале атаки
        if state == MovementState.ATTACK and not seq.is_playing:
            seq.run()

        seq.update(dt)
        frame = seq.get_frame()
        frames = dirs[direction]
        if frame < len(frames):
            self.surface = frames[frame][0]

    def render(self, surface: pygame.Surface,
               offset: Optional[pygame.math.Vector2] = None) -> None:
        if not self.surface or not self.transform:
            return
        off = offset if offset is not None else pygame.math.Vector2(0, 0)

        pos = self.transform.get_screen_position() + self.offset - off

        # Мигание при получении урона
        stats = self.game_object.get_component("stats") if self.game_object else None
        if stats and stats.is_flashing:
            # Рисуем красноватый overlay
            tinted = self.surface.copy()
            tinted.fill((255, 80, 80, 100), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(tinted, pos)
        else:
            surface.blit(self.surface, pos)