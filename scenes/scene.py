from abc import ABC, abstractmethod
from typing import List, Optional, Dict

class Scene(ABC):
    def __init__(self, scene_name: str, ref_scene_manager: Optional['SceneManager']):
        self.name = scene_name
        self.ref_scene_manager = ref_scene_manager

    @abstractmethod
    def on_enter(self): pass  # Подготовка декораций, актеров, реквизита

    @abstractmethod
    def on_exit(self): pass  # Очистка сцены

    @abstractmethod
    def update(self, dt): pass  # Обновление логики сцены. Развитие сюжета пьесы

    @abstractmethod
    def render(self, surface): pass  # Визуальное представление пьесы зрителям

    @abstractmethod
    def handle_events(self, event): pass  # Обработка событий, специфичных для этой сцены.
    # Реакция актеров на действия зрителей





