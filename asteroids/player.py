import pygame as pg
from pygame.locals import *

from asteroids.actor import Actor
from asteroids.utils import load_image


class Player(Actor):
    ANGULAR_SPEED = 1.5
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        if keys[K_d]:
            self.rotate_cw()
        if keys[K_a]:
            self.rotate_ccw()
        # if keys[K_s]:
        #     self.decelerate()
        if keys[K_w]:
            self.accelerate()
