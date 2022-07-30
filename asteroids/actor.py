import math

import pygame as pg
from pygame.math import Vector2
import pygame.transform


# @dataclass(unsafe_hash=True)
from asteroids.utils import load_image


class Actor(pg.sprite.Sprite):
    ACCELERATION = 0.01
    VELOCITY_MULT = .5
    ANGULAR_SPEED = 1.5
    MAX_VELOCITY = 1.
    THRUST_MULT = .01

    def __init__(self, image, scale=1.,
                 position=(0, 0)):
        super().__init__()
        self._original_image = load_image(image)
        self._scale(scale)
        self.image: pg.Surface = self._original_image.copy()
        self.rect = self.image.get_rect()
        self.velocity = Vector2(0, 0)
        self.position = Vector2(position)
        self.angle = 0
        self.thrust = 0
        self._delta = 0

    def _scale(self, factor):
        self._original_image = pg.transform.scale(
            self._original_image,
            (factor * self._original_image.get_width(),
             factor * self._original_image.get_height()))

    def update(self, dt, keys) -> None:
        self._delta = dt
        dx = -math.sin(math.radians(self.angle)) * self.thrust
        dy = -math.cos(math.radians(self.angle)) * self.thrust
        self.velocity += (dx, dy)
        self.thrust = 0
        self.position += self.velocity * dt * self.VELOCITY_MULT
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

    def accelerate(self):
        self.thrust = self.THRUST_MULT

    def decelerate(self):
        self.thrust = -self.THRUST_MULT

    def rotate_ccw(self):
        self.angle += self.ANGULAR_SPEED
        if self.angle >= 360:
            self.angle = 0

    def rotate_cw(self):
        self.angle -= self.ANGULAR_SPEED
        if self.angle <= 0:
            self.angle = 360
