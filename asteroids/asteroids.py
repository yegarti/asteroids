import enum
import logging
import math
import time
from random import random, choice

import pygame as pg
import pygame.display
from pygame.locals import *

from asteroids.actor import Actor
from asteroids.animation import Animation
from asteroids.asteroid import Asteroid
from asteroids.bullet import Bullet
from asteroids.config import Config
from asteroids.events import AsteroidsEvent
from asteroids.player import Player
from asteroids.utils import load_image, repeat_surface


log = logging.getLogger(__name__)


class Layer(enum.IntEnum):
    PLAYERS = 0
    ASTEROIDS = 1
    BULLETS = 2
    ANIMATIONS = 3


class Asteroids:
    MOVEMENT_SCALAR = 0.25
    PLAYER_SCALE = 0.5
    ASTEROID_OFF_SCREEN_POS_OFFSET = 100
    BACKGROUND_IMAGE = 'purple'
    PLAYER_IMAGE = 'player'
    SPAWN_ASTEROID_FREQUENCY_MS = 1000
    MAX_ASTEROIDS = 5

    def __init__(self, config: Config):
        self.config = config
        pg.display.set_caption(self.config.title)
        log.debug('Setting screen to (%d,%d)', self.config.width, self.config.height)
        self.screen = pg.display.set_mode(self.config.size)
        self.is_running = True
        self._clock = pygame.time.Clock()
        log.debug("Setting background to '%s'", self.BACKGROUND_IMAGE)
        self.background = repeat_surface(self.screen.get_size(),
                                         load_image(self.BACKGROUND_IMAGE))
        self.layers = {
            layer: pg.sprite.Group() for layer in sorted(Layer)
        }
        self.player = Player(position=self._get_center(),
                             scale=self.PLAYER_SCALE, groups=self.layers)
        log.info('Added player %r', self.player)
        self.layers[Layer.PLAYERS].add(self.player)

        # asteroid = Asteroid(angular_velocity=0.5, image='asteroid_big',
        #                     position=(1338, 829), velocity=(-.2, .1), size='big')
        # self.asteroids.add(asteroid)

        self.delta = 0
        log.info("Setting spawn asteroid timer to %d ms", self.SPAWN_ASTEROID_FREQUENCY_MS)
        pg.time.set_timer(self._create_spawn_asteroid_event('big'), self.SPAWN_ASTEROID_FREQUENCY_MS)

    def _get_center(self):
        return (self.screen.get_width() // 2,
                self.screen.get_height() // 2)

    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or \
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                log.debug('Quit event')
                self.is_running = False
            if event.type == AsteroidsEvent.SPAWN_ASTEROID:
                log.debug('Spawn asteroid event')
                self._spawn_new_asteroid(event.size, event.position)
            if event.type == AsteroidsEvent.SHOT_BULLET:
                log.debug('Shot bullet event')
                self._shot()

    def _random_value_in_range(self, min_val: float, max_val: float):
        value = random() * (max_val - min_val) + min_val
        return value

    def _spawn_new_asteroid(self, size, position):
        if len([a for a in self.layers[Layer.ASTEROIDS] if a.size == 'big']) >= self.MAX_ASTEROIDS and size == 'big':
            log.info("Too many big asteroids on screen")
            return
        width, height = self.screen.get_width(), self.screen.get_height()

        x_vel = [-self.config.asteroid_max_velocity, self.config.asteroid_max_velocity]
        y_vel = [-self.config.asteroid_max_velocity, self.config.asteroid_max_velocity]
        if not position:
            spawn_location = choice(['top', 'left', 'right', 'bottom'])
            match spawn_location:
                case 'top':
                    pos = [self._random_value_in_range(0, height), -self.ASTEROID_OFF_SCREEN_POS_OFFSET]
                    y_vel[0] = self.config.asteroid_min_velocity
                case 'left':
                    pos = [-self.ASTEROID_OFF_SCREEN_POS_OFFSET, self._random_value_in_range(0, width)]
                    x_vel[0] = self.config.asteroid_min_velocity
                case 'right':
                    pos = [width + self.ASTEROID_OFF_SCREEN_POS_OFFSET, self._random_value_in_range(0, height)]
                    x_vel[1] = -self.config.asteroid_min_velocity
                case 'bottom':
                    pos = [self._random_value_in_range(0, height), width + self.ASTEROID_OFF_SCREEN_POS_OFFSET]
                    y_vel[1] = -self.config.asteroid_min_velocity
                case _:
                    raise ValueError(f'Unknown spawn location: {spawn_location}')

            log.debug('Spawning asteroid from %s at pos (%d, %d) and velocity range (x=%s, y=%s)',
                      spawn_location, *pos, x_vel, y_vel)
        else:
            pos = position

        velocity = (self._random_value_in_range(*x_vel),
                    self._random_value_in_range(*y_vel))

        ang_vel = self._random_value_in_range(-self.config.asteroid_max_angular_velocity,
                                              self.config.asteroid_max_angular_velocity)
        asteroid = Asteroid(angular_velocity=ang_vel, image=f'asteroid_{size}',
                            size=size,
                            position=pos, velocity=velocity)
        self.layers[Layer.ASTEROIDS].add(asteroid)
        log.info("Spawned %s", asteroid)
        self.layers[Layer.ASTEROIDS].add(asteroid)

    def _create_spawn_asteroid_event(self, size, position=None):
        return pg.event.Event(AsteroidsEvent.SPAWN_ASTEROID, size=size,
                              position=position)

    def _shot(self):
        pos = self.player.position
        angle = self.player.angle
        x = -math.sin(math.radians(angle))
        y = -math.cos(math.radians(angle))
        velocity = pg.math.Vector2(x, y) * self.config.bullet_speed + self.player.velocity
        bullet = Bullet(position=pos,
                        velocity=velocity, angle=angle, scale=.8)

        log.info("Shot bullet %s", bullet)
        self.layers[Layer.BULLETS].add(bullet)

    def update(self):
        dt = self._clock.tick(60)
        keys = pg.key.get_pressed()
        self.delta = dt
        log.debug("Updating actors")
        for group in self.layers.values():
            group.update(dt, keys)
        self._detect_bullet_hits()
        self._check_player_hit()
        log.debug("Handling game events")
        self._handle_events()

    def render(self):
        self.screen.blit(self.background, (0, 0))
        log.debug("Drawing all actors")
        for group in self.layers.values():
            group.draw(self.screen)
        pg.display.flip()

    def _detect_bullet_hits(self):
        bullet: Bullet
        asteroid: Asteroid
        for bullet in self.layers[Layer.BULLETS]:
            for asteroid in self.layers[Layer.ASTEROIDS]:
                if pg.sprite.collide_circle(bullet, asteroid):
                    bullet.hit()
                    self._spawn_bullet_animation(bullet.position)
                    asteroid.hit()
                    if asteroid.is_dead():
                        asteroid.explode()
                    log.debug('Bullet hit detected')

    def _spawn_bullet_animation(self, position):
        animation = Animation(['bullet_hit1', 'bullet_hit2'], position, 30, 0.8)
        self.layers[Layer.ANIMATIONS].add(animation)

    def _check_player_hit(self):
        asteroid: Asteroid
        for asteroid in self.layers[Layer.ASTEROIDS]:
            if pg.sprite.collide_circle(self.player, asteroid):
                log.info("Player got hit by asteroid")
                asteroid.hit()
