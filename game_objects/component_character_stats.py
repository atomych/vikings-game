import pygame.math
from game_objects.component import Component


class CharacterStatsComponent(Component):
    """
    Компонент характеристик персонажа (игрок, NPC, враг).
    Содержит все параметры: здоровье, стамина, скорость.
    """
    def __init__(self,
                 max_health: float = 100,
                 max_stamina: float = 100,
                 base_move_speed: float = 150.0,
                 name: str = "NoName",
                 info: str = "..."):
        super().__init__("stats")
        self.max_health          = max_health
        self.max_stamina         = max_stamina
        self.base_move_speed     = base_move_speed
        self.base_running_speed  = self.base_move_speed * 2
        self.character_name      = name
        self.info                = info

        self.current_health  = self.max_health
        self.current_stamina = self.max_stamina

        # Мигание при получении урона
        self._hit_flash_timer   = 0.0
        self.HIT_FLASH_DURATION = 0.15   # секунды
        self.is_flashing        = False

    # ── здоровье ──────────────────────────────────────────────────────────────

    def is_alive(self) -> bool:
        return self.current_health > 0

    def take_damage(self, val: float) -> bool:
        """Наносит урон. Возвращает True если персонаж выжил."""
        self.current_health = max(0.0, self.current_health - val)
        self.is_flashing        = True
        self._hit_flash_timer   = 0.0
        if self.current_health <= 0:
            print(f"Персонаж '{self.character_name}' погиб")
            return False
        print(f"Персонаж '{self.character_name}' получил урон {val:.0f} "
              f"(осталось {self.current_health:.0f})")
        return True

    def heal(self, val: float) -> None:
        self.current_health = min(self.max_health, self.current_health + val)

    # ── стамина ───────────────────────────────────────────────────────────────

    def use_stamina(self, val: float) -> bool:
        if self.current_stamina >= val:
            self.current_stamina -= val
            return True
        return False

    def restore_stamina(self, dt: float) -> None:
        rate = self.max_stamina / 5   # восстанавливается за 5 секунд
        self.current_stamina = min(self.max_stamina,
                                   self.current_stamina + rate * dt)

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        if not self.enabled:
            return
        if self.current_stamina < self.max_stamina:
            self.restore_stamina(dt)
        if self.is_flashing:
            self._hit_flash_timer += dt
            if self._hit_flash_timer >= self.HIT_FLASH_DURATION:
                self.is_flashing = False