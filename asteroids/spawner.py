import logging
import re

import pygame
import random

from pygame.math import Vector2

from asteroids.alien import Alien
from asteroids.asteroid import Asteroid
from asteroids.config import get_config
from asteroids.display import Display
from asteroids.events.events_info import SpawnAsteroidInfo, SpawnAlienInfo, SpawnPowerUpInfo
from asteroids.layer import Layer
from asteroids.power_up import PowerUp
from asteroids.utils import get_sprites_path

log = logging.getLogger(__name__)


class Spawner:
    def __init__(self, groups: dict[Layer, pygame.sprite.Group]):
        self.groups = groups
        self._init_asteroid_sprites()

    def _init_asteroid_sprites(self):
        self.asteroids_sprites: dict[str, dict[str, list[str]]] = {}
        for sprite in get_sprites_path().iterdir():
            match = re.match(r'(meteor(\w+)_(\w+)\d).png', sprite.name)
            if match:
                name, color, size = match.groups()
                size = 'medium' if size == 'med' else size
                self.asteroids_sprites.setdefault(color.lower(), {}).setdefault(size, []).append(name)

    def spawn_asteroid(self, info: SpawnAsteroidInfo):
        if len([a for a in self.groups[Layer.ASTEROIDS] if a.size == 'big']) >= get_config().max_asteroids and info.size == 'big':
            log.debug("Too many big asteroids on screen")
            return
        x_vel = [-get_config().asteroid_max_velocity, get_config().asteroid_max_velocity]
        y_vel = [-get_config().asteroid_max_velocity, get_config().asteroid_max_velocity]
        if not info.position:
            pos, spawn_location = self._random_border_location()
            match spawn_location:
                case 'top':
                    y_vel[0] = get_config().asteroid_min_velocity
                case 'left':
                    x_vel[0] = get_config().asteroid_min_velocity
                case 'right':
                    x_vel[1] = -get_config().asteroid_min_velocity
                case 'bottom':
                    y_vel[1] = -get_config().asteroid_min_velocity
            log.debug('Spawning asteroid from %s at pos (%d, %d) and velocity range (x=%s, y=%s)',
                      spawn_location, x_vel, y_vel, *pos)
        else:
            pos = info.position

        velocity = Vector2(self._random_value_in_range(*x_vel),
                           self._random_value_in_range(*y_vel))

        ang_vel = self._random_value_in_range(-get_config().asteroid_max_angular_velocity,
                                              get_config().asteroid_max_angular_velocity)

        color = info.color
        if not info.color:
            color = random.choice(list(self.asteroids_sprites.keys()))

        asteroid = Asteroid(angular_velocity=ang_vel,
                            image_name=random.choice(self.asteroids_sprites[color][info.size]),
                            size=info.size, color=color,
                            pos=pos, velocity=velocity)
        log.debug("Spawned %s", asteroid)
        self.groups[Layer.ASTEROIDS].add(asteroid)

    def spawn_alien(self, info: SpawnAlienInfo):
        alien = self.groups[Layer.ENEMIES].sprites()
        if random.random() > info.probability or len(alien):
            return
        velocity = Vector2(get_config().alien_velocity, get_config().alien_velocity)
        pos, spawn_loc = self._random_border_location(relative_area=.8)
        velocity = velocity.elementwise() * {
            'top': Vector2(0, 1),
            'bottom': Vector2(0, -1),
            'left': Vector2(1, 0),
            'right': Vector2(-1, 0),
        }[spawn_loc]
        alien = Alien(velocity=velocity, scale=.7, pos=pos, groups=self.groups)
        log.info(f"Spawning alien: {alien}")
        self.groups[Layer.ENEMIES].add(alien)

    def spawn_powerup(self, info: SpawnPowerUpInfo):
        for power_name in info.power_ups:
            power = PowerUp.new(power_name)
            power_config = get_config().power_up[power_name]
            if random.random() > power_config.frequency:
                continue

            spawn_area = get_config().power_up_spawn_area
            width, height = Display.get_size()
            width_spawn_area = int(width * spawn_area)
            height_spawn_area = int(height * spawn_area)
            pos = Vector2(
                random.randrange(width_spawn_area,
                                 width - width_spawn_area),
                random.randrange(height_spawn_area,
                                 height - height_spawn_area))

            duration = random.randrange(*power_config.duration_s) * 1000

            power_inst = power(image_name=power_config.image,
                               pos=pos,
                               duration=duration,
                               groups=self.groups,
                               )
            if power_inst.can_spawn():
                self.groups[Layer.POWER_UP].add(power_inst)

    def _random_value_in_range(self, min_val: float, max_val: float):
        value = random.random() * (max_val - min_val) + min_val
        return value

    def _random_border_location(self, relative_area: float = 0.):
        width, height = Display.get_size()
        spawn_location = random.choice(['top', 'left', 'right', 'bottom'])
        rand_height = self._random_value_in_range(height * relative_area, height * (1 - relative_area))
        rand_width = self._random_value_in_range(width * relative_area, width * (1 - relative_area))
        match spawn_location:
            case 'top':
                pos = [rand_width, -get_config().out_of_screen_offset_spawn]
            case 'left':
                pos = [-get_config().out_of_screen_offset_spawn, rand_height]
            case 'right':
                pos = [width + get_config().out_of_screen_offset_spawn, rand_height]
            case 'bottom':
                pos = [rand_width, height + get_config().out_of_screen_offset_spawn]
            case _:
                raise ValueError(f'Unknown spawn location: {spawn_location}')
        return pos, spawn_location