import logging
import math

import pygame as pg
from pygame.math import Vector2
import pygame.transform

from asteroids.utils import load_image

log = logging.getLogger(__name__)


class Actor(pg.sprite.Sprite):
    ACCELERATION = 0.01
    VELOCITY_MULT = .5
    ANGULAR_SPEED = 1
    MAX_VELOCITY = 1.
    THRUST_MULT = .01
    HITBOX_RADIUS_RATIO = 0.9
    HIT_DURATION = .1
    HIT_MARK_DURATION_MS = 100

    def __init__(self, image, scale=1.,
                 position=(0, 0), velocity=(0, 0), angle=0, health=1.):
        super().__init__()
        self._screen_rect: pg.Rect = pg.display.get_surface().get_rect()
        self._original_image = load_image(image)
        self._scale(scale)
        self.image: pg.Surface = self._original_image.copy()
        self.image.get_rect()
        self.rect = self.image.get_rect()
        self.velocity = Vector2(velocity)
        self.position = Vector2(position)
        self.angle = angle
        self.thrust = 0
        self.health = health
        self._delta = 0
        self.radius = self.image.get_width() / 2 * self.HITBOX_RADIUS_RATIO
        self._hit_mark_cooldown = 0
        self._update_physics()

    def _scale(self, factor):
        self._original_image = pg.transform.scale(
            self._original_image,
            (factor * self._original_image.get_width(),
             factor * self._original_image.get_height()))

    def update(self, dt, keys) -> None:
        self._delta = dt
        self._hit_mark_cooldown -= dt
        self._update_physics()
        if self._hit_mark_cooldown > 0:
            hit_mark_image = pg.Surface(self.image.get_size()).convert_alpha()
            hit_mark_image.fill((255, 0, 0))
            self.image.blit(hit_mark_image, (0, 0), special_flags=pg.BLEND_RGB_MULT)

    def _update_physics(self):
        self._update_velocity()
        log.debug('Thrust on: %r', self.thrust > 0)
        self.thrust = 0
        self.position += self.velocity * self._delta * self.VELOCITY_MULT
        log.debug('Position: (%f, %f)', *self.position)
        rotated_image, rotated_rect = self._rotate(self.angle)
        self.image = rotated_image
        self.rect = rotated_rect

    def _update_velocity(self):
        dx = -math.sin(math.radians(self.angle)) * self.thrust
        dy = -math.cos(math.radians(self.angle)) * self.thrust
        self.velocity += (dx, dy)
        self.velocity.x = max(min(self.velocity.x, self.MAX_VELOCITY), -self.MAX_VELOCITY)
        self.velocity.y = max(min(self.velocity.y, self.MAX_VELOCITY), -self.MAX_VELOCITY)
        log.debug('Velocity: (%f, %f)', *self.velocity)

    def _rotate(self, angle):
        # using // reduce the vibrations
        center = self._original_image.get_width() // 2, self._original_image.get_height() // 2
        image_rect = self._original_image.get_rect(topleft=(self.position.x - center[0], self.position.y - center[1]))

        offset_center_to_pivot = self.position - image_rect.center

        # rotated offset from pivot to center
        rotated_offset = offset_center_to_pivot.rotate(-angle)

        # rotated image center
        rotated_image_center = (self.position.x - rotated_offset.x,
                                self.position.y - rotated_offset.y)

        # using rotozoom to same smooth edges
        rotated_image = pygame.transform.rotozoom(self._original_image, angle, 1.0)
        rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

        # self.image = rotated_image
        # self.rect = rotated_image_rect
        return rotated_image, rotated_image_rect

    def accelerate(self):
        self.thrust = self.THRUST_MULT

    def decelerate(self):
        self.thrust = -self.THRUST_MULT

    def rotate_ccw(self):
        self.angle += self.ANGULAR_SPEED
        log.debug("Rotated CCW to %f", self.angle)
        if self.angle >= 360:
            self.angle = 0

    def rotate_cw(self):
        self.angle -= self.ANGULAR_SPEED
        log.debug("Rotated CW to %f", self.angle)
        if self.angle <= 0:
            self.angle = 359

    def inbounds(self):
        return self._screen_rect.colliderect(self.rect)

    def hit(self):
        self.health -= 1
        self._hit_mark_cooldown = self.HIT_MARK_DURATION_MS

    def is_dead(self):
        return self.health <= 0

    def __repr__(self):
        return f'<{self.__class__.__name__} -' \
               f' pos={self.position!r}' \
               f' velocity={self.velocity!r}' \
               f' ang_vel={self.ANGULAR_SPEED}' \
               f'>'
