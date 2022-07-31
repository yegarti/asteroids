from asteroids.actor import Actor


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
                self.kill()
                print('bye')
            elif self.ttl_ms < 0:
                self.kill()
                print('ttl')
        self.ttl_ms -= dt
        self.rotate_cw()
