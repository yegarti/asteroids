import logging

from asteroids.actor import Actor


log = logging.getLogger(__name__)


class Asteroid(Actor):
    def __init__(self, angular_velocity, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ANGULAR_SPEED = angular_velocity
        self.spawned = False
        self.ttl_ms = 5000

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
        self.ttl_ms -= dt
        self.rotate_cw()
