"""
FX-эффекты: одиночные анимации (удар, взрыв, вспышка).
Используются как lightweight-объекты без GameObject/Component.
"""
from __future__ import annotations

import os
from typing import List, Optional

import pygame


class FXEffect:
    """Одиночная одноразовая анимация в мировых (экранных) координатах."""

    def __init__(self,
                 frames: List[pygame.Surface],
                 screen_pos: pygame.math.Vector2,
                 frame_duration: float = 0.07,
                 scale: float = 1.0):
        self.frames         = frames
        self.pos            = pygame.math.Vector2(screen_pos)
        self.frame_duration = frame_duration
        self.current_frame  = 0
        self.elapsed        = 0.0
        self.done           = False

        if scale != 1.0:
            self.frames = [
                pygame.transform.scale(
                    s,
                    (int(s.get_width() * scale), int(s.get_height() * scale))
                )
                for s in frames
            ]

    def update(self, dt: float) -> None:
        if self.done:
            return
        self.elapsed += dt
        if self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.done = True

    def render(self, surface: pygame.Surface,
               camera_offset: pygame.math.Vector2) -> None:
        if self.done or self.current_frame >= len(self.frames):
            return
        surf = self.frames[self.current_frame]
        draw_pos = self.pos - camera_offset - pygame.math.Vector2(
            surf.get_width() // 2, surf.get_height() // 2
        )
        surface.blit(surf, draw_pos)


class FXPool:
    """
    Менеджер активных FX-эффектов.
    Сцена создаёт один экземпляр и передаёт ссылку AttackComponent-ам.
    """

    def __init__(self):
        self._effects: List[FXEffect] = []
        # Кэш загруженных наборов кадров: path → list[Surface]
        self._frame_cache: dict[str, List[pygame.Surface]] = {}

    # ── публичный API ──────────────────────────────────────────────────────

    def load_frames(self, folder: str, prefix: str = "") -> List[pygame.Surface]:
        """
        Загружает и кэширует кадры из папки.
        Фильтрует по префиксу (опционально).
        """
        key = f"{folder}|{prefix}"
        if key in self._frame_cache:
            return self._frame_cache[key]

        frames: List[pygame.Surface] = []
        if not os.path.isdir(folder):
            print(f"[FXPool] Папка не найдена: {folder}")
            return frames

        names = sorted(
            f for f in os.listdir(folder)
            if f.endswith(".png") and f.startswith(prefix)
        )
        for name in names:
            try:
                surf = pygame.image.load(os.path.join(folder, name)).convert_alpha()
                frames.append(surf)
            except pygame.error as e:
                print(f"[FXPool] Ошибка загрузки {name}: {e}")

        self._frame_cache[key] = frames
        return frames

    def spawn(self,
              frames: List[pygame.Surface],
              screen_pos: pygame.math.Vector2,
              frame_duration: float = 0.07,
              scale: float = 1.0) -> None:
        """Создаёт новый одиночный эффект."""
        if not frames:
            return
        self._effects.append(FXEffect(frames, screen_pos, frame_duration, scale))

    def update(self, dt: float) -> None:
        for fx in self._effects:
            fx.update(dt)
        # Удаляем завершённые
        self._effects = [fx for fx in self._effects if not fx.done]

    def render(self, surface: pygame.Surface,
               camera_offset: pygame.math.Vector2) -> None:
        for fx in self._effects:
            fx.render(surface, camera_offset)