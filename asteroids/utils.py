import logging
from functools import cache
from importlib.resources import files
import pygame


@cache
def load_image(image_name: str) -> pygame.Surface:
    file = files('asteroids.resources').joinpath(f'{image_name}.png')
    logging.debug('Loading %s from %s', image_name, file)
    return pygame.image.load(file).convert_alpha()


@cache
def load_font(font_name: str, size: int) -> pygame.font.Font:
    file = files('asteroids.resources').joinpath(f'{font_name}.ttf')
    logging.debug('Loading %s from %s', font_name, file)
    return pygame.font.Font(file, size)


def repeat_surface(size: tuple[int, int], image: pygame.Surface) -> pygame.Surface:
    width, height = size
    surface = pygame.Surface(size)
    for x in range((width // image.get_width()) + 1):
        for y in range((height // image.get_height()) + 1):
            surface.blit(image,
                         (x * image.get_height(),
                          y * image.get_width()))
    return surface
