import math


class BitUtils:
    # Return the position of the first bit set in a mask
    def ffs(mask):
        return (mask & -mask).bit_length() - 1


class FormatUtils:
    def format_phi(val):
        phi = val * 360.0 / 65536.0
        if phi < 0.0:
            phi += 360
        return "%.3f" % (phi)

    def format_q4_12(val):
        return "%.4f" % (val * 2**-12)

    def to_q4_12(val):
        return round(val * 2**12) & 0xFFFF

    def from_q4_12(val):
        return val * 2**-12

    def format_q0_15(val):
        return "%.7f" % (val * 2**-15)

    def from_q8_8(val):
        return val * 2**-8

    def format_q8_8(val):
        return "%.3f" % (FormatUtils.from_q8_8(val))

    def to_q8_8(val):
        return round(val * 2**8) & 0xFFFF

    def format_q3_29(val):
        return "%.9f" % (val * 2**-29)


######################################################################
# Biquad filter utilities
######################################################################


class BiquadUtils:
    # Filter design formula from 4671 datasheet
    def biquad_lpf_tmc(fs, f, D):
        w0 = 2.0 * math.pi * f / fs
        b2 = b1 = 0.0
        b0 = 1.0
        a2 = 1.0 / (w0**2)
        a1 = 2.0 * D / w0
        a0 = 1.0
        return b0, b1, b2, a0, a1, a2

    # Filter design formulae from https://www.w3.org/TR/audio-eq-cookbook/

    # Design a biquad low pass filter in canonical form
    def biquad_lpf(fs, f, Q):
        w0 = 2.0 * math.pi * f / fs
        cw0 = math.cos(w0)
        sw0 = math.sin(w0)
        alpha = 0.5 * sw0 / Q
        b1 = 1.0 - cw0
        b0 = b2 = b1 / 2.0
        a0 = 1 + alpha
        a1 = -2.0 * cw0
        a2 = 1 - alpha
        return b0, b1, b2, a0, a1, a2

    # Design a biquad notch filter in canonical form
    def biquad_notch(fs, f, Q):
        w0 = 2.0 * math.pi * f / fs
        cw0 = math.cos(w0)
        sw0 = math.sin(w0)
        alpha = 0.5 * sw0 / Q
        b1 = -2.0 * cw0
        b0 = b2 = 1.0
        a0 = 1 + alpha
        a1 = -2.0 * cw0
        a2 = 1 - alpha
        return b0, b1, b2, a0, a1, a2

    # Design a biquad allpass filter in canonical form
    def biquad_apf(fs, f, Q):
        w0 = 2.0 * math.pi * f / fs
        cw0 = math.cos(w0)
        sw0 = math.sin(w0)
        alpha = 0.5 * sw0 / Q
        b2 = 1 + alpha
        b1 = -2.0 * cw0
        b0 = 1 - alpha
        a0 = 1 + alpha
        a1 = -2.0 * cw0
        a2 = 1 - alpha
        return b0, b1, b2, a0, a1, a2

    # Z-transform and normalise a biquad filter, according to TMC
    def biquad_Z_tmc(T, b0, b1, b2, a0, a1, a2):
        den = T**2 - 2 * a1 + 4 * a2
        b2z = (b0 * (T**2) + 2 * b1 * T + 4 * b2) / den
        b1z = (2 * b0 * (T**2) - 8 * b2) / den
        b0z = (b0 * (T**2) - 2 * b1 * T + 4 * b2) / den
        a2z = (T**2 + 2 * a1 * T + 4 * a2) / den
        a1z = (2 * (T**2) - 8 * a2) / den
        # dcgain = (b0z + b1z + b2z) / (a0z + a1z + a2z)
        dcgain = 1.0
        e29 = 2**29
        b0 = round(b0z / (a0 * dcgain) * e29)
        b1 = round(b1z / (a0 * dcgain) * e29)
        b2 = round(b2z / (a0 * dcgain) * e29)
        a1 = round(-a1z / a0 * e29)
        a2 = round(-a2z / a0 * e29)
        # return in the same order as the config registers
        return a1, a2, b0, b1, b2

    # Normalise a biquad filter, according to TMC
    def biquad_tmc(b0, b1, b2, a0, a1, a2):
        # dcgain = (b0 + b1 + b2) / (a0 + a1 + a2)
        dcgain = 1.0
        e29 = 2**29
        b0 = round(b0 / (a0 * dcgain) * e29)
        b1 = round(b1 / (a0 * dcgain) * e29)
        b2 = round(b2 / (a0 * dcgain) * e29)
        a1 = round(-a1 / a0 * e29)
        a2 = round(-a2 / a0 * e29)
        # return in the same order as the config registers
        return a1, a2, b0, b1, b2


class PIDUtils:
    # S-IMC PI controller design
    def simc(k, theta, tau1, tauc):
        Kc = (1.0 / k) * ((tau1 + theta / 3.0) / (tauc + theta))
        taui = min((tau1 + theta / 3.0), 4 * (tauc + theta))
        return Kc, taui
