from enum import Enum, IntEnum
from typing import NamedTuple

import pygame as pg
from pygame.event import Event

from asteroids.events.events_info import ShotBulletInfo


class EventId(IntEnum):
    SPAWN_ASTEROID = pg.USEREVENT + 1
    SHOT_BULLET = pg.USEREVENT + 2
    BULLET_HIT = pg.USEREVENT + 3
    THRUST_ON = pg.USEREVENT + 4
    PLAYER_DEAD = pg.USEREVENT + 5
    GAME_OVER = pg.USEREVENT + 6


class GameEvents:

    @staticmethod
    def _gen_event(event: EventId, info: NamedTuple):
        return Event(event.value, info=info)

    @staticmethod
    def shot_bullet(info: ShotBulletInfo) -> Event:
        return GameEvents._gen_event(EventId.SHOT_BULLET, info)
