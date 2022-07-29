import pygame as pg
from pygame.math import Vector2
import pygame.transform


# @dataclass(unsafe_hash=True)
from asteroids.utils import load_image


class Actor(pg.sprite.Sprite):
    def __init__(self, image_name, scale=1.):
        super().__init__()
        self._original_image = load_image(image_name)
        self._scale(scale)
        self.image = self._original_image.copy()
        self.velocity = Vector2(0, 0)
        self.position = Vector2(0, 0)
        self.angle = 0

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        self.rect = self.image.get_rect()

    def _scale(self, factor):
        self._original_image = pg.transform.scale(
            self._original_image,
            (factor * self._original_image.get_width(),
             factor * self._original_image.get_height()))

    def update(self, dt) -> None:
        self.position += self.velocity * dt
        self.rect.x = self.position.x
        self.rect.y = self.position.y
