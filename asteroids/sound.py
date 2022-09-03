import logging
import time
from enum import Enum
from typing import NamedTuple

import pygame.mixer

from asteroids.utils import load_sound


log = logging.getLogger(__name__)


class _SoundInfo(NamedTuple):
    pg_sound: pygame.mixer.Sound
    length: float


class SoundManager:
    def __init__(self):
        pygame.mixer.set_num_channels(16)
        self._sounds: dict[str, _SoundInfo] = {}

        self._playing: dict[str, float] = {}
        self._last_update = time.time()

    def play(self, sound: str, loop=False, volume=100, unique=False):
        self._check_sound(sound)
        self._update()
        loops = 0 if not loop else 100
        if unique and sound in self._playing:
            return
        _sound = self._sounds[sound]
        _sound.pg_sound.set_volume(volume / 100)
        _sound.pg_sound.play(loops)
        self._playing[sound] = _sound.length

    def stop(self, sound: str, fadeout=False):
        self._check_sound(sound)
        if fadeout:
            self._sounds[sound].pg_sound.fadeout(500)
        else:
            self._sounds[sound].pg_sound.stop()
        if sound in self._playing:
            del self._playing[sound]

    def _update(self):
        delta = time.time() - self._last_update
        self._last_update = time.time()
        filterd_playing = {}
        for sound in self._playing:
            self._playing[sound] -= delta
            if (remaining := self._playing[sound]) > 0:
                filterd_playing[sound] = remaining
        self._playing = filterd_playing

    def _check_sound(self, sound: str):
        if sound not in self._sounds:
            try:
                pg_sound = load_sound(sound)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Audio file '{sound}' not found") from e
            self._sounds[sound] = _SoundInfo(pg_sound, pg_sound.get_length())
