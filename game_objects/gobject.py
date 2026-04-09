import uuid
from typing import Dict, Optional, List
import pygame
from game_objects.component import Component


class GameObject:
    def __init__(self, name: str):
        self.id = uuid.uuid4()  # Уникальный идентификатор
        self.name = name
        self.enabled = True
        self.is_show_origins = True

        self.tags: List[str] = []
        # Иерархия объектов
        self.parent: Optional['GameObject'] = None
        self.children: List['GameObject'] = []

        # Компоненты
        self.components: Dict[str, Component] = {}

    def add_component(self, component: Component) -> Optional['Component']:
        self.components[component.name] = component
        component.on_attach(self)
        return component

    def get_component(self, component_name) -> Optional['Component']:
        if self.has_component(component_name):
            return self.components[component_name]
        else:
            return None

    def has_component(self, component_name):
        if component_name in self.components:
            return True
        else:
            return False

    def remove_component(self, component_name) -> bool:
        component = self.get_component(component_name)
        if component:
            component.on_detach()
            del self.components[component.name]
            return True
        return False

    def add_child(self, child: 'GameObject') -> bool:
        if child.parent:
            child.parent.remove_child(child)
            child.parent = self
            self.children.append(child)
            return True
        return False

    def get_child(self, name) -> Optional['GameObject']:
        for child in self.children:
            if child.name == name:
                return child
        return None

    def remove_child(self, child: 'GameObject') -> bool:
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            return True
        return False

    def update(self, delta_time: float) -> None:
        if not self.enabled:
            return
        for component in self.components.values():
            component.update(delta_time)

        for child in self.children:
            child.update(delta_time)

    def render(self, surface: pygame.Surface, camera_offset: Optional[pygame.math.Vector2] = None) -> None:
        if not self.enabled:
            return
        for component in self.components.values():
            component.render(surface, camera_offset)

        for child in self.children:
            child.render(surface, camera_offset)

        if self.is_show_origins:
            trans_comp = self.get_component("transform")
            if trans_comp:
                pygame.draw.circle(surface, (255, 0, 255, 255), trans_comp.screen_position - camera_offset, 2)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False

        for component in self.components.values():
            component.handle_event(event)

        for child in self.children:
            child.handle_event(event)

        return True
