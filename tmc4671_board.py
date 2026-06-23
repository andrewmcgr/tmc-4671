# TMC4671 board profile config section
#
# Copyright (C) 2024  Andrew McGregor <andrewmcgr@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# Handles [tmc4671_board <name>] config sections.  A board profile captures
# all PCB-specific parameters (voltage/current scaling, ADC channel
# assignments, dead-time settings, TMC6100 gate-driver settings, and the
# AGPI thermistor configuration) so that multiple [tmc4671] instances on the
# same board can share a single definition.
#
# Usage in printer.cfg:
#
#   [tmc4671_board myboard]
#   voltage_scale_ratio: 40.875
#   current_scale_ma_lsb: 1.272
#   adc_i_ux_select: 0
#   adc_i_v_select: 2
#   adc_i_wy_select: 1
#
#   [tmc4671 stepper_x]
#   board_profile: myboard
#   ...
#
# The built-in profile name 'OpenFFBoard' is available without any
# [tmc4671_board] section in printer.cfg:
#
#   [tmc4671 stepper_x]
#   board_profile: OpenFFBoard
#   ...

from .tmc4671_profiles import FocProfile


class FocBoard(FocProfile):
    """Board profile: captures PCB-specific hardware parameters.

    All fields are optional.  Unspecified fields fall through to the
    hardcoded defaults in tmc4671.py.
    """

    ALLOWED = [
        # Voltage and current scaling
        ('voltage_scale_ratio',      'float'),  # V_bus / ADC_full_scale
        ('current_scale_ma_lsb',     'float'),  # mA per ADC LSB

        # PWM frequency
        ('pwm_freq_target',          'float'),  # Hz; actual freq rounded to chip granularity

        # ADC current channel assignment (which ADC input maps to which phase)
        ('adc_i_ux_select',          'int'),    # phase U/X ADC channel
        ('adc_i_v_select',           'int'),    # phase V ADC channel
        ('adc_i_wy_select',          'int'),    # phase W/Y ADC channel

        # PWM dead-time (break-before-make) settings
        ('pwm_bbm_l',                'int'),    # low-side BBM time (PWM cycles)
        ('pwm_bbm_h',                'int'),    # high-side BBM time (PWM cycles)

        # Voltage output limit (32768 = Vm); also acts as anti-windup
        ('pidout_uq_ud_limits',      'int'),

        # TMC6100 gate driver (only relevant when drv_cs_pin is set)
        ('singleline',               'bool'),   # single-line SPI mode
        ('normal',                   'bool'),   # normal (not stealth) mode
        ('drvstrength',              'int'),    # gate drive strength (0-3)
        ('bbmclks',                  'int'),    # BBM clock cycles

        # AGPI thermistor configuration
        ('adc_temp_reg',             'str'),    # 'AGPI_A' or 'AGPI_B'
        ('adc_temp_pullup_resistor', 'float'),  # Ω — pull-down to GND
        ('adc_temp_t1',              'float'),  # °C reference temperature
        ('adc_temp_r1',              'float'),  # Ω thermistor resistance at t1
        ('adc_temp_beta',            'float'),  # thermistor beta coefficient
    ]


def load_config_prefix(config):
    return FocBoard(config)
