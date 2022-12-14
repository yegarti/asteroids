import logging
import random
import time

import pygame

from asteroids.actor import Actor
from asteroids.bullet import Bullet
from asteroids.config import get_config
from asteroids.events.events_info import SpawnAsteroidInfo
from asteroids.events.game_events import GameEvents
from asteroids.sound import SoundManager

log = logging.getLogger(__name__)


class Asteroid(Actor):
    HEALTH_TABLE = {'big': 3, 'medium': 2, 'small': 1}
    KILL_TELEPORT_DELTA = .1
    EXPLODE_PARTS = {
        'big': [{'medium': 2, 'small': 1}],
        'medium': [{'small': 2}],
    }
    SCORE = {
        'small': 1, 'medium': 2, 'big': 3
    }

    def __init__(self, angular_velocity, size, color, *args, **kwargs):
        super().__init__(*args, **kwargs, spawned=False)
        self._last_teleport = 0
        self.ANGULAR_SPEED = angular_velocity
        self.ttl_ms = 5000
        self.size = size
        self.health = self.HEALTH_TABLE[size]
        self.color = color
        self.score: int = self.SCORE[self.size]

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        # doesn't make sense...
        inbounds = self.inbounds()
        if inbounds and not self.spawned:
            self.spawned = True

        if not self.spawned and not self.inbounds() and self.ttl_ms < 0:
            log.info("Asteroid time to live passed and not spawned")
            self.kill()
        self.ttl_ms -= dt
        self.rotate_cw()

    def _teleport(self):
        super()._teleport()
        # asteroid may be stuck in odd position keeping it teleported very fast
        if time.time() - self._last_teleport < self.KILL_TELEPORT_DELTA:
            self.kill()
        self._last_teleport = time.time()

    def explode(self):
        self.kill()
        parts_opts = self.EXPLODE_PARTS.get(self.size)
        # asteroid too small
        if not parts_opts:
            return

        parts = random.choice(parts_opts)
        log.info('Exploding %s asteroid to %s', self.size, parts)
        for size, amount in parts.items():
            for _ in range(amount):
                pygame.event.post(
                    GameEvents.spawn_asteroid(SpawnAsteroidInfo(
                        position=self.position,
                        size=size,
                        color=self.color
                    ))
                )

    def on_bullet_hit(self, bullet: Bullet):
        self.hit()
        self.health -= bullet.damage
        if self.is_dead():
            self.explode()
            SoundManager.play(get_config().explosion_sound, volume=40)
        else:
            SoundManager.play(get_config().hit_sound, volume=30)
