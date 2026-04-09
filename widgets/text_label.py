import enum

import pygame

from widgets.widget import Widget

class TextAlignmentType(enum.Enum):
    LEFT = 0,
    CENTER = 0,
    RIGHT = 0


class TextLabel(Widget):
    def __init__(self,
                 text: str = "",
                 x=0, y=0,
                 width:int =0, height: int =0,
                 font_size:int =25,
                 font_name='Times new roman',
                 widget_name="Text label"):
        super().__init__(widget_name)
        self.rect = pygame.Rect((x, y),(width, height))

        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.color = (255, 255, 255)

        self._text_blocks: list[str] = []
        self._current_block = 0

        self._font = None
        self._rendered_lines: list[pygame.Surface] = []
        self.update_text()

    def update_text(self):
        """Обновляет внутренние данные текста и его отображение."""
        self._font = pygame.font.SysFont(self.font_name, self.font_size)
        self._wrap_text()

    def _wrap_text(self):
        """Разбивает текст на строки по ширине self.rect.width."""
        self._rendered_lines.clear()
        words = self.text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self._font.size(test_line)[0] <= self.rect.width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line[:-1])  # Убираем лишний пробел
                current_line = word + " "

        if current_line:
            lines.append(current_line[:-1])

        for line in lines:
            self._rendered_lines.append(self._font.render(line, True, self.color))

    def set_text(self, text: str):
        self.text = text
        self.update_text()

    def set_color(self, color: tuple[int, int, int]):
        self.color = color
        self.update_text()

    def render(self, screen: pygame.Surface):
        y_offset = self.rect.y
        print(len(self._rendered_lines))
        for line_surface in self._rendered_lines:
            screen.blit(line_surface, (self.rect.x, y_offset))
            y_offset += self._font.get_height()  # Переходим на следующую строку

    def handle_event(self, event: pygame.event.Event) -> bool:
        pass

    def update(self, delta_time: float) -> None:
        pass