import pygame as pg
import pygame.display
from pygame.locals import *

from asteroids.actor import Actor
from asteroids.events import AsteroidsEvent


class Player(Actor):
    ANGULAR_SPEED = 2.5
    SHOT_COOLDOWN_MS = 150
    MAX_VELOCITY = .3

    def __init__(self, *args, **kwargs):
        super().__init__('player', *args, **kwargs)
        self._cooldown = 0
        self.health = 1

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
        if keys[K_r]:
            self.position = tuple(c // 2 for c in pygame.display.get_window_size())
            self.velocity.x = self.velocity.y = 0
        if keys[K_SPACE]:
            if self._cooldown <= 0:
                self.shot()
                self._cooldown = self.SHOT_COOLDOWN_MS
        self._cooldown -= dt
        self._cooldown = max(self._cooldown, 0)

    def shot(self):
        pg.event.post(pg.event.Event(AsteroidsEvent.SHOT_BULLET))
