from __future__ import annotations
from typing import NamedTuple

_config = None


def get_config() -> Config:
    global _config
    if not _config:
        _config = Config()
    return _config


class _BulletConfig(NamedTuple):
    image: str
    sound: str
    velocity: float
    scale: float
    duration: float
    cooldown: float
    damage: int
    hit_images: tuple[str, ...]


class _PowerConfig(NamedTuple):
    image: str
    duration_s: tuple[int, int]
    frequency: float


class Config(NamedTuple):
    width: int = 1280
    height: int = 720
    size: tuple[int, int] = (1280, 720)
    title: str = 'Asteroids'
    asteroid_max_velocity: float = .5
    asteroid_min_velocity: float = .1
    asteroid_max_angular_velocity: float = 2.0
    asteroid_spawn_frequency_ms: int = 1000
    max_asteroids: int = 15
    lives: int = 3
    player_asteroid_damage: float = .5
    player_scale: float = .5
    player_bullet: tuple[_BulletConfig] = (
        _BulletConfig(velocity=1.,
                      scale=.8,
                      duration=500,
                      cooldown=330,
                      image='bullet',
                      sound='sfx_laser2',
                      damage=1,
                      hit_images=('bullet_hit1', 'bullet_hit2')),
        _BulletConfig(velocity=1.,
                      scale=.8,
                      duration=500,
                      cooldown=200,
                      image='bullet',
                      sound='sfx_laser2',
                      damage=1,
                      hit_images=('bullet_hit1', 'bullet_hit2')),
        _BulletConfig(velocity=1.,
                      scale=.8,
                      duration=1000,
                      cooldown=200,
                      image='bullet',
                      sound='sfx_laser2',
                      damage=1,
                      hit_images=('bullet_hit1', 'bullet_hit2')),
    )
    alien_spawn_frequency_per_seconds: float = .05
    alien_velocity: float = .2
    alien_bullet: _BulletConfig = _BulletConfig(velocity=.5,
                                                scale=1.,
                                                duration=1000,
                                                cooldown=1000,
                                                image='laserRed01',
                                                sound='laserSmall_002',
                                                damage=10,
                                                hit_images=('laserRed08', 'laserRed09'))
    alien_sound: str = 'spaceEngineLow_003'
    alien_explosion_sound: str = 'explosionCrunch_004'
    gui_font: str = 'kenvector_future'
    player_die_sound: str = 'sfx_lose'
    impact_sound: str = 'impactMetal_000'
    thrust_sound: str = 'thrusterFire_000'
    explosion_sound: str = 'explosionCrunch_000'
    hit_sound: str = 'lowFrequency_explosion_000'
    global_volume: float = .5
    power_up: dict[str, _PowerConfig] = {
        'health': _PowerConfig(
            image='pill_green',
            duration_s=(20, 60),
            frequency=0.5
        ),
        'laser': _PowerConfig(
            image='things_blue',
            duration_s=(10, 20),
            frequency=0.1,
        )
    }
    power_up_freq_s: float = 10
    power_up_spawn_area: float = 0.1
    powerup_sound: str = 'sfx_twoTone'
    power_up_health_amount: int = 20
