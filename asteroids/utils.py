import logging
from functools import cache
from importlib.abc import Traversable
from importlib.resources import files

import pygame


def _get_resource_path(resource, suffix='') -> Traversable:
    suffix = f'.{suffix}' if suffix else ''
    file = files('asteroids.resources{}'.format(suffix)).joinpath(resource)
    logging.debug('Loading %s from %s', resource, file)
    return file


@cache
def load_image(image_name: str) -> pygame.Surface:
    file = f'{image_name}.png'
    return pygame.image.load(_get_resource_path(file, 'sprites')).convert_alpha()


@cache
def load_font(font_name: str, size: int) -> pygame.font.Font:
    file = f'{font_name}.ttf'
    return pygame.font.Font(_get_resource_path(file), size)


@cache
def load_sound(sound_name: str) -> pygame.mixer.Sound:
    file = f'{sound_name}.ogg'
    return pygame.mixer.Sound(str(_get_resource_path(file, 'sounds')))


def repeat_surface(size: tuple[int, int], image: pygame.Surface) -> pygame.Surface:
    width, height = size
    surface = pygame.Surface(size)
    for x in range((width // image.get_width()) + 1):
        for y in range((height // image.get_height()) + 1):
            surface.blit(image,
                         (x * image.get_height(),
                          y * image.get_width()))
    return surface
