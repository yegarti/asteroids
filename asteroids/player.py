import pygame as pg
import pygame.display
from pygame.locals import *
from pygame.math import Vector2

from asteroids.actor import Actor
from asteroids.bullet import Bullet
from asteroids.config import get_config
from asteroids.display import Display
from asteroids.events.events_info import ShotBulletInfo
from asteroids.events.game_events import EventId, GameEvents
from asteroids.layer import Layer
from asteroids.sound import SoundManager
from asteroids.static_actor import StaticActor


class Player(Actor):
    ANGULAR_SPEED = 3.5
    MAX_VELOCITY = .3
    FRONT_THURST_OFFSET = (0, 30)

    def __init__(self, *args, **kwargs):
        super().__init__('player', *args, **kwargs)
        self._cooldown = 0
        self._health = 100
        self._front_thrust = StaticActor('fire01')
        self._dead = False
        self.laser_max_level = len(get_config().player_bullet) - 1
        self.laser_level = 0
        self._bullet_config = get_config().player_bullet[self.laser_level]

    @property
    def laser_level(self):
        return self._laser_level

    @laser_level.setter
    def laser_level(self, value):
        self._laser_level = min(value, self.laser_max_level)
        self._bullet_config = get_config().player_bullet[self.laser_level]

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = min(value, 100)

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
                self._cooldown = self._bullet_config.cooldown
        self._cooldown -= dt
        self._cooldown = max(self._cooldown, 0)

    def shot(self):
        pg.event.post(GameEvents.shot_bullet(ShotBulletInfo(
            position=self.position,
            angle=self.angle,
            layer=Layer.BULLETS,
            bullet_config=self._bullet_config,
        )))

    def _die_slowly(self, dt):
        self.angle += 300 * dt / 1000
        self.alpha = self.alpha * .96
        if self.alpha < .2:
            self.kill()
            pygame.event.post(GameEvents.player_dead())

    def explode(self):
        self._dead = True
        self.active = False
        self.velocity = Vector2(0, 0)
        self._front_thrust.kill()
        self.thrust = 0

    def on_asteroid_hit(self):
        self.health -= get_config().player_asteroid_damage
        self.hit()
        SoundManager.play(get_config().impact_sound, unique=True)

    def on_bullet_hit(self, bullet: Bullet):
        self.health -= bullet.damage
        self.hit()