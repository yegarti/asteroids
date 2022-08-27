import pygame as pg
import pygame.display
from pygame.locals import *
from pygame.math import Vector2

from asteroids.actor import Actor
from asteroids.asteroids import Layer
from asteroids.display import Display
from asteroids.events import AsteroidsEvent
from asteroids.static_actor import StaticActor


class Player(Actor):
    ANGULAR_SPEED = 3.5
    SHOT_COOLDOWN_MS = 330
    MAX_VELOCITY = .3
    FRONT_THURST_OFFSET = (0, 30)

    def __init__(self, *args, **kwargs):
        super().__init__('player', *args, **kwargs)
        self._cooldown = 0
        self.health = 100
        self._front_thrust = StaticActor('fire01')
        self._dead = False

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        if self._dead:
            self._die_slowly(dt)
            return
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
        if keys[K_g]:
            self.explode()
        if keys[K_SPACE]:
            if self._cooldown <= 0:
                self.shot()
                self._cooldown = self.SHOT_COOLDOWN_MS
        self._cooldown -= dt
        self._cooldown = max(self._cooldown, 0)

    def shot(self):
        pg.event.post(pg.event.Event(AsteroidsEvent.SHOT_BULLET))

    def _die_slowly(self, dt):
        self.angle += 300 * dt / 1000
        self.alpha = self.alpha * .96
        if self.alpha < .2:
            self.kill()
            pygame.event.post(pygame.event.Event(AsteroidsEvent.PLAYER_DEAD))

    def explode(self):
        self._dead = True
        self.active = False
        self.velocity = Vector2(0, 0)
        self._front_thrust.kill()
        self.thrust = 0
