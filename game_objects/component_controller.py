from __future__ import annotations

from typing import Optional, Dict, List

import pygame

import utils
from game_objects.component import Component
from game_objects.component_character_stats import CharacterStatsComponent
from game_objects.component_transform import TransformComponent, Direction
from game_objects.component_collider import ColliderComponent, CollisionBehavior
from game_objects.ground import Map
from pygame.math import Vector2

from game_objects.movement_state import MovementState
from managers.event_manager import event_manager, EventType


class ControllerComponent(Component):

    def __init__(self, map_ref: Map):
        super().__init__("controller")
        self.transform:  Optional[TransformComponent]      = None
        self.stats:      Optional[CharacterStatsComponent] = None
        self.collider:   Optional[ColliderComponent]       = None

        self.movement_state = MovementState.IDLE
        self.move_vector    = Vector2(0, 0)
        self.map_ref: Map   = map_ref
        self.control_point: Optional[tuple] = None

        for key in EventType:
            event_manager.register_event_type(key)

    def on_attach(self, game_object) -> None:
        self.transform = game_object.get_component("transform")
        self.stats     = game_object.get_component("stats")
        self.collider  = game_object.get_component("collider")

    def set_state(self, new_state: MovementState) -> None:
        old_state = self.movement_state
        self.movement_state = new_state
        event_manager.emit(EventType.MOVEMENT_STATE_CHANGED,
                           self, new_state, old_state, reuse_cache=True)

    def move(self) -> None:
        self.move_vector = self.transform.direction.to_vector() * self.stats.base_move_speed
        self.set_state(MovementState.WALK)

    def stop(self) -> None:
        self.move_vector = Vector2(0, 0)
        self.set_state(MovementState.IDLE)

    def run(self) -> None:
        self.move_vector = self.transform.direction.to_vector() * self.stats.base_running_speed
        self.set_state(MovementState.RUN)

    def set_direction(self, direction: Direction) -> None:
        self.transform.set_direction(direction)

    def _apply_movement(self, delta_time: float) -> bool:
        if self.movement_state not in (MovementState.WALK, MovementState.RUN):
            return False
        if not self.stats or not self.stats.is_alive():
            return False

        ahead = self.transform.screen_position + self.transform.direction.to_vector() * 100
        self.control_point = ahead
        r, c = utils.iso_to_cart(ahead.x, ahead.y)
        if not self.map_ref.is_walkable(r, c):
            return False

        if self.collider:
            for obj in self.map_ref.all_static_objects:
                other = obj.get_component("collider")
                if other and self.collider.check_collision(other):
                    if other.behavior == CollisionBehavior.BLOCK:
                        return False

        self.transform.move_screen(
            self.move_vector.x * delta_time,
            self.move_vector.y * delta_time / 2
        )
        return True

    def update(self, delta_time: float) -> None:
        if not self.enabled or not self.transform or not self.stats:
            return
        if self.movement_state == MovementState.ATTACK:
            return
        self._apply_movement(delta_time)

    def render(self, surface: pygame.Surface,
               offset: Optional[pygame.math.Vector2] = None) -> None:
        pass


# ─────────────────────────────────────────────────────────────────────────────
class PlayerControllerComponent(ControllerComponent):
    def __init__(self, map_ref):
        super().__init__(map_ref)
        self.move_keys = {
            pygame.K_w: Direction.N,
            pygame.K_s: Direction.S,
            pygame.K_a: Direction.W,
            pygame.K_d: Direction.E,
        }
        self.active_keys  = set()
        self._game_object = None
        self._attack_comp = None

    def on_attach(self, game_object) -> None:
        super().on_attach(game_object)
        self._game_object = game_object

    def _get_attack(self):
        if self._attack_comp is None and self._game_object:
            self._attack_comp = self._game_object.get_component("attack")
        return self._attack_comp

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in self.move_keys:
                self.active_keys.add(event.key)
                self._update_movement()
                return True
            elif event.key == pygame.K_f:
                atk = self._get_attack()
                if atk:
                    atk.try_attack()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                atk = self._get_attack()
                if atk:
                    atk.try_attack()
                return True

        elif event.type == pygame.KEYUP:
            if event.key in self.move_keys and event.key in self.active_keys:
                self.active_keys.discard(event.key)
                self._update_movement()

        return False

    def _update_movement(self) -> None:
        if self.movement_state == MovementState.ATTACK:
            return
        self.move_vector = Vector2(0, 0)
        for key in self.active_keys:
            if key in self.move_keys:
                self.move_vector += self.move_keys[key].to_vector()

        if self.move_vector.length() > 0:
            self.set_direction(Direction.from_vector(self.move_vector))
            self.move_vector = self.move_vector.normalize() * self.stats.base_move_speed
            self.set_state(MovementState.WALK)
        else:
            self.stop()


