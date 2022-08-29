from __future__ import annotations
import json
import typing

_config = None


def get_config() -> Config:
    if not _config:
        raise RuntimeError("Config has not been set")
    return _config


class Config(typing.NamedTuple):
    width: int
    height: int
    size: tuple[int, int]
    title: str
    asteroid_max_velocity: float
    asteroid_min_velocity: float
    asteroid_max_angular_velocity: float
    player_scale: float
    bullet_speed: float
    alien_bullet_ttl: float
    bullet_ttl: float
    alien_bullet_speed: float
    gui_font: str

    @staticmethod
    def parse(config_file: str):
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
        except Exception:
            raise RuntimeError("Failed to read config file '%s'", config_file)
        size = (data['width'], data['height'])
        return Config(**data, size=size)

    @staticmethod
    def set(config: Config):
        global _config
        _config = config
