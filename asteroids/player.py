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
    FRONT_THURST_OFFSET = (0, 30)

    def __init__(self, *args, **kwargs):
        super().__init__('player', *args, **kwargs)
        self._cooldown = 0
        self.health = 1
        self._front_thrust = StaticActor('fire01')

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        if keys[K_d]:
            self.rotate_cw()
        if keys[K_a]:
            self.rotate_ccw()
        if keys[K_w]:
            self.accelerate()
            self.groups[Layer.PLAYERS].add(self._front_thrust)
            self._front_thrust.position = self.position
            self._front_thrust.rotate(self.angle, pivot=self.position + self.FRONT_THURST_OFFSET)
        else:
            self._front_thrust.kill()

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
