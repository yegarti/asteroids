from dataclasses import dataclass, field, InitVar

import pygame.font
from pygame.math import Vector2

from asteroids.config import get_config
from asteroids.display import Display
from asteroids.utils import load_font, load_image


@dataclass(eq=False)
class GUI:
    screen: pygame.surface.Surface
    health: int
    lives: int
    score: int = 0
    _font: pygame.font.Font = field(init=False)
    _start_pos: Vector2 = field(init=False)
    _curr_pos: Vector2 = field(init=False)
    _max_health: int = field(init=False)

    HEIGHT_OFFSET = 40
    WIDTH_OFFSET = 10
    HEALTH_BAR_WIDTH = 120
    HEALTH_BAR_HEIGHT = 20

    def __post_init__(self):
        self._font = load_font(get_config().gui_font, 32)
        self._small_font = load_font(get_config().gui_font, 16)
        sprite = load_image("player")
        self._sprite = pygame.transform.scale(sprite,
                                              (0.3 * sprite.get_width(),
                                               0.3 * sprite.get_height()))
        w, h = Display.get_size()
        self._start_pos = Vector2(self.WIDTH_OFFSET, h - self.HEIGHT_OFFSET)
        self._curr_pos = Vector2(0, 0)
        self._max_health = self.health

    def render(self):
        self._curr_pos = self._start_pos.copy()
        self._curr_pos += Vector2(self.WIDTH_OFFSET, 0)
        self._render_score()
        self._curr_pos += Vector2(25, 0)
        self._render_lives()
        self._curr_pos += Vector2(50, 0)
        self._render_health()

    def _render_score(self):
        text = self._font.render(f'{self.score}', True, '#ffffff')

        self.screen.blit(text, self._curr_pos)

    def _render_lives(self):
        for _ in range(self.lives):
            self._curr_pos += Vector2(35, 0)
            self.screen.blit(self._sprite, self._curr_pos)

    def _render_health(self):
        health = max(self.health, 0)
        health_perc = health / self._max_health
        bg = pygame.surface.Surface((self.HEALTH_BAR_WIDTH, self.HEALTH_BAR_HEIGHT))
        fg = pygame.surface.Surface((self.HEALTH_BAR_WIDTH * health_perc, self.HEALTH_BAR_HEIGHT))
        bg.fill('#000000')
        fg.fill('#bf0000')
        self.screen.blit(bg, self._curr_pos)
        self.screen.blit(fg, self._curr_pos)
        text = self._small_font.render(f'{int(health_perc * 100)}', True, '#ffffff')
        self.screen.blit(text, self._curr_pos)
