import math
from dataclasses import dataclass, field, InitVar

import pygame
from pygame import Rect
from pygame.sprite import Group, Sprite
from pygame.math import Vector2

from pygame.surface import Surface

from asteroids.display import Display
from asteroids.utils import load_image


@dataclass(eq=False)
class StaticActor(Sprite):
    image_name: str
    scale: float = 1
    pos: InitVar[Vector2] = Vector2(0, 0)
    spawned: bool = True
    image: Surface = field(init=False, repr=False)
    rect: Rect = field(init=False, repr=False)
    alpha: float = 1.
    radius: float = field(init=False)
    _original_image: Surface = field(init=False, repr=False)
    _position: Vector2 = field(init=False)

    HITBOX_RADIUS_RATIO = 0.9

    def __post_init__(self, pos: Vector2):
        super().__init__()
        self._original_image = load_image(self.image_name)
        self._scale(self.scale)
        self.image = self._original_image.copy()
        self.image.set_alpha(math.floor(self.alpha * 255))
        self.rect = self.image.get_rect()
        self.position = Vector2(pos)
        self.radius = self.image.get_width() / 2 * self.HITBOX_RADIUS_RATIO

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = Vector2(value)
        self.rect.center = self._position

    def _scale(self, factor):
        self._original_image = pygame.transform.scale(
            self._original_image,
            (factor * self._original_image.get_width(),
             factor * self._original_image.get_height()))

    def rotate(self, angle, pivot=None):
        # using // reduce the vibrations
        if not pivot:
            center = self._original_image.get_width() // 2, self._original_image.get_height() // 2
            image_rect = self._original_image.get_rect(topleft=(self.position.x - center[0], self.position.y - center[1]))
            pivot = image_rect.center

        offset_center_to_pivot = self.position - pivot

        # rotated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # rotated image center
        rotated_image_center = (self.position.x - rotated_offset.x,
                                self.position.y - rotated_offset.y)

        # using rotozoom to smooth edges
        rotated_image = pygame.transform.rotozoom(self._original_image, angle, 1.0)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

        self.image = rotated_image
        self.rect = rotated_image_rect
        self.image.set_alpha(math.floor(self.alpha * 255))

    def inbounds(self):
        return Display.get_rect().colliderect(self.rect)
