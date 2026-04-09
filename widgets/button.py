import os.path
from typing import Callable, Tuple

import pygame
import pygame.event
from widgets.widget import Widget


class PushButton(Widget):
    def __init__(self,
                 pos: tuple[int, int],
                 size: tuple[int, int],
                 text: str,
                 callback_function: Callable[[None], None] = None,
                 font_name: str = 'Times new roman',
                 font_size: int = 16,
                 font_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
                 ui_btn_name: str = "btn02",
                 bgr_color: Tuple[int, int, int, int] = (255, 200, 100, 255)
                 ):
        super().__init__("PushButton")
        self.text: str = text
        self.on_click = callback_function
        self.background_color = bgr_color
        self.rect = pygame.Rect(pos, size)

        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color

        self.is_image = False
        self.is_convert_image_to_orig_size = False

        self.is_pressed = False
        self.is_hovered = False
        self.is_updated = False

        self._init_data(ui_btn_name)

    def _init_data(self, ui_btn_name):
        path_ui_btn_default = f"assets/image/ui/{ui_btn_name}_default.png"
        path_ui_btn_pressed = f"assets/image/ui/{ui_btn_name}_pressed.png"

        if os.path.exists(path_ui_btn_default):
            self.default_surface = pygame.image.load(path_ui_btn_default).convert_alpha()
            self.pressed_surface = pygame.image.load(path_ui_btn_pressed).convert_alpha()

            if self.is_convert_image_to_orig_size and self.default_surface and self.pressed_surface:
                self.default_surface = pygame.transform.scale(self.default_surface, self.rect)
                self.pressed_surface = pygame.transform.scale(self.default_surface, self.rect)

            self.rect.size = self.default_surface.get_rect().size
            self.is_image = True
        else:
            self.is_image = False

        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        if self.text:
            # Загружаем шрифт и создаем текстовую поверхность (изображение с текстом)
            self.font = pygame.font.SysFont(self.font_name, self.font_size)
            self.text_surface = self.font.render(self.text, True, self.font_color)  # (0,0,0) - Черный цвет

    def _update_surface(self, dt: float):
        if self.is_image:
            self.surface.fill((0, 0, 0, 0))

            if self.is_image:
                if self.is_pressed:
                    self.surface.blit(self.pressed_surface, (0, 0))
                else:
                    self.surface.blit(self.default_surface, (0, 0))

            if self.text:
                text_rect = self.text_surface.get_rect()
                surf_rect = self.surface.get_rect()
                text_rect.center = surf_rect.center

                self.surface.blit(self.text_surface, text_rect)

                self.background_color = None
        else:
            self.surface.fill((0, 0, 0, 0))
            if self.is_pressed:
                pygame.draw.rect(self.surface, (80, 170, 50, 255), self.surface.get_rect())
            else:
                pygame.draw.rect(self.surface, (40, 170, 10, 255), self.surface.get_rect())

            if self.text:
                surface_rect = self.surface.get_rect()
                text_rect = self.text_surface.get_rect()
                text_rect.center = surface_rect.center
                self.surface.blit(self.text_surface, text_rect)
        self.is_updated = True

    def up(self):  #Метод срабатывает когда мы отпускаем кнопку
        """Вызывается при отпускании ЛКМ над кнопкой"""
        print(f"Кнопка '{self.text}' отпущена — действие выполнено!")
        # Здесь обычно вызывают какое-то действие (callback)
        self.is_pressed = False
        self.is_updated = False
        if self.on_click:
            self.on_click()

    def down(self):  #Метод срабатывает когда мы нажимаем кнопку
        """Вызывается при нажатии ЛКМ на кнопку"""
        self.is_pressed = True
        self.is_updated = False
        print(f"Кнопка '{self.text}' нажата")

    def hover(self):  #Метод срабатывает когда курсор над кнопкой
        """Вызывается, когда курсор впервые попадает на кнопку"""
        self.is_updated = False
        print(f"Курсор над кнопкой '{self.text}'")
        # Позже сюда можно добавить звук или анимацию

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:

            # Проверяем, находится ли курсор над кнопкой
            if self.collide_to_point(event.pos):
                if self.collide_point_with_mask(event.pos):
                    if not self.is_hovered:
                        self.hover()  # только при входе в область
                    self.is_hovered = True
            else:
                self.is_hovered = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # ЛКМ
                if self.collide_point_with_mask(event.pos):
                    self.down()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.is_pressed and self.is_hovered:
                    self.up()  # кнопка была нажата И отпущена над ней

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.get_absolute_rect())

    def update(self, delta_time: float) -> None:
        if self.is_updated:
            return
        self._update_surface(delta_time)
