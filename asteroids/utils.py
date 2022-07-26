from importlib.resources import files
import pygame


def load_image(image_name: str) -> pygame.Surface:
    file = files('asteroids.resources').joinpath(f'{image_name}.png')
    return pygame.image.load(file).convert()


def repeat_surface(size: tuple[int, int], image: pygame.Surface) -> pygame.Surface:
    width, height = size
    surface = pygame.Surface(size)
    for x in range((width // image.get_width()) + 1):
        for y in range((height // image.get_height()) + 1):
            surface.blit(image,
                         (x * image.get_height(),
                          y * image.get_width()))
    return surface
