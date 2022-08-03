import logging

from asteroids.actor import Actor

log = logging.getLogger(__name__)


class Bullet(Actor):
    def __init__(self, image, *args, **kwargs):
        super().__init__(image, *args, **kwargs)
        self.ttl_ms = 500
        # WA to avoid spawn with angle=0
        self._rotate(self.angle)

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        self.ttl_ms -= dt
        if self.ttl_ms <= 0:
            log.debug("Killing bullet")
            self.kill()
