import time
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

import pygame.mixer

from asteroids.utils import load_sound


class Sound(Enum):
    BULLET_FIRE1 = 'sfx_laser1'
    BULLET_FIRE2 = 'sfx_laser2'
    PLAYER_DIE = 'sfx_lose'
    IMPACT = 'impactMetal_000'
    THRUST = 'thrusterFire_000'
    EXPLOSION = 'explosionCrunch_000'
    HIT = 'lowFrequency_explosion_000'


class _SoundInfo(NamedTuple):
    pg_sound: pygame.mixer.Sound
    length: float


class SoundManager:
    def __init__(self):
        pygame.mixer.set_num_channels(16)
        self._sounds: dict[Sound, _SoundInfo] = {}
        for sound in Sound:
            s = load_sound(sound.value)
            self._sounds[sound] = _SoundInfo(s, s.get_length())

        self._playing: dict[Sound, float] = {}
        self._last_update = time.time()

    def play(self, sound: Sound, loop=False, volume=100, unique=False):
        self._update()
        loops = 0 if not loop else 100
        if unique and sound in self._playing:
            return
        _sound = self._sounds[sound]
        _sound.pg_sound.play(loops)
        self._playing[sound] = _sound.length
        _sound.pg_sound.set_volume(volume / 100)

    def stop(self, sound: Sound, fadeout=False):
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


