import logging
import math
import re
from random import random, choice, randrange
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
from asteroids.spawner import Spawner
from asteroids.text import Text
from asteroids.utils import load_image, repeat_surface, get_sprites_path

log = logging.getLogger(__name__)


class Asteroids:

    def __init__(self):
        self.config: Config = get_config()
        pg.display.set_caption(self.config.title)
        log.debug('Setting screen to (%d,%d)', self.config.width, self.config.height)
        if get_config().full_screen:
            self.screen = pg.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode((get_config().width,
                                               get_config().height))

        self.is_running = True
        self._clock = pygame.time.Clock()
        self._game_over: bool = False
        log.debug("Setting background to '%s'", get_config().background_image)
        self.background = repeat_surface(self.screen.get_size(),
                                         load_image(get_config().background_image))
        self.layers: dict[Layer, pg.sprite.Group] = {
            layer: pg.sprite.Group() for layer in sorted(Layer)
        }
        self.gui = GUI(self.screen, max_health=100)
        self.lives = get_config().lives
        self._init_player()
        self.sound_manager = SoundManager
        self.sound_manager.init()
        self.alien = None
        self._pause = False
        self.spawner = Spawner(self.layers)

        self._text = Text(get_config().gui_font)

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

        for powerup in ('health', 'laser'):
            pg.time.set_timer(GameEvents.spawn_powerup(
                SpawnPowerUpInfo(
                    power_ups=tuple(get_config().power_up.keys()),
                )), get_config().power_up_freq_s * 1000)

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

    def _get_center(self):
        return (self.screen.get_width() // 2,
                self.screen.get_height() // 2)

    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or \
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                log.debug('Quit event')
                self.is_running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                self._pause = not self._pause
                if self._pause:
                    SoundManager.mute()
                else:
                    SoundManager.unmute()

            if self._pause:
                continue

            if event.type == EventId.SPAWN_ASTEROID:
                log.debug('Spawn asteroid event')
                self.spawner.spawn_asteroid(event.info)
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
                self.spawner.spawn_alien(event.info)
            if event.type == pg.KEYDOWN and event.key == pg.K_j:
                self.spawner.spawn_alien(SpawnAlienInfo(probability=1.))
            if event.type == EventId.SPAWN_POWERUP:
                self.spawner.spawn_powerup(event.info)
            if event.type == pg.KEYDOWN and event.key == pg.K_o:
                pygame.event.post(
                    GameEvents.spawn_powerup(
                        SpawnPowerUpInfo(
                            power_ups=tuple(get_config().power_up.keys())
                        )))

    def _shot(self, info: ShotBulletInfo):
        bullet_config = info.bullet_config
        x = -math.sin(math.radians(info.angle))
        y = -math.cos(math.radians(info.angle))
        velocity = pg.math.Vector2(x, y) * bullet_config.velocity
        bullet = Bullet(image_name=bullet_config.image, pos=info.position,
                        velocity=velocity, angle=info.angle,
                        scale=bullet_config.scale, ttl=bullet_config.duration,
                        damage=bullet_config.damage,
                        groups=self.layers,
                        hit_animation_images=bullet_config.hit_images)

        log.debug("Shot bullet %s", bullet)
        self.layers[info.layer].add(bullet)
        self.sound_manager.play(bullet_config.sound)

    def update(self):
        dt = self._clock.tick(60)
        keys = pg.key.get_pressed()
        self.delta = dt
        log.debug("Handling game events")
        self._handle_events()

        if self._pause:
            return

        log.debug("Updating actors")
        for group in self.layers.values():
            group.update(dt, keys)
        self.check_actions()
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
        try:
            self.alien = self.layers[Layer.ENEMIES].sprites()[0]
        except IndexError:
            self.alien = None

    def render(self):
        self.screen.blit(self.background, (0, 0))
        log.debug("Drawing all actors")
        for group in self.layers.values():
            group.draw(self.screen)
        self.gui.render()
        if self._game_over:
            self._text.render('Game Over', 40, Vector2(self._get_center()) + Vector2(0, -100))
            self._text.render(f'{self.gui.score}', 32, Vector2(self._get_center()) + Vector2(0, -50))
        if self._pause:
            self._text.render("Game paused", 40, Vector2(self._get_center()))
        pg.display.flip()

    def check_actions(self):
        self.check_player_bullets_hit()
        self.check_asteroid_hit_player()
        self.check_asteroid_hit_alien()
        self.check_powerups()

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

    def check_asteroid_hit_alien(self):
        bullet: Bullet
        for bullet in self.layers[Layer.ENEMY_BULLETS]:
            if pg.sprite.collide_circle(bullet, self.player):
                bullet.on_hit()
                self.player.on_bullet_hit(bullet)

    def check_powerups(self):
        for powerup in self.layers[Layer.POWER_UP]:
            powerup: PowerUp
            powerup.duration -= self.delta
            if self.player.alive() and pg.sprite.collide_circle(powerup, self.player):
                powerup.activate()
                powerup.kill()
            if powerup.duration < 0:
                powerup.kill()
