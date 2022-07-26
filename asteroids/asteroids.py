import pygame as pg
import pygame.display
from pygame.locals import *

from asteroids.actor import Actor
from asteroids.utils import load_image, repeat_surface


class Asteroids:
    MOVEMENT_SCALAR = 0.25
    ANGLE = 0.1

    def __init__(self, width, height, title='Asteroids'):
        pg.display.set_caption(title)
        self.screen = pg.display.set_mode((width, height))
        self.is_running = True
        self._clock = pygame.time.Clock()
        self.background = repeat_surface(self.screen.get_size(),
                                         load_image('purple'))

        img = pg.Surface((20, 40))
        img.fill((255, 0, 0))
        self._player: Actor = Actor(image=img,
                                    position=self._get_center(),
                                    velocity=(0, 0))
        self.delta = 0

    def _get_center(self):
        return (self.screen.get_width() // 2,
                self.screen.get_height() // 2)

    def _handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or \
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.is_running = False

    def _update_player(self):
        keys = pg.key.get_pressed()
        # if keys[K_d]:
        #     self._player.rotate(-self.ANGLE * self.delta)
        # if keys[K_a]:
        #     self._player.rotate(self.ANGLE * self.delta)
        # if keys[K_s]:
        #     self._player.move(0, self.MOVEMENT_SCALAR * self.delta)
        # if keys[K_w]:
        #     self._player.move(0, -self.MOVEMENT_SCALAR * self.delta)
        pass

    def update(self):
        dt = self._clock.tick(60)
        self.delta = dt
        self._handle_events()
        self._update_player()
        # self.screen.blit(pg.Surface(rect.size), (0, 0))

    def render(self):
        self.screen.blit(self.background, (0, 0))
        # self.screen.fill((0, 0, 0))
        image, rect = self._player.render()
        # self.screen.blit(self._player.image, self._player.rect)
        self.screen.blit(image, rect)
        pg.display.flip()
