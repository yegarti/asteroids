from dataclasses import dataclass

from asteroids.display import Display
from asteroids.utils import load_font


@dataclass
class Text:
    font: str

    def render(self, text, size, position):
        font = load_font(self.font, size)
        surface = font.render(text, True, '#ffffff')
        Display.get_screen().blit(surface,
                                  (position.x - surface.get_width() / 2,
                                   position.y - surface.get_height() / 2))
