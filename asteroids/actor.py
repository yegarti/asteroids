import operator
from dataclasses import dataclass, field

import pygame as pg
import pygame.transform


@dataclass
class Actor(pg.sprite.Sprite):
    image: pg.Surface
    position: tuple[int, int]
    velocity: tuple[float, float]
    angle: float = 0
    rect: pg.Rect = field(init=False)

    def __post_init__(self):
        # self.rect.center =
        self.rect = self.image.get_rect()

    def move(self, x, y):
        self.rect.move_ip(x, y)

    def rotate(self, angle):
        self.angle += angle

    def render(self):
        image = pygame.transform.rotate(self.image, self.angle)
        return image, image.get_rect()
