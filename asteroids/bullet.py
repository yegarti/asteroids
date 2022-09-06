import logging
from typing import Sequence

from asteroids.actor import Actor
from asteroids.animation import Animation
from asteroids.config import get_config
from asteroids.layer import Layer

log = logging.getLogger(__name__)


class Bullet(Actor):
    def __init__(self, ttl=500, damage=1, *args, hit_animation_images: Sequence[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.ttl_ms = ttl
        self.damage = damage
        self._animation_sprites = hit_animation_images

    def hit(self):
        super().hit()
        self.kill()

    def update(self, dt, keys) -> None:
        super().update(dt, keys)
        self.ttl_ms -= dt
        if self.ttl_ms <= 0:
            log.debug("Killing bullet")
            self.kill()

    def on_hit(self):
        self.hit()
        animation = Animation(self._animation_sprites,
                              self.position, 30, 0.8)
        self.groups[Layer.ANIMATIONS].add(animation)
