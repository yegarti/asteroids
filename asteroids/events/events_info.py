from typing import NamedTuple, Sequence, Optional, Type

import pygame
from pygame import Vector2

from asteroids.config import _BulletConfig
from asteroids.layer import Layer


class ShotBulletInfo(NamedTuple):
    position: Vector2
    bullet_config: _BulletConfig
    angle: float
    layer: Layer


class SpawnAsteroidInfo(NamedTuple):
    position: Optional[Vector2]
    size: str
    color: Optional[str]


class SpawnAlienInfo(NamedTuple):
    probability: float


class SpawnPowerUpInfo(NamedTuple):
    power_up: str
