import os
from pathlib import Path

import pygame
import logging
from asteroids.asteroids import Asteroids
from asteroids.config import Config

logging.basicConfig(level=os.getenv('ASTEROID_LOG_LEVEL', 'ERROR'),
                    format='[%(asctime)s.%(msecs)03d] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')


def main():
    pygame.init()
    game = Asteroids()
    while game.is_running:
        game.update()
        game.render()
    pygame.quit()


if __name__ == '__main__':
    main()
