from enum import Enum, IntEnum, auto
from typing import NamedTuple, Any

import pygame as pg
from pygame.event import Event

from asteroids.events.events_info import ShotBulletInfo


class EventId(IntEnum):
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return pg.USEREVENT + count
    SPAWN_ASTEROID = auto()
    SHOT_BULLET = auto()
    BULLET_HIT = auto()
    THRUST_ON = auto()
    PLAYER_DEAD = auto()
    GAME_OVER = auto()


class GameEvents:

    @staticmethod
    def _gen_event(event: EventId, info: NamedTuple):
        return Event(event.value, info=info)

    @staticmethod
    def shot_bullet(info: ShotBulletInfo) -> Event:
        return GameEvents._gen_event(EventId.SHOT_BULLET, info)
