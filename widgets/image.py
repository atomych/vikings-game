import pygame.image

from widgets.widget import Widget


class Image(Widget):
    def __init__(self, pos, file_name):
        image =  pygame.image.load(file_name)
        if image:
            self.surface = image
        else