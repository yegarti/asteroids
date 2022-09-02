from __future__ import annotations
import json
import typing

_config = None


def get_config() -> Config:
    global _config
    if not _config:
        _config = Config()
    return _config


class Config(typing.NamedTuple):
    width: int = 1280
    height: int = 720
    size: tuple[int, int] = (1280, 720)
    title: str = 'Asteroids'
    asteroid_max_velocity: float = .5
    asteroid_min_velocity: float = .1
    asteroid_max_angular_velocity: float = 2.0
    player_scale: float = .5
    bullet_speed: float = 1.
    alien_bullet_ttl: float = .5
    bullet_ttl: float = 500
    alien_bullet_speed: float = .5
    gui_font: str = 'kenvector_future'
    alien_bullet_image: str = 'laserRed01'
    alien_bullet_sound: str = 'laserSmall_002'
