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
    _sounds: dict[str, _SoundInfo] = {}
    _playing: dict[str, float] = {}
    _last_update = time.time()

    @staticmethod
    def init():
        pygame.mixer.set_num_channels(16)

    @staticmethod
    def play(sound: str, loop=False, volume=100, unique=False):
        SoundManager._check_sound(sound)
        SoundManager._update()
        loops = 0 if not loop else 100
        if unique and sound in SoundManager._playing:
            return
        _sound = SoundManager._sounds[sound]
        _sound.pg_sound.set_volume(volume / 100)
        _sound.pg_sound.play(loops)
        SoundManager._playing[sound] = _sound.length

    @staticmethod
    def stop(sound: str, fadeout=False):
        SoundManager._check_sound(sound)
        if fadeout:
            SoundManager._sounds[sound].pg_sound.fadeout(500)
        else:
            SoundManager._sounds[sound].pg_sound.stop()
        if sound in SoundManager._playing:
            del SoundManager._playing[sound]

    @staticmethod
    def _update():
        delta = time.time() - SoundManager._last_update
        SoundManager._last_update = time.time()
        filterd_playing = {}
        for sound in SoundManager._playing:
            SoundManager._playing[sound] -= delta
            if (remaining := SoundManager._playing[sound]) > 0:
                filterd_playing[sound] = remaining
        SoundManager._playing = filterd_playing

    @staticmethod
    def _check_sound(sound: str):
        if sound not in SoundManager._sounds:
            try:
                pg_sound = load_sound(sound)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Audio file '{sound}' not found") from e
            SoundManager._sounds[sound] = _SoundInfo(pg_sound, pg_sound.get_length())
