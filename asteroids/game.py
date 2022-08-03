import os
import time

import pygame
import logging
from asteroids.asteroids import Asteroids

logging.basicConfig(level=os.getenv('ASTEROID_LOG_LEVEL', 'ERROR'),
                    format='[%(asctime)s.%(msecs)03d] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')


def main():
    pygame.init()
    game = Asteroids(width=1280, height=768)
    while game.is_running:
        game.update()
        game.render()
    pygame.quit()
    # time.sleep(1)


if __name__ == '__main__':
    main()
