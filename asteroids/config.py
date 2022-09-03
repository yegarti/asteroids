from __future__ import annotations
import json
import typing

_config = None


def get_config() -> Config:
    global _config
    if not _config:
        _config = Config()
    return _config


class _BulletConfig(typing.NamedTuple):
    image: str
    sound: str
    speed: float
    scale: float
    ttl: float


class Config(typing.NamedTuple):
    width: int = 1280
    height: int = 720
    size: tuple[int, int] = (1280, 720)
    title: str = 'Asteroids'
    asteroid_max_velocity: float = .5
    asteroid_min_velocity: float = .1
    asteroid_max_angular_velocity: float = 2.0
    player_scale: float = .5
    player_bullet: _BulletConfig = _BulletConfig(speed=1.,
                                                 scale=.8,
                                                 ttl=500,
                                                 image='bullet',
                                                 sound='sfx_laser2')
    alien_bullet: _BulletConfig = _BulletConfig(speed=.5,
                                                scale=1.,
                                                ttl=1000,
                                                image='laserRed01',
                                                sound='laserSmall_002')
    gui_font: str = 'kenvector_future'
