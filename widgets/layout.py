from typing import List, Optional
import pygame

from widgets.widget import Widget

class Layout(Widget):
    def __init__(self):
        super().__init__()
        self.children: List[Widget] = []
        self.spacing = 30  # Расстояние между элементами


    def add_child(self, child):
        child.parent = self
        self.children.append(child)
        self._update_layout()

    def remove_child(self, child: Widget) -> None:
        """Удаление дочернего виджета"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            self._update_layout()



    def _update_layout(self) -> None:
        """Обновление компоновки - должен быть реализован в дочерних классах"""
        pass


    def render(self, surface: pygame.Surface) -> None:
        """Отрисовка layout'а и всех дочерних виджетов"""
        self.update_background()

        if self.surface:
            surface.blit(self.surface, self.rect)

        for child in self.children:
            child.render(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        for child in self.children:
            child.handle_event(event)

    def update(self, delta_time: float) -> None:
        for child in self.children:
            child.update(delta_time)


class VerticalLayout(Layout):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos


    def _update_layout(self):
        size = (0, 0)
        for child in self.children:
            child_size = child.rect.size
            size = max(size, child_size)

        y_offset = 0
        for child in self.children:
            child.rect.x = 0
            child.rect.y = 0 + y_offset
            y_offset += child.rect.height + self.spacing

        size = (size[0], y_offset)
        self.rect = pygame.Rect(self.pos, size)
        self.surface = pygame.Surface(size, pygame.SRCALPHA)



class HorizontalLayout(Layout):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos

    def _update_layout(self):
        size = (0, 0)
        for child in self.children:
            child_size = child.rect.size
            size = max(size, child_size)

        x_offset = 0
        for child in self.children:
            child.rect.x = 0 + x_offset
            child.rect.y = 0
            x_offset += child.rect.width + self.spacing

        size = (x_offset, size[0])
        self.rect = pygame.Rect(self.pos, size)
        self.surface = pygame.Surface(size, pygame.SRCALPHA)


class ScreenLayout(Layout):
    def __init__(self, game):
        self.game_ref = game
        self.rect = game.screen.get_rect()