# ─────────────────────────────────────────────────────────────────────────────
class AIControllerComponent(ControllerComponent):
    WAYPOINT_REACH_PX = 60

    def __init__(self, map_ref: Map,
                 detection_radius: float = 500,
                 attack_radius: float = 110,
                 dialog_radius: float = 150):
        super().__init__(map_ref)
        self.detection_radius = detection_radius
        self.attack_radius    = attack_radius
        self.dialog_radius    = dialog_radius
        self.target           = None
        self.waypoints: Dict[str, List[tuple]] = {}
        self.current_way: str = ""
        self.way_index: int   = 0
        self._game_object_ref = None
        self._attack_comp     = None

    def on_attach(self, game_object) -> None:
        super().on_attach(game_object)
        self._game_object_ref = game_object

    def _get_attack(self):
        if self._attack_comp is None and self._game_object_ref:
            self._attack_comp = self._game_object_ref.get_component("attack")
        return self._attack_comp

    def set_target(self, target) -> None:
        self.target = target

    def add_waypoints(self, way_name: str, waypoints: List[tuple]) -> None:
        self.waypoints[way_name] = waypoints

    def set_way(self, way_name: str) -> None:
        if way_name in self.waypoints:
            self.current_way = way_name
            self.way_index   = 0

    def _target_pos(self) -> Optional[Vector2]:
        if not self.target:
            return None
        t = self.target.get_component("transform")
        return t.get_screen_position() if t else None

    def _dist_to_target(self) -> float:
        pos = self._target_pos()
        if pos is None or not self.transform:
            return float("inf")
        return (pos - self.transform.screen_position).length()

    def _face_and_walk(self, target_screen: Vector2) -> None:
        diff = target_screen - self.transform.screen_position
        if diff.length() < 2:
            return
        norm = diff.normalize()
        self.set_direction(Direction.from_vector(norm))
        self.move_vector = norm * self.stats.base_move_speed
        self.set_state(MovementState.WALK)

    def _patrol_step(self) -> None:
        if not self.current_way or self.current_way not in self.waypoints:
            self.stop()
            return
        wps = self.waypoints[self.current_way]
        if not wps:
            self.stop()
            return
        wp_row, wp_col = wps[self.way_index]
        wp_screen = Vector2(utils.cart_to_iso(wp_row, wp_col))
        if (wp_screen - self.transform.screen_position).length() < self.WAYPOINT_REACH_PX:
            self.way_index = (self.way_index + 1) % len(wps)
        else:
            self._face_and_walk(wp_screen)

    def update(self, delta_time: float) -> None:
        if not self.enabled or not self.transform or not self.stats:
            return
        if not self.stats.is_alive():
            return
        if self.movement_state == MovementState.ATTACK:
            return

        dist = self._dist_to_target()
        atk  = self._get_attack()

        if dist <= self.attack_radius:
            self.stop()
            tpos = self._target_pos()
            if tpos:
                diff = tpos - self.transform.screen_position
                if diff.length() > 0:
                    self.set_direction(Direction.from_vector(diff.normalize()))
            if atk:
                atk.try_attack()

        elif dist <= self.detection_radius:
            tpos = self._target_pos()
            if tpos:
                self._face_and_walk(tpos)
            self._apply_movement(delta_time)

        else:
            self._patrol_step()
            self._apply_movement(delta_time)