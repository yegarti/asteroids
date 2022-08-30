from typing import NamedTuple

import pygame
from pygame import Vector2


class ShotBulletInfo(NamedTuple):
    position: Vector2
    velocity: float
    constant_velocity: Vector2
    angle: float
    duration: float
