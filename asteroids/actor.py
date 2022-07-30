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
        self.image: pg.Surface = self._original_image.copy()
        self.rect = self.image.get_rect()
        self.velocity = Vector2(0, 0)
        self.position = Vector2(0, 0)
        self.angle = 0

    def _scale(self, factor):
        self._original_image = pg.transform.scale(
            self._original_image,
            (factor * self._original_image.get_width(),
             factor * self._original_image.get_height()))

    def update(self, dt, keys) -> None:
        self.position += self.velocity * dt
        self._rotate(self.angle)

    def _rotate(self, angle):
        # using // reduce the vibrations
        center = self._original_image.get_width() // 2, self._original_image.get_height() // 2
        image_rect = self._original_image.get_rect(topleft=(self.position.x - center[0], self.position.y - center[1]))

        offset_center_to_pivot = self.position - image_rect.center

        # rotated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # rotated image center
        rotated_image_center = (self.position.x - rotated_offset.x,
                                self.position.y - rotated_offset.y)

        # using rotozoom to same smooth edges
        rotated_image = pygame.transform.rotozoom(self._original_image, angle, 1.0)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

        self.image = rotated_image
        self.rect = rotated_image_rect

    def rotate_ccw(self, angle):
        self.angle += angle

    def rotate_cw(self, angle):
        self.angle -= angle
