import pygame
from asteroids.asteroids import Asteroids


def main():
    pygame.init()
    game = Asteroids(width=800, height=600)
    while game.is_running:
        game.update()
        game.render()


if __name__ == '__main__':
    main()
