import logging
import math
from dataclasses import dataclass, field

import pygame as pg
from pygame.math import Vector2
import pygame.transform

from asteroids.display import Display
from asteroids.layer import Layer
from asteroids.static_actor import StaticActor
from asteroids.utils import load_image

log = logging.getLogger(__name__)


@dataclass(eq=False)
class Actor(StaticActor):
    ACCELERATION = 0.01
    VELOCITY_MULT = .5
    ANGULAR_SPEED = 1
    MAX_VELOCITY = 1.
    THRUST_MULT = .01
    HITBOX_RADIUS_RATIO = 0.9
    HIT_DURATION = .1
    HIT_MARK_DURATION_MS = 100

    health: int = 1
    angle: float = 0
    velocity: Vector2 = field(default_factory=Vector2)
    radius: float = field(init=False)
    thrust: float = field(init=False, default=0)
    groups: dict[Layer, pg.sprite.Group] = None
    active: bool = True

    _delta: float = field(init=False, default=0)
    _hit_mark_cooldown: float = field(init=False, default=0)

    def __post_init__(self, pos: Vector2):
        super().__post_init__(pos)
        self.radius = self.image.get_width() / 2 * self.HITBOX_RADIUS_RATIO
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
        if not self.inbounds() and self.spawned:
            self.teleport()
            pass

    def _update_physics(self):
        self._update_velocity()
        log.debug('Thrust on: %r', self.thrust > 0)
        self.thrust = 0
        self.rotate(self.angle)
        pos_delta = self.velocity * self._delta * self.VELOCITY_MULT
        self.position += pos_delta
        log.debug(f'{self.angle=}, {self.velocity=}, {self.position=}, {pos_delta=}')
        log.debug('Position: (%f, %f)', *self.position)
        # rotated_image, rotated_rect = self._rotate(self.angle)
        # self.image = rotated_image
        # self.rect = rotated_rect

    def _update_velocity(self):
        dx = -math.sin(math.radians(self.angle)) * self.thrust
        dy = -math.cos(math.radians(self.angle)) * self.thrust
        self.velocity += (dx, dy)
        self.velocity.x = max(min(self.velocity.x, self.MAX_VELOCITY), -self.MAX_VELOCITY)
        self.velocity.y = max(min(self.velocity.y, self.MAX_VELOCITY), -self.MAX_VELOCITY)
        log.debug('Velocity: (%f, %f)', *self.velocity)

    def teleport(self):
        center = self.rect.height // 2, self.rect.width // 2
        width, height = Display.get_size()
        new_x = width - self.position.x + center[1]
        new_y = height - self.position.y + center[0]
        if self.position.y > height:
            new_y = -center[0] + 2
        elif self.position.y < 0:
            new_y = height + center[0] - 2
        if self.position.x > width:
            new_x = -center[1] + 2
        elif self.position.x < 0:
            new_x = width + center[1] - 2
        # new_y = min(max(height - self.position.y, 0), height) + center[1]

        new_position = Vector2(new_x, new_y)
        diff = new_position - self.position
        log.debug("Teleporting out of bounds actor %s from %s to %s",
                  id(self),
                  self.position, new_position)
        self.rect.move_ip(diff.x, diff.y)
        self.position = new_position

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

    def hit(self):
        self._hit_mark_cooldown = self.HIT_MARK_DURATION_MS

    def is_dead(self):
        return self.health <= 0
