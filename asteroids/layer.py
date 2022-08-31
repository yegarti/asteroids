from enum import IntEnum, auto


class Layer(IntEnum):
    ASTEROIDS = auto()
    BULLETS = auto()
    PLAYERS = auto()
    ENEMY_BULLETS = auto()
    ENEMIES = auto()
    ANIMATIONS = auto()
