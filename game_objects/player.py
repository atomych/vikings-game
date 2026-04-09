from __future__ import annotations

from typing import Optional

import pygame

from game_objects.component_character_stats import CharacterStatsComponent
from game_objects.component_controller import PlayerControllerComponent, AIControllerComponent
from game_objects.component_image import ImageComponent
from game_objects.component_transform import TransformComponent
from game_objects.component_animation import CharacterAnimationComponent
from game_objects.component_collider import ColliderComponent
from game_objects.component_attack import AttackComponent
from game_objects.gobject import GameObject


class Player(GameObject):
    def __init__(self, map_ref):
        super().__init__("Player")
        self.add_component(TransformComponent())
        self.add_component(CharacterStatsComponent(
            name="Викинг", max_health=100, base_move_speed=150))
        self.add_component(ColliderComponent(size=(50, 50), stride=20))
        self.add_component(PlayerControllerComponent(map_ref))
        self.add_component(AttackComponent(
            damage=30, range_px=130, cooldown=0.7, attack_duration=0.35))
        self.add_component(
            CharacterAnimationComponent(
                "assets/image/GameObjects/Character/Forester", (-75, -180)))

    def render(self, surface: pygame.Surface,
               camera_offset: Optional[pygame.math.Vector2] = None) -> None:
        super().render(surface, camera_offset)

    def update(self, delta_time: float) -> None:
        super().update(delta_time)


class Enemy(GameObject):
    def __init__(self, map_ref,
                 detection_radius: float = 500,
                 attack_radius: float = 110,
                 speed: float = 90.0):
        super().__init__("Enemy")
        self.add_component(TransformComponent())
        self.add_component(CharacterStatsComponent(
            name="Враг", max_health=60, base_move_speed=speed))
        self.add_component(ColliderComponent(size=(50, 50), stride=20))
        self.add_component(AIControllerComponent(
            map_ref,
            detection_radius=detection_radius,
            attack_radius=attack_radius))
        self.add_component(AttackComponent(
            damage=15, range_px=attack_radius, cooldown=1.2, attack_duration=0.4))
        self.add_component(
            CharacterAnimationComponent(
                "assets/image/GameObjects/Character/Enemy", (-75, -180)))

    def set_target(self, target: GameObject) -> None:
        ctrl = self.get_component("controller")
        if ctrl:
            ctrl.set_target(target)

    def add_patrol(self, way_name: str, waypoints: list) -> None:
        ctrl = self.get_component("controller")
        if ctrl:
            ctrl.add_waypoints(way_name, waypoints)
            ctrl.set_way(way_name)


class House(GameObject):
    def __init__(self):
        super().__init__("House")
        self.add_component(TransformComponent(8, 8))
        self.add_component(ImageComponent("assets/image/GameObjects/Home.png", (0, -500)))


class Tree(GameObject):
    def __init__(self, row=0, col=0):
        super().__init__("Tree")
        self.add_component(TransformComponent(row, col))
        self.add_component(ImageComponent(
            "assets/image/GameObjects/Tree/Tree.png", (-140, -280)))
        self.add_component(ColliderComponent(size=(50, 50)))
