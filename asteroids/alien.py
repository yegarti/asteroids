import math

import pygame

from asteroids.actor import Actor
from asteroids.config import get_config
from asteroids.events.game_events import GameEvents
from asteroids.events.events_info import ShotBulletInfo
from asteroids.layer import Layer
from asteroids.player import Player
from asteroids.utils import load_image, load_sound


class Alien(Actor):

    SHOT_COOLDOWN_MS = 1000
    ANGULAR_SPEED = 4.4

    def __init__(self, *args, **kwargs):
        super().__init__('ufoGreen', *args, **kwargs)
        self._cooldown = self.SHOT_COOLDOWN_MS
        self.health = 5
        self.teleport = False
        self.spawned = False
        self._dead = False

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        if self._dead:
            self._die_slowly(dt)
            return
        if self.inbounds() and not self.spawned:
            self.spawned = True
        self.rotate_cw()
        self._cooldown -= dt
        self._cooldown = max(self._cooldown, 0)
        try:
            player: Player = self.groups[Layer.PLAYERS].sprites()[0]
        except IndexError:
            return
        d = self.position - player.position
        d.y = 1e-6 if d.y == 0 else d.y
        d.x = 1e-6 if d.x == 0 else d.x
        if self.position.y >= player.position.y:
            angle = math.degrees(math.atan(d.x / d.y))
        else:
            angle = 180 + math.degrees(math.atan(d.x / d.y))
        shot_direction = angle
        # print(d, self.position.angle_to(d))
        # shot_direction = self.position.angle_to(d)
        if self._cooldown == 0 and self.spawned:
            pygame.event.post(
                GameEvents.shot_bullet(
                    ShotBulletInfo(
                        position=self.position,
                        velocity=get_config().alien_bullet_speed,
                        constant_velocity=self.velocity,
                        angle=shot_direction,
                        duration=get_config().alien_bullet_ttl,
                        layer=Layer.ENEMY_BULLETS,
                    ))
            )
            self._cooldown = self.SHOT_COOLDOWN_MS

    def _die_slowly(self, dt):
        self.angle += 300 * dt / 1000
        self.alpha = self.alpha * .96
        if self.alpha < .2:
            self.kill()

    def explode(self):
        self._dead = True
        self.active = False
        self.velocity = pygame.Vector2(0, 0)
        self.thrust = 0
