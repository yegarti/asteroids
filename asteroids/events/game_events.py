from enum import Enum, IntEnum, auto
from typing import NamedTuple, Any

import pygame as pg
from pygame.event import Event

from asteroids.events.events_info import ShotBulletInfo, SpawnAsteroidInfo, SpawnAlienInfo


class EventId(IntEnum):
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        return pg.USEREVENT + count
    SPAWN_ASTEROID = auto()
    SHOT_BULLET = auto()
    PLAYER_DEAD = auto()
    SPAWN_ALIEN = auto()
    GAME_OVER = auto()


class GameEvents:

    @staticmethod
    def _gen_event(event: EventId, info: NamedTuple = None):
        return Event(event.value, info=info)

    @staticmethod
    def shot_bullet(info: ShotBulletInfo) -> Event:
        return GameEvents._gen_event(EventId.SHOT_BULLET, info)

    @staticmethod
    def spawn_asteroid(info: SpawnAsteroidInfo) -> Event:
        return GameEvents._gen_event(EventId.SPAWN_ASTEROID, info)

    @staticmethod
    def player_dead() -> Event:
        return GameEvents._gen_event(EventId.PLAYER_DEAD)

    @staticmethod
    def spawn_alien(info: SpawnAlienInfo) -> Event:
        return GameEvents._gen_event(EventId.SPAWN_ALIEN, info)

    @staticmethod
    def game_over() -> Event:
        return GameEvents._gen_event(EventId.GAME_OVER)
