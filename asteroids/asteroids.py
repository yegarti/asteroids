from random import random, choice

import pygame as pg
import pygame.display
from pygame.locals import *

from asteroids.actor import Actor
from asteroids.asteroid import Asteroid
from asteroids.events import AsteroidsEvent
from asteroids.player import Player
from asteroids.utils import load_image, repeat_surface


class Asteroids:
    MOVEMENT_SCALAR = 0.25
    ANGLE = 0.1
    PLAYER_SCALE = 0.5
    ASTEROID_MAX_VELOCITY = 0.5
    ASTEROID_MAX_ANGULAR_VELOCITY = 2.0

    def __init__(self, width, height, title='Asteroids'):
        pg.display.set_caption(title)
        self.screen = pg.display.set_mode((width, height))
        self.is_running = True
        self._clock = pygame.time.Clock()
        self.background = repeat_surface(self.screen.get_size(),
                                         load_image('purple'))
        self.player = Player(image='player',
                             position=self._get_center(),
                             scale=0.5)
        self.all_actors = pygame.sprite.Group()
        self.all_actors.add(self.player)

        self.delta = 0
        pg.time.set_timer(AsteroidsEvent.SPAWN_ASTEROID, 1000)

    def _get_center(self):
        return (self.screen.get_width() // 2,
                self.screen.get_height() // 2)

    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or \
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.is_running = False
            if event.type == AsteroidsEvent.SPAWN_ASTEROID:
                self._spawn_asteroid()

    def _random_value_in_range(self, min_val: float, max_val: float):
        value = random() * (max_val - min_val) + min_val
        return value

    def _spawn_asteroid(self):
        wlimit, hlimit = choice([
            (0, self.screen.get_height()),
            (self.screen.get_width(), 0),
        ])

        pos = (self._random_value_in_range(0, wlimit),
               self._random_value_in_range(0, hlimit))
        velocity = (self._random_value_in_range(-self.ASTEROID_MAX_VELOCITY,
                                                self.ASTEROID_MAX_VELOCITY),
                    self._random_value_in_range(-self.ASTEROID_MAX_VELOCITY,
                                                self.ASTEROID_MAX_VELOCITY))
        # pos = (400, 400)

        ang_vel = self._random_value_in_range(-self.ASTEROID_MAX_ANGULAR_VELOCITY,
                                              self.ASTEROID_MAX_ANGULAR_VELOCITY)
        asteroid = Asteroid(angular_velocity=ang_vel, image='asteroid',
                            position=pos, velocity=velocity)
        self.all_actors.add(asteroid)

    def update(self):
        dt = self._clock.tick(60)
        keys = pg.key.get_pressed()
        self.delta = dt
        self.all_actors.update(dt, keys)
        self._handle_events()

    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.all_actors.draw(self.screen)
        pg.display.flip()

    def exit(self):
        pg.quit()
