import pygame as pg
from pygame.locals import *

from asteroids.actor import Actor
from asteroids.events import AsteroidsEvent
from asteroids.utils import load_image


class Player(Actor):
    ANGULAR_SPEED = 1.5
    SHOT_COOLDOWN_MS = 150

    def __init__(self, image, *args, **kwargs):
        super().__init__(image, *args, **kwargs)
        self._cooldown = 0

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        if keys[K_d]:
            self.rotate_cw()
        if keys[K_a]:
            self.rotate_ccw()
        if keys[K_s]:
            self.decelerate()
        if keys[K_w]:
            self.accelerate()
        if keys[K_SPACE]:
            if self._cooldown <= 0:
                self.shot()
                self._cooldown = self.SHOT_COOLDOWN_MS
        self._cooldown -= dt
        self._cooldown = max(self._cooldown, 0)

    def shot(self):
        pg.event.post(pg.event.Event(AsteroidsEvent.SHOT_BULLET))
