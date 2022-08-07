import logging

from asteroids.actor import Actor

log = logging.getLogger(__name__)


class Bullet(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__('bullet', *args, **kwargs)
        self.ttl_ms = 500

    def hit(self):
        super().hit()
        self.kill()

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        self.ttl_ms -= dt
        if self.ttl_ms <= 0:
            log.debug("Killing bullet")
            self.kill()
