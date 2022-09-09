import logging
import math
import re
from random import random, choice
from typing import Sequence, Type

import pygame as pg
import pygame.display
from pygame.math import Vector2

from asteroids.alien import Alien
from asteroids.animation import Animation
from asteroids.asteroid import Asteroid
from asteroids.bullet import Bullet
from asteroids.config import Config, get_config
from asteroids.events.game_events import EventId, GameEvents
from asteroids.events.events_info import ShotBulletInfo, SpawnAsteroidInfo, SpawnAlienInfo, SpawnPowerUpInfo
from asteroids.gui import GUI
from asteroids.layer import Layer
from asteroids.player import Player
from asteroids.power_up import Health, PowerUp
from asteroids.sound import SoundManager
from asteroids.text import Text
from asteroids.utils import load_image, repeat_surface, get_sprites_path

log = logging.getLogger(__name__)


class Asteroids:
    SPAWN_BORDER_OFFSET = 100
    BACKGROUND_IMAGE = 'purple'

    def __init__(self):
        self.config: Config = get_config()
        pg.display.set_caption(self.config.title)
        log.debug('Setting screen to (%d,%d)', self.config.width, self.config.height)
        self.screen = pg.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.is_running = True
        self._clock = pygame.time.Clock()
        self._game_over: bool = False
        log.debug("Setting background to '%s'", self.BACKGROUND_IMAGE)
        self.background = repeat_surface(self.screen.get_size(),
                                         load_image(self.BACKGROUND_IMAGE))
        self.layers: dict[Layer, pg.sprite.Group] = {
            layer: pg.sprite.Group() for layer in sorted(Layer)
        }
        self.gui = GUI(self.screen, max_health=100)
        self.lives = get_config().lives
        self._init_player()
        self.sound_manager = SoundManager
        self.sound_manager.init()
        self._init_asteroid_sprites()
        self.alien = None

        self._text = Text(get_config().gui_font)

        # asteroid = Asteroid(angular_velocity=0, image_name=self.asteroids_sprites['brown']['big'][1],
        #                     color='brown',
        #                     pos=(400, 400), velocity=Vector2(0, 0), size='big')
        # self.layers[Layer.ASTEROIDS].add(asteroid)

        self.delta = 0
        log.info("Setting spawn asteroid timer to %d ms", get_config().asteroid_spawn_frequency_ms)
        pg.time.set_timer(
            GameEvents.spawn_asteroid(SpawnAsteroidInfo(
                size='big',
                color=None,
                position=None,
            )), get_config().asteroid_spawn_frequency_ms)

        pg.time.set_timer(GameEvents.spawn_alien(SpawnAlienInfo(
            probability=get_config().alien_spawn_frequency_per_seconds
        )), 1000)

    def _init_player(self):
        self.lives -= 1

        # make sure event trigger only once
        if self.lives == -1:
            pygame.event.post(GameEvents.game_over())
            return

        self.player = Player(pos=self._get_center(),
                             scale=get_config().player_scale, groups=self.layers)
        log.info('Added player %r', self.player)
        self.layers[Layer.PLAYERS].add(self.player)
        self.gui.health = self.player.health

    def _init_asteroid_sprites(self):
        self.asteroids_sprites: dict[str, dict[str, list[str]]] = {}
        for sprite in get_sprites_path().iterdir():
            match = re.match(r'(meteor(\w+)_(\w+)\d).png', sprite.name)
            if match:
                name, color, size = match.groups()
                size = 'medium' if size == 'med' else size
                self.asteroids_sprites.setdefault(color.lower(), {}).setdefault(size, []).append(name)

    def _get_center(self):
        return (self.screen.get_width() // 2,
                self.screen.get_height() // 2)

    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or \
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                log.debug('Quit event')
                self.is_running = False
            if event.type == EventId.SPAWN_ASTEROID:
                log.debug('Spawn asteroid event')
                self._spawn_new_asteroid(event.info)
            if event.type == EventId.SHOT_BULLET:
                log.debug('Shot bullet event')
                self._shot(event.info)
            if event.type == EventId.PLAYER_DEAD:
                log.debug("Respawning player")
                self._init_player()
            if event.type == EventId.GAME_OVER:
                log.info("Game over!")
                log.info("Score: %d", self.gui.score)
                self._game_over = True
            if event.type == EventId.SPAWN_ALIEN:
                log.debug("Spawn alien event")
                self._spawn_alien(event.info)
            if event.type == pg.KEYDOWN and event.key == pg.K_j:
                self._spawn_alien(SpawnAlienInfo(probability=1.))
            if event.type == EventId.SPAWN_POWERUP:
                self._spawn_powerup(event.info)
            if event.type == pg.KEYDOWN and event.key == pg.K_o:
                pygame.event.post(
                    GameEvents.spawn_powerup(
                        SpawnPowerUpInfo(
                            position=Vector2(random() * 800, random() * 800),
                            duration=0,
                            image=get_config().power_up_health,
                            scale=1.0,
                            power_up='health',
                        )))

    def _random_value_in_range(self, min_val: float, max_val: float):
        value = random() * (max_val - min_val) + min_val
        return value

    def _random_border_location(self, relative_area: float = 0.):
        width, height = self.screen.get_width(), self.screen.get_height()
        spawn_location = choice(['top', 'left', 'right', 'bottom'])
        rand_height = self._random_value_in_range(height * relative_area, height * (1 - relative_area))
        rand_width = self._random_value_in_range(width * relative_area, width * (1 - relative_area))
        match spawn_location:
            case 'top':
                pos = [rand_width, -self.SPAWN_BORDER_OFFSET]
                # yvel[0] = self.config.asteroid_min_velocity
            case 'left':
                pos = [-self.SPAWN_BORDER_OFFSET, rand_height]
                # xvel[0] = self.config.asteroid_min_velocity
            case 'right':
                pos = [width + self.SPAWN_BORDER_OFFSET, rand_height]
                # xvel[1] = -self.config.asteroid_min_velocity
            case 'bottom':
                pos = [rand_width, height + self.SPAWN_BORDER_OFFSET]
                # yvel[1] = -self.config.asteroid_min_velocity
            case _:
                raise ValueError(f'Unknown spawn location: {spawn_location}')
        return pos, spawn_location
        # return pos, xvel, yvel, spawn_location

    def _spawn_new_asteroid(self, info: SpawnAsteroidInfo):
        if len([a for a in self.layers[Layer.ASTEROIDS] if a.size == 'big']) >= get_config().max_asteroids and info.size == 'big':
            log.debug("Too many big asteroids on screen")
            return
        x_vel = [-self.config.asteroid_max_velocity, self.config.asteroid_max_velocity]
        y_vel = [-self.config.asteroid_max_velocity, self.config.asteroid_max_velocity]
        if not info.position:
            pos, spawn_location = self._random_border_location()
            match spawn_location:
                case 'top':
                    y_vel[0] = self.config.asteroid_min_velocity
                case 'left':
                    x_vel[0] = self.config.asteroid_min_velocity
                case 'right':
                    x_vel[1] = -self.config.asteroid_min_velocity
                case 'bottom':
                    y_vel[1] = -self.config.asteroid_min_velocity
            log.debug('Spawning asteroid from %s at pos (%d, %d) and velocity range (x=%s, y=%s)',
                      spawn_location, x_vel, y_vel, *pos)
        else:
            pos = info.position

        velocity = Vector2(self._random_value_in_range(*x_vel),
                           self._random_value_in_range(*y_vel))

        ang_vel = self._random_value_in_range(-self.config.asteroid_max_angular_velocity,
                                              self.config.asteroid_max_angular_velocity)

        color = info.color
        if not info.color:
            color = choice(list(self.asteroids_sprites.keys()))

        asteroid = Asteroid(angular_velocity=ang_vel,
                            image_name=choice(self.asteroids_sprites[color][info.size]),
                            size=info.size, color=color,
                            pos=pos, velocity=velocity)
        self.layers[Layer.ASTEROIDS].add(asteroid)
        log.debug("Spawned %s", asteroid)
        self.layers[Layer.ASTEROIDS].add(asteroid)

    def _shot(self, info: ShotBulletInfo):

        x = -math.sin(math.radians(info.angle))
        y = -math.cos(math.radians(info.angle))
        velocity = pg.math.Vector2(x, y) * info.velocity
        bullet = Bullet(image_name=info.image, pos=info.position,
                        velocity=velocity, angle=info.angle,
                        scale=info.scale, ttl=info.duration,
                        damage=info.damage,
                        groups=self.layers,
                        hit_animation_images=info.hit_images)

        log.debug("Shot bullet %s", bullet)
        self.layers[info.layer].add(bullet)
        self.sound_manager.play(info.sound)

    def update(self):
        dt = self._clock.tick(60)
        keys = pg.key.get_pressed()
        self.delta = dt
        log.debug("Updating actors")
        for group in self.layers.values():
            group.update(dt, keys)
        self.check_actions()
        log.debug("Handling game events")
        self._handle_events()
        self.gui.health = self.player.health
        self.gui.lives = self.lives
        if self.player.thrust != 0:
            self.sound_manager.play(get_config().thrust_sound, volume=40, unique=True)
        else:
            self.sound_manager.stop(get_config().thrust_sound, fadeout=True)
        if self.alien and self.alien.alive():
            self.sound_manager.play(get_config().alien_sound, volume=60, unique=True)
        else:
            self.sound_manager.stop(get_config().alien_sound)
        if self.player.is_dead() and self.player.active:
            self.player.explode()
            self.sound_manager.play(get_config().player_die_sound)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        log.debug("Drawing all actors")
        for group in self.layers.values():
            group.draw(self.screen)
        self.gui.render()
        if self._game_over:
            self._text.render('Game Over', 40, Vector2(self._get_center()) + Vector2(0, -100))
            self._text.render(f'{self.gui.score}', 32, Vector2(self._get_center()) + Vector2(0, -50))
        pg.display.flip()

    def check_actions(self):
        self.check_player_bullets_hit()
        self.check_asteroid_hit_player()
        self.check_asteroid_hit_alien()
        self.check_powerup_collected()

    def check_player_bullets_hit(self):
        bullet: Bullet
        asteroid: Asteroid
        for bullet in self.layers[Layer.BULLETS]:
            for asteroid in self.layers[Layer.ASTEROIDS]:
                if pg.sprite.collide_circle(bullet, asteroid):
                    bullet.on_hit()
                    asteroid.on_bullet_hit(bullet)
                    if not asteroid.alive():
                        self.gui.score += asteroid.score
            if self.alien and self.alien.alive() and pg.sprite.collide_circle(bullet, self.alien):
                bullet.on_hit()
                self.alien.on_bullet_hit(bullet)
                if not self.alien.active and self.alien.is_dead():
                    self.gui.score += 15

    def check_asteroid_hit_player(self):
        asteroid: Asteroid
        for asteroid in self.layers[Layer.ASTEROIDS]:
            if pg.sprite.collide_circle(self.player, asteroid):
                self.player.on_asteroid_hit()

    def _spawn_alien(self, info: SpawnAlienInfo):
        if random() > info.probability or self.alien in self.layers[Layer.ENEMIES]:
            return
        velocity = Vector2(get_config().alien_velocity, get_config().alien_velocity)
        pos, spawn_loc = self._random_border_location(relative_area=.8)
        velocity = velocity.elementwise() * {
            'top': Vector2(0, 1),
            'bottom': Vector2(0, -1),
            'left': Vector2(1, 0),
            'right': Vector2(-1, 0),
        }[spawn_loc]
        self.alien = Alien(velocity=velocity, scale=.7, pos=pos, groups=self.layers)
        log.info(f"Spawning alien: {self.alien}")
        self.layers[Layer.ENEMIES].add(self.alien)

    def check_asteroid_hit_alien(self):
        bullet: Bullet
        for bullet in self.layers[Layer.ENEMY_BULLETS]:
            if pg.sprite.collide_circle(bullet, self.player):
                bullet.on_hit()
                self.player.on_bullet_hit(bullet)

    def _spawn_powerup(self, info: SpawnPowerUpInfo):
        power = PowerUp.new(info.power_up)
        self.layers[Layer.POWER_UP].add(
            power(image_name=info.image,
                  scale=info.scale,
                  pos=info.position,
                  duration=info.duration,
                  groups=self.layers,
                  )
        )

    def check_powerup_collected(self):
        for powerup in self.layers[Layer.POWER_UP]:
            powerup: PowerUp
            if self.player.alive() and pg.sprite.collide_circle(powerup, self.player):
                powerup.activate()
                powerup.kill()
