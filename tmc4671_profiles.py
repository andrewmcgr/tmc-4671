# TMC4671 motor and board profile infrastructure
#
# Copyright (C) 2024  Andrew McGregor <andrewmcgr@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# Provides:
#   _MISSING          - sentinel for "key not in profile"
#   ConfigWithDefaults - config wrapper that injects profile defaults
#   FocProfile        - base class for FocMotor / FocBoard
#   BUILTIN_MOTORS    - dict of named built-in motor profiles
#   BUILTIN_BOARDS    - dict of named built-in board profiles

_MISSING = object()


class ConfigWithDefaults:
    """Thin Klipper config wrapper that injects motor/board profile defaults.

    All standard config getters are intercepted.  When a caller supplies a
    *default* argument (positional or keyword) and the profile contains a
    value for that key, the profile value replaces the caller's default.
    Instance-section values always win (Klipper reads the file first and only
    falls back to the default when the option is absent).

    Key matching rules
    ------------------
    * Direct lookup: ``voltage_scale_ratio`` → matches ``voltage_scale_ratio``
      in the profile dict.
    * Prefix stripping: ``set_config_field(config, "N_POLE_PAIRS", 4)``
      generates config key ``foc_n_pole_pairs`` (FieldHelper adds prefix
      ``foc_``).  ``_lookup`` strips ``foc_`` and matches ``n_pole_pairs``
      in the motor profile.  The same logic applies to the ``drv_`` prefix
      used by the TMC6100 FieldHelper.
    """

    def __init__(self, config, *profile_dicts):
        self._config = config
        # Earlier dicts (motor) take priority; merge in reverse so higher
        # priority wins.
        self._defaults = {}
        for d in reversed(profile_dicts):
            self._defaults.update(d)

    # ------------------------------------------------------------------
    # Internal helpers

    def _lookup(self, name):
        name_lower = name.lower()
        if name_lower in self._defaults:
            return self._defaults[name_lower]
        for prefix in ("foc_", "drv_"):
            if name_lower.startswith(prefix):
                stripped = name_lower[len(prefix):]
                if stripped in self._defaults:
                    return self._defaults[stripped]
        return _MISSING

    def _inject(self, name, args, kwargs):
        """Replace the caller's default with the profile value if present."""
        val = self._lookup(name)
        if val is _MISSING:
            return args, kwargs
        if 'default' in kwargs:
            kwargs = dict(kwargs, default=val)
        elif args:
            args = (val,) + args[1:]
        # No default supplied → required field; do not inject.
        return args, kwargs

    # ------------------------------------------------------------------
    # Intercepted config getters

    def getfloat(self, name, *args, **kwargs):
        args, kwargs = self._inject(name, args, kwargs)
        return self._config.getfloat(name, *args, **kwargs)

    def getint(self, name, *args, **kwargs):
        args, kwargs = self._inject(name, args, kwargs)
        return self._config.getint(name, *args, **kwargs)

    def getboolean(self, name, *args, **kwargs):
        args, kwargs = self._inject(name, args, kwargs)
        return self._config.getboolean(name, *args, **kwargs)

    def getchoice(self, name, *args, **kwargs):
        args, kwargs = self._inject(name, args, kwargs)
        return self._config.getchoice(name, *args, **kwargs)

    def get(self, name, *args, **kwargs):
        args, kwargs = self._inject(name, args, kwargs)
        return self._config.get(name, *args, **kwargs)

    # ------------------------------------------------------------------
    # Pass-through: delegate any attribute not explicitly defined above
    # to the underlying config object.  This covers has_section(),
    # getlists(), getsection(), get_name(), get_printer(), error(), and
    # anything else Klipper may call on the config object.

    def __getattr__(self, name):
        return getattr(self._config, name)


class FocProfile:
    """Base class for motor and board profile config sections.

    Subclasses define ``ALLOWED``: a list of ``(key, type_str)`` pairs where
    *key* is the natural name (no prefix) used in the profile section and
    *type_str* is one of ``'float'``, ``'int'``, ``'bool'``, ``'str'``.

    All allowed keys are optional in the profile section; unspecified keys are
    simply absent from ``get_values()``, allowing the hardcoded defaults in
    ``tmc4671.py`` to apply.
    """

    ALLOWED = []  # subclasses define this

    def __init__(self, config):
        self._name = config.get_name()
        self._config = config
        self._values = {}
        for key, type_str in self.ALLOWED:
            val = self._read_one(config, key, type_str)
            if val is not _MISSING:
                self._values[key] = val
        self._validate(config)

    def _read_one(self, config, key, type_str):
        if type_str == 'float':
            val = config.getfloat(key, None)
        elif type_str == 'int':
            val = config.getint(key, None)
        elif type_str == 'bool':
            val = config.getboolean(key, None)
        elif type_str == 'str':
            val = config.get(key, None)
        else:
            return _MISSING
        return _MISSING if val is None else val

    def _validate(self, config):
        pass  # override in subclasses

    def get_values(self):
        """Return a copy of the resolved profile dict."""
        return dict(self._values)


# ---------------------------------------------------------------------------
# Built-in profiles
# ---------------------------------------------------------------------------

BUILTIN_MOTORS = {
    'LDO_2504b-EN1000': {
        'motor_type':       2,
        'n_pole_pairs':     50,
        'motor_kt':         0.022,   # holding_torque 0.055 Nm / holding_current 2.5 A
        'jmotor':           8.45e-6,
        'abn_decoder_ppr':  4000,
    },
}

BUILTIN_BOARDS = {
    'OpenFFBoard': {
        'voltage_scale_ratio':      40.875,
        'current_scale_ma_lsb':     1.155,
        'adc_i_ux_select':          0,
        'adc_i_v_select':           2,
        'adc_i_wy_select':          1,
        'pwm_bbm_l':                9,
        'pwm_bbm_h':                9,
        'pidout_uq_ud_limits':      31440,
        'adc_temp_reg':             'AGPI_B',
        'adc_temp_pullup_resistor': 1500.0,
        'adc_temp_t1':              25.0,
        'adc_temp_r1':              10000.0,
        'adc_temp_beta':            4300.0,
    },
    'Ouroboros': {
        'voltage_scale_ratio':  40.875,
        'current_scale_ma_lsb': 1.272,
        'adc_i_ux_select':      0,
        'adc_i_v_select':       2,
        'adc_i_wy_select':      1,
        'pwm_bbm_l':            9,
        'pwm_bbm_h':            9,
        'pidout_uq_ud_limits':  31440,
    },
}
