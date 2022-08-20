import pygame as pg
import pygame.display
from pygame.locals import *
from pygame.math import Vector2

from asteroids.actor import Actor
from asteroids.asteroids import Layer
from asteroids.display import Display
from asteroids.events import AsteroidsEvent
from asteroids.static_actor import StaticActor
from asteroids.utils import load_image


class Player(Actor):
    ANGULAR_SPEED = 3.5
    SHOT_COOLDOWN_MS = 150
    MAX_VELOCITY = .3

    def __init__(self, *args, **kwargs):
        super().__init__('player', *args, **kwargs)
        # self._thrust = Actor(image='fire1')
        self._cooldown = 0
        self.health = 1
        self._thurst_accel = StaticActor('fire01')

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        if keys[K_d]:
            self.rotate_cw()
        if keys[K_a]:
            self.rotate_ccw()
        if keys[K_w]:
            self.accelerate()
            self.groups[Layer.PLAYERS].add(self._thurst_accel)
            self._thurst_accel.position = self.position
            self._thurst_accel.rotate(self.angle, pivot=self.position + Vector2(0, 30))
        else:
            self._thurst_accel.kill()

        if keys[K_r]:
            self.position = Display.get_center()
            self.velocity.x = self.velocity.y = 0
        if keys[K_SPACE]:
            if self._cooldown <= 0:
                self.shot()
                self._cooldown = self.SHOT_COOLDOWN_MS
        self._cooldown -= dt
        self._cooldown = max(self._cooldown, 0)

    def shot(self):
        pg.event.post(pg.event.Event(AsteroidsEvent.SHOT_BULLET))
