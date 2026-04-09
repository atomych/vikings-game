import uuid
from typing import Optional, Dict

import pygame

from game_objects.component import Component
from game_objects.gobject import GameObject
from game_objects.player import Player
from game_objects.ground import Map







class WorldMap(GameObject):
    def __init__(self, name: str = "WorldMap"):
        super().__init__(name)
        self.surface: pygame.Surface = None
        #self.map = Map(40, 40)



    def initialize_world(self):
        self.surface = pygame.image.load("assets//image//mode_placeholders//res.png")


    def update(self, delta_time: float) -> None:
        pass


    def render(self, surface: pygame.Surface) -> None:
        pass




    def handle_event(self, event: pygame.event.Event) -> bool:
        pass


