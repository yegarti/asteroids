import pygame
import logging
from asteroids.asteroids import Asteroids

logging.basicConfig(level=logging.INFO)


def main():
    pygame.init()
    game = Asteroids(width=1280, height=768)
    while game.is_running:
        game.update()
        game.render()
    game.exit()


if __name__ == '__main__':
    main()
