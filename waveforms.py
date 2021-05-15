# MODULES

import math
import cfg
from typing import Callable
import random

# import automation

# WAVEFORMS


class Waveform:
    def __init__(self, glide: float = 0) -> None:
        self.glide = glide
        self.phase = 0

    def wave(self):
        return 0

    def next_phase(self, freq):
        self.phase += (freq / cfg.sps) * 360
        if self.phase >= 360:
            self.phase -= 360

    def out(self, freq: float = 440, amp: float = 1) -> float:
        self.next_phase(freq)
        return amp * self.wave()


class Sine(Waveform):
    def wave(self) -> float:
        return math.sin(self.phase * 2 * math.pi / 360)


class Square(Waveform):
    def __init__(self, glide: float = 0, pulse_width: float = 0.5) -> None:
        self.pulse_width = pulse_width
        super().__init__(glide)

    def wave(self) -> float:
        if self.phase >= 0 and self.phase < 360 * self.pulse_width:
            return 1
        else:
            return -1


class Triangle(Waveform):
    def wave(self) -> float:
        if self.phase >= 0 and self.phase < 90:
            return self.phase / 90
        elif self.phase >= 90 and self.phase < 270:
            return 1 - (self.phase - 90) / 90
        else:
            return -1 + (self.phase - 270) / 90

class Sawtooth(Waveform):
    def wave(self) -> float:
        return 2 * self.phase / 360 - 1

class Random(Waveform):
    def wave(self) -> float:
        return (random.random() * 2) - 1