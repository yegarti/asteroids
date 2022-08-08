import json
import typing

_config = None


# def get_config():
#     if not _config:
#         _config = Config()
#     return _config


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

    @staticmethod
    def parse(config_file: str):
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
        except Exception:
            raise RuntimeError("Failed to read config file '%s'", config_file)
        size = (data['width'], data['height'])
        return Config(**data, size=size)
