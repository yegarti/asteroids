from typing import NamedTuple, Sequence

import pygame
from pygame import Vector2

from asteroids.layer import Layer


class ShotBulletInfo(NamedTuple):
    position: Vector2
    velocity: float
    constant_velocity: Vector2
    angle: float
    duration: float
    layer: Layer
    image: str
    sound: str
    scale: float
    damage: int
    hit_images: Sequence[str]
