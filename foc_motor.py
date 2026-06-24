# TMC4671 motor profile config section
#
# Copyright (C) 2024  Andrew McGregor <andrewmcgr@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# Handles [foc_motor <name>] config sections.  A motor profile captures all
# motor-specific hardware parameters (pole pairs, encoder geometry, Hall
# sensor settings, motor Kt, rotor inertia) so that multiple [tmc4671]
# instances driving the same motor model can share a single definition.
#
# Usage in printer.cfg:
#
#   [foc_motor nema17_1]
#   n_pole_pairs: 50
#   abn_decoder_ppr: 4000
#   motor_kt: 0.022
#   jmotor: 8.45e-6
#
#   [tmc4671 stepper_x]
#   motor_profile: nema17_1
#   ...

from .tmc4671_profiles import FocProfile


class FocMotor(FocProfile):
    """Motor profile: captures motor-specific hardware parameters.

    All fields are optional.  Unspecified fields fall through to the
    hardcoded defaults in tmc4671.py, exactly as if the profile were absent.

    ``motor_kt`` may be specified directly, **or** derived from
    ``holding_current`` + ``holding_torque`` (Kt = torque / current).
    Specifying both ``motor_kt`` and the holding pair is an error.
    """

    ALLOWED = [
        # Motor electrical / mechanical type
        ('motor_type',          'int'),    # 2 = two-phase stepper (default), 3 = BLDC
        ('n_pole_pairs',        'int'),    # number of electrical pole pairs

        # Motor torque constant
        ('motor_kt',            'float'),  # N·m / A (direct)
        ('holding_current',     'float'),  # A  ─┐ alternative: derive Kt
        ('holding_torque',      'float'),  # N·m ─┘
        ('rated_current',       'float'),  # A RMS; driver converts to peak (× √2) for run_current default

        # Rotor inertia
        ('jmotor',              'float'),  # kg·m²

        # ABN incremental encoder
        ('abn_decoder_ppr',     'int'),    # pulses per revolution
        ('abn_direction',       'bool'),   # reverse encoder direction
        ('abn_apol',            'bool'),   # A-channel polarity inversion
        ('abn_bpol',            'bool'),   # B-channel polarity inversion
        ('abn_npol',            'bool'),   # N-channel polarity inversion
        ('abn_use_abn_as_n',    'bool'),   # use ABN as N
        ('abn_cln',             'bool'),   # ABN clear-on-N

        # Analog encoder (AENC / Hall)
        ('aenc_deg',            'int'),    # 1 = 120°, 2 = 60° analogue Hall
        ('aenc_ppr',            'int'),    # analogue encoder PPR

        # Digital Hall sensor
        ('hall_interp',         'bool'),   # Hall interpolation
        ('hall_sync',           'bool'),   # sync Hall to PWM
        ('hall_polarity',       'bool'),   # invert Hall polarity
        ('hall_dir',            'bool'),   # reverse Hall direction
        ('hall_dphi_max',       'int'),    # max angular step between Hall edges
        ('hall_phi_e_offset',   'int'),    # electrical angle offset
        ('hall_blank',          'int'),    # Hall blank time (PWM cycles)

        # Feedback selection
        ('phi_e_selection',     'int'),    # 3 = ABN, 5 = Hall
    ]

    def _validate(self, config):
        hc = self._values.get('holding_current')
        ht = self._values.get('holding_torque')
        # Both or neither must be given.
        if (hc is None) != (ht is None):
            raise config.error(
                "'holding_current' and 'holding_torque' must be specified "
                "together in [%s]" % (self._name,))
        if hc is not None:
            if 'motor_kt' in self._values:
                raise config.error(
                    "Cannot specify both 'motor_kt' and "
                    "'holding_current'/'holding_torque' in [%s]"
                    % (self._name,))
            # Derive Kt and remove the raw pair from the profile dict so that
            # ConfigWithDefaults only sees 'motor_kt'.
            self._values['motor_kt'] = ht / hc
            del self._values['holding_current']
            del self._values['holding_torque']


def load_config_prefix(config):
    return FocMotor(config)
