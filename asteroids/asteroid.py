import logging
import random

import pygame

from asteroids.actor import Actor
from asteroids.events import AsteroidsEvent

log = logging.getLogger(__name__)


class Asteroid(Actor):
    HEALTH_TABLE = {'big': 3, 'medium': 2, 'small': 1}
    EXPLODE_PARTS = {
        'big': [{'medium': 2, 'small':1}],
        'medium': [{'small': 2}],
    }

    def __init__(self, angular_velocity, size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ANGULAR_SPEED = angular_velocity
        self.spawned = False
        self.ttl_ms = 5000
        self.size = size
        self.health = self.HEALTH_TABLE[size]

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        # doesn't make sense...
        inbounds = self.inbounds()
        if inbounds and not self.spawned:
            self.spawned = True

        if not inbounds:
            if self.spawned:
                log.debug("Asteroid out of bound")
                self.kill()
            elif self.ttl_ms < 0:
                log.debug("Asteroid time to live passed and not spawned")
                self.kill()
        if self.is_dead():
            self.kill()
        self.ttl_ms -= dt
        self.rotate_cw()

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
                pygame.event.post(pygame.event.Event(
                    AsteroidsEvent.SPAWN_ASTEROID,
                    size=size, position=self.position))
