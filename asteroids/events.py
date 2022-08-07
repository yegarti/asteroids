import pygame as pg


class AsteroidsEvent:
    SPAWN_ASTEROID = pg.USEREVENT + 1
    SHOT_BULLET = pg.USEREVENT + 2
    BULLET_HIT = pg.USEREVENT + 3
