from typing import Sequence

import pygame.sprite
from pygame.math import Vector2

from asteroids.utils import load_image


class Animation(pygame.sprite.Sprite):
    def __init__(self, images: Sequence[str], center: tuple, fps: float,
                 scale: float = 1.):
        super().__init__()
        self._images = list(images)
        self._scale = scale
        self._center = center
        self._frame_delta = 0
        self._delta = 1 / fps * 1000
        self._load_next_frame()
        # self._delta = 1

    def _load_next_frame(self):
        if not self._images:
            self.kill()
            return
        image = self._images.pop(0)
        self.image = load_image(image)
        self.image = pygame.transform.scale(
            self.image,
            (self._scale * self.image.get_width(),
             self._scale * self.image.get_height()))
        self.rect = self.image.get_rect()
        self.rect.center = self._center

    def update(self, dt, keys):
        self._frame_delta += dt
        if self._frame_delta >= self._delta:
            self._load_next_frame()
            self._frame_delta = 0
