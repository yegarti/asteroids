import math

import pygame

from asteroids.actor import Actor
from asteroids.config import get_config
from asteroids.events.game_events import GameEvents
from asteroids.events.events_info import ShotBulletInfo
from asteroids.layer import Layer
from asteroids.player import Player


class Alien(Actor):

    SHOT_COOLDOWN_MS = 1500
    ANGULAR_SPEED = 4.4

    def __init__(self, *args, **kwargs):
        super().__init__('ufoGreen', *args, **kwargs)
        self._cooldown = self.SHOT_COOLDOWN_MS
        self.health = 5

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
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
        if self._cooldown == 0:
            pygame.event.post(
                GameEvents.shot_bullet(
                    ShotBulletInfo(
                        self.position,
                        get_config().alien_bullet_speed,
                        self.velocity,
                        shot_direction,
                        get_config().alien_bullet_ttl,
                    ))
            )
            self._cooldown = self.SHOT_COOLDOWN_MS
