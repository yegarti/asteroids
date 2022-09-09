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
    duration_s: float = 0

    def __post_init__(self, pos: Vector2):
        super().__post_init__(pos)

    def activate(self):
        SoundManager.play(get_config().powerup_sound)

    @staticmethod
    def new(name: str) -> Type['PowerUp']:
        match name:
            case 'health':
                return Health


class Health(PowerUp):
    def activate(self):
        super().activate()
        try:
            player: Player = self.groups[Layer.PLAYERS].sprites()[0]
            player.health += get_config().power_up_health_amount
        except IndexError:
            pass


class Fire(PowerUp):
    def activate(self):
        # spawn bullet upgrade event
        pass
    pass

class Nuke(PowerUp):
    def activate(self):
        #spawn nuke event
        pass
    pass