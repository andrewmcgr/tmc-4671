# TMC4671 biquad filter design utilities
#
# Copyright (C) 2024       Andrew McGregor <andrewmcgr@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import math
from typing import NamedTuple


class BiquadFilter(NamedTuple):
    type: str
    freq: float
    slope: float


######################################################################
# Biquad filter utilities
######################################################################

BIQUAD_FILTER_TYPES = ['lpf', 'notch', 'apf']
BIQUAD_FILTER_TARGETS = {
        'flux': 'CONFIG_BIQUAD_F_ENABLE',
        'torque': 'CONFIG_BIQUAD_T_ENABLE',
        'velocity': 'CONFIG_BIQUAD_V_ENABLE',
        'position': 'CONFIG_BIQUAD_X_ENABLE',
}

# Filter design formula from 4671 datasheet
def biquad_lpf_tmc(fs: float, f: float, D: float) -> tuple[float, float, float, float, float, float]:
    """Design a TMC-specific biquad low-pass filter."""
    w0 = 2.0 * math.pi * f / fs
    b2 = b1 = 0.0
    b0 = 1.0
    a2 = 1.0 / (w0**2)
    a1 = 2.0 * D / w0
    a0 = 1.0
    return b0, b1, b2, a0, a1, a2

# Filter design formulae from https://www.w3.org/TR/audio-eq-cookbook/

# Design a biquad low pass filter in canonical form
def biquad_lpf(fs: float, f: float, Q: float) -> tuple[float, float, float, float, float, float]:
    """Design a biquad low pass filter in canonical form."""
    w0 = 2.0 * math.pi * f / fs
    cw0 = math.cos(w0)
    sw0 = math.sin(w0)
    alpha = 0.5 * sw0 / Q
    b1 = 1.0 - cw0
    b0 = b2 = b1 / 2.0
    a0 = 1 + alpha
    a1 = - 2.0 * cw0
    a2 = 1 - alpha
    return b0, b1, b2, a0, a1, a2

# Design a biquad notch filter in canonical form
def biquad_notch(fs: float, f: float, Q: float) -> tuple[float, float, float, float, float, float]:
    """Design a biquad notch filter in canonical form."""
    w0 = 2.0 * math.pi * f / fs
    cw0 = math.cos(w0)
    sw0 = math.sin(w0)
    alpha = 0.5 * sw0 / Q
    b1 = - 2.0 * cw0
    b0 = b2 = 1.0
    a0 = 1 + alpha
    a1 = - 2.0 * cw0
    a2 = 1 - alpha
    return b0, b1, b2, a0, a1, a2

# Design a biquad allpass filter in canonical form
def biquad_apf(fs, f, Q):
    w0 = 2.0 * math.pi * f / fs
    cw0 = math.cos(w0)
    sw0 = math.sin(w0)
    alpha = 0.5 * sw0 / Q
    b2 = 1 + alpha
    b1 = - 2.0 * cw0
    b0 = 1 - alpha
    a0 = 1 + alpha
    a1 = - 2.0 * cw0
    a2 = 1 - alpha
    return b0, b1, b2, a0, a1, a2

# Z-transform and normalise a biquad filter, according to TMC
def biquad_Z_tmc(T, b0, b1, b2, a0, a1, a2):
    den = (T**2 - 2*a1 + 4*a2)
    b2z = (b0*(T**2) + 2*b1*T + 4*b2) / den
    b1z = (2*b0*(T**2) - 8*b2) / den
    b0z = (b0*(T**2) - 2*b1*T + 4*b2) / den
    a2z = (T**2 + 2*a1*T + 4*a2) / den
    a1z = (2*(T**2) - 8*a2) / den
    e29 = 2**29
    b0 = round(b0z/(a0) * e29)
    b1 = round(b1z/(a0) * e29)
    b2 = round(b2z/(a0) * e29)
    a1 = round(-a1z/a0 * e29)
    a2 = round(-a2z/a0 * e29)
    # return in the same order as the config registers
    return a1, a2, 0, b0, b1, b2

# Normalise a biquad filter, according to TMC
def biquad_tmc(b0, b1, b2, a0, a1, a2):
    e29 = 2**29
    b0 = round(b0/(a0) * e29)
    b1 = round(b1/(a0) * e29)
    b2 = round(b2/(a0) * e29)
    a1 = round(-a1/a0 * e29)
    a2 = round(-a2/a0 * e29)
    # return in the same order as the config registers
    return a1, a2, 0, b0, b1, b2
