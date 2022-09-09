from typing import NamedTuple, Sequence, Optional, Type

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


class SpawnAsteroidInfo(NamedTuple):
    position: Optional[Vector2]
    size: str
    color: Optional[str]


class SpawnAlienInfo(NamedTuple):
    probability: float


class SpawnPowerUpInfo(NamedTuple):
    position: Vector2
    duration: float
    image: str
    scale: float
    power_up: str
