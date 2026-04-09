from typing import Dict, Optional, List

import pygame

from scenes.scene import Scene
from scenes.scene_game import GameScene
from scenes.scene_intro import IntroScene
from scenes.scene_mainmenu import MainMenuScene


class SceneManager:
    """
        Менеджер сцен - управляет переключением между различными состояниями игры.
        Реализует паттерн "Конечный автомат" (State Machine) для управления сценами.
        """

    def __init__(self, game):
        self.ref_game = game
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.previous_scene: Optional[Scene] = None
        self.scene_stack: List[Scene] = []  # Стек для вложенных сцен (например, пауза поверх игры)

        # Регистрация системных сцен
        self._register_system_scenes()

    def _register_system_scenes(self):
        self.register_scene(MainMenuScene(self))
        self.register_scene(IntroScene(self))
        self.register_scene(GameScene(self))

    def register_scene(self, scene: Scene) -> None:
        """Регистрация сцены в менеджере"""
        self.scenes[scene.name] = scene
        print(f"Зарегистрирована сцена: {scene.name}")

    def change_scene(self, scene_name: str) -> None:
        """
         Полная замена текущей сцены на новую.
        """
        if scene_name not in self.scenes:
            raise ValueError(f"Сцена '{scene_name}' не зарегистрирована")
        new_scene = self.scenes[scene_name]
        if self.current_scene:
            self.current_scene.on_exit()
            self.previous_scene = self.current_scene
            self.current_scene = new_scene
            self.current_scene.on_enter()
        else:
            # Первая сцена
            self.current_scene = new_scene
            self.current_scene.on_enter()

    def push_scene(self, scene_name: str) -> None:
        """
        Добавление сцены поверх текущей (например, меню паузы).
        Текущая сцена приостанавливается.
        """
        if scene_name not in self.scenes:
            raise ValueError(f"Сцена '{scene_name}' не зарегистрирована")

        new_scene = self.scenes[scene_name]

        if self.current_scene:
            # Приостанавливаем текущую сцену и добавляем в стек
            self.scene_stack.append(self.current_scene)

        self.current_scene = new_scene
        self.current_scene.on_enter()

    def pop_scene(self) -> None:
        """
        Удаление текущей сцены и возврат к предыдущей из стека.
        """
        if not self.scene_stack:
            print("Нет сцен в стеке для возврата")
            return

        old_scene = self.current_scene
        self.current_scene = self.scene_stack.pop()

        if old_scene:
            old_scene.on_exit(self.current_scene)

    def get_scene(self, scene_name: str) -> Optional[Scene]:
        """Получение сцены по имени"""
        return self.scenes.get(scene_name)

    def has_scene(self, scene_name: str) -> bool:
        """Проверка существования сцены"""
        return scene_name in self.scenes

    def handle_events(self, events) -> None:
        if self.current_scene:
            self.current_scene.handle_events(events)

    def update(self, delta_time: float) -> None:
        """Обновление текущей сцены"""
        if self.current_scene:
            self.current_scene.update(delta_time)

    def render(self, surface: pygame.Surface) -> None:
        """Отрисовка текущей сцены"""
        if self.current_scene:
            self.current_scene.render(surface)

    def cleanup(self) -> None:
        """Очистка всех сцен"""
        for scene in self.scenes:
            scene.on_exit()

        self.scenes.clear()
        self.current_scene = None
        self.previous_scene = None
        self.scene_stack.clear()