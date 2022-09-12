from abc import abstractmethod
from dataclasses import dataclass
from typing import Type

from pygame import Vector2

from asteroids.config import get_config
from asteroids.layer import Layer
from asteroids.player import Player
from asteroids.sound import SoundManager
from asteroids.static_actor import StaticActor


@dataclass(eq=False)
class PowerUp(StaticActor):
    duration: float = 0

    def __post_init__(self, pos: Vector2):
        super().__post_init__(pos)

    def activate(self):
        SoundManager.play(get_config().powerup_sound)

    def can_spawn(self):
        return True

    def _get_player(self):
        player = None
        try:
            player: Player = self.groups[Layer.PLAYERS].sprites()[0]
        except IndexError:
            pass
        return player

    @staticmethod
    def new(name: str) -> Type['PowerUp']:
        match name:
            case 'health':
                return Health
            case 'laser':
                return Fire
            case _:
                raise ValueError(f'Unknown powerup: {name}')


class Health(PowerUp):
    def activate(self):
        super().activate()
        if player := self._get_player():
            player.health += get_config().power_up_health_amount


class Fire(PowerUp):
    def activate(self):
        super().activate()
        if player := self._get_player():
            player.laser_level += 1

    def can_spawn(self):
        if player := self._get_player():
            return player.laser_level < player.laser_max_level
        return False
