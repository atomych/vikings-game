import pygame
import cv2
import numpy as np
from scenes.scene import Scene


class IntroScene(Scene):
    def __init__(self, scene_manager):
        super().__init__("Intro", scene_manager)
        self._cap = None  # VideoCapture от OpenCV
        self._frame_surface = None
        self._fps = 60.0
        self._frame_timer = 0.0  # накопленное время до следующего кадра
        self._target_size = None  # целевой размер экрана
        self._use_smooth_scaling = True  # использовать сглаживание
        self._sound = None  # звук для видео
        self._sound_played = False  # флаг, что звук уже запущен

    def on_enter(self):
        # Получаем размер экрана для масштабирования
        screen = self.ref_scene_manager.ref_game.screen
        self._target_size = screen.get_size()

        # Загружаем и запускаем звук
        try:
            self._sound = pygame.mixer.Sound("assets/video/intro.mp3")
            self._sound.play()
            self._sound_played = True
        except pygame.error as e:
            print(f"Не удалось загрузить звук: {e}")
            self._sound = None
            self._sound_played = False

        self._cap = cv2.VideoCapture("assets/video/intro.mp4")
        if self._cap.isOpened():
            self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 60.0

            # Получаем оригинальное разрешение видео
            orig_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            orig_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Если видео меньше экрана, используем сглаживание при масштабировании
            if orig_width < self._target_size[0] or orig_height < self._target_size[1]:
                self._use_smooth_scaling = True
            else:
                self._use_smooth_scaling = False

        self._frame_timer = 0.0
        self._advance_frame()  # показываем первый кадр сразу

    def on_exit(self):
        # Останавливаем звук при выходе
        if self._sound:
            self._sound.stop()
            self._sound = None
        self._sound_played = False

        if self._cap:
            self._cap.release()
            self._cap = None
        self._frame_surface = None
        self._frame_timer = 0.0

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # При пропуске видео останавливаем звук
            if self._sound:
                self._sound.stop()
            self.ref_scene_manager.change_scene("Game")

    def update(self, dt):
        if not self._cap or not self._cap.isOpened():
            return

        self._frame_timer += dt
        frame_duration = 1.0 / self._fps

        # Пропускаем столько кадров, сколько накопилось времени
        while self._frame_timer >= frame_duration:
            self._frame_timer -= frame_duration
            finished = self._advance_frame()
            if finished:
                # Видео закончилось - останавливаем звук и переходим в игру
                if self._sound:
                    self._sound.stop()
                self.ref_scene_manager.change_scene("Game")
                return

    def _advance_frame(self) -> bool:
        """Читает следующий кадр. Возвращает True если видео закончилось."""
        if not self._cap:
            return True

        ret, frame = self._cap.read()
        if not ret:
            return True  # видео закончилось

        # OpenCV даёт BGR — переворачиваем в RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Вариант 1: Используем numpy для более качественного масштабирования (рекомендуется)
        if self._target_size and frame.shape[:2][::-1] != self._target_size:
            # Используем интерполяцию INTER_LANCZOS4 для максимального качества
            # или INTER_CUBIC для хорошего качества/производительности
            h, w = frame.shape[:2]
            target_w, target_h = self._target_size

            # Сохраняем соотношение сторон, если нужно
            # Можно закомментировать, если нужно растянуть на весь экран
            aspect_ratio = w / h
            target_aspect = target_w / target_h

            if aspect_ratio > target_aspect:
                # Видео шире экрана
                new_w = target_w
                new_h = int(target_w / aspect_ratio)
            else:
                # Видео выше экрана
                new_h = target_h
                new_w = int(target_h * aspect_ratio)

            # Масштабируем с высоким качеством через OpenCV
            frame_resized = cv2.resize(frame_rgb, (new_w, new_h),
                                       interpolation=cv2.INTER_LANCZOS4)

            # Создаем черный фон и центрируем видео
            if (new_w, new_h) != self._target_size:
                canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                x_offset = (target_w - new_w) // 2
                y_offset = (target_h - new_h) // 2
                canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = frame_resized
                frame_rgb = canvas
            else:
                frame_rgb = frame_resized
        else:
            # Если размеры совпадают, используем оригинал
            pass

        # Создаем поверхность Pygame
        surf = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))

        # Дополнительное сглаживание через pygame если нужно
        if self._use_smooth_scaling and surf.get_size() != self._target_size:
            # Используем smoothscale для лучшего качества
            surf = pygame.transform.smoothscale(surf, self._target_size)

        self._frame_surface = surf
        return False

    def render(self, surface: pygame.Surface):
        if self._frame_surface:
            surface.blit(self._frame_surface, (0, 0))

        # Подсказка об ESC с тенью для лучшей читаемости
        font = pygame.font.SysFont("Arial", 24, bold=True)

        # Тень
        hint_shadow = font.render("ESC — пропустить", True, (0, 0, 0))
        shadow_pos = (22, surface.get_height() - hint_shadow.get_height() - 18)
        surface.blit(hint_shadow, shadow_pos)

        # Основной текст
        hint = font.render("ESC — пропустить", True, (255, 255, 255))
        text_pos = (20, surface.get_height() - hint.get_height() - 20)
        surface.blit(hint, text_pos)

        # Опционально: показываем индикатор прогресса видео
        if self._cap:
            # Получаем текущую позицию видео (примерно)
            current_frame = self._cap.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self._cap.get(cv2.CAP_PROP_FRAME_COUNT)

            if total_frames > 0:
                progress = current_frame / total_frames
                bar_width = 200
                bar_height = 5
                bar_x = 20
                bar_y = surface.get_height() - 50

                # Фон прогресс-бара
                pygame.draw.rect(surface, (50, 50, 50),
                                 (bar_x, bar_y, bar_width, bar_height))
                # Заполненная часть
                if progress > 0:
                    pygame.draw.rect(surface, (255, 255, 255),
                                     (bar_x, bar_y, int(bar_width * progress), bar_height))
