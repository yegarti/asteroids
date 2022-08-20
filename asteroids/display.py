import pygame


class Display:

    @staticmethod
    def get_rect() -> pygame.rect.Rect:
        return pygame.display.get_surface().get_rect()

    @staticmethod
    def get_size() -> tuple:
        return pygame.display.get_window_size()

    @staticmethod
    def get_center() -> tuple:
        return tuple([a // 2 for a in pygame.display.get_window_size()])
