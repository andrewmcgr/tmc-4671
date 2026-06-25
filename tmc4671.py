# TMC4671 servo driver support
#
# Copyright (C) 2024       Andrew McGregor <andrewmcgr@gmail.com>
#
# Based heavily on Klipper TMC stepper drivers which are:
#
# Copyright (C) 2018-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import dataclasses
import logging, collections
import math
import time
from time import monotonic_ns
from enum import IntEnum
from statistics import mean, fmean
from extras import bus, thermistor
from .tmc4671_regs import (
    Registers6100, Fields6100, Registers,
    ADC_GPIO_FIELDS, Fields, FloatFields, SignedFields,
    FieldFormatters, to_q4_12, from_q4_12, to_q8_8, from_q8_8,
    to_q2_30, from_q2_30
)
from .tmc4671_biquad import (
    BiquadFilter, BIQUAD_FILTER_TYPES, BIQUAD_FILTER_TARGETS,
    biquad_lpf, biquad_notch, biquad_apf,
    biquad_tmc
)
from .tmc4671_profiles import (
    ConfigWithDefaults, BUILTIN_MOTORS, BUILTIN_BOARDS
)

# The 4671 has a 25 MHz external clock
TMC_FREQUENCY=25000000.
# However there is a 100 MHz internal clock, hence 10 ns units in places

# Some magic numbers for the driver

class MotionMode(IntEnum):
    stopped_mode = 0
    torque_mode = 1
    velocity_mode = 2
    position_mode = 3
    uq_ud_ext_mode = 8

# Tuple is the address followed by a value to put in the next higher address
# to select that sub-register, or none to just go straight there.
# Not used for 6100, but there to use the same code.

DumpGroups6100 = {
    "Default": ["GCONF", "GSTAT", "IOIN", "SHORT_CONF", "DRV_CONF",],
}


DumpGroups = {
    "default": ["CHIPINFO_SI_TYPE", "CHIPINFO_SI_VERSION",
                "STATUS_FLAGS", "PHI_E"],
    "hall": ["HALL_MODE", "HALL_POSITION_060_000", "HALL_POSITION_180_120",
             "HALL_POSITION_300_240", "HALL_PHI_E_INTERPOLATED_PHI_E",
             "HALL_PHI_E_PHI_M_OFFSET", "HALL_PHI_M",],
    "abn": ["ABN_DECODER_COUNT", "ABN_DECODER_MODE", "ABN_DECODER_PPR",
            "ABN_DECODER_PHI_E_PHI_M_OFFSET", "ABN_DECODER_PHI_E_PHI_M",
            ],
    "adc": ["ADC_I1_RAW_ADC_I0_RAW",
            "ADC_IWY_IUX",
            "ADC_IV",
            "ADC_I0_SCALE_OFFSET",
            "ADC_I1_SCALE_OFFSET",
            ],
    "aenc": ["AENC_DECODER_MODE",
             "AENC_DECODER_PPR", "ADC_I1_RAW_ADC_I0_RAW",
             "ADC_AGPI_A_RAW_ADC_VM_RAW", "ADC_AENC_UX_RAW_ADC_AGPI_B_RAW",
             "ADC_AENC_WY_RAW_ADC_AENC_VN_RAW", "AENC_DECODER_PHI_A_RAW"],
    "pwm": ["PWM_POLARITIES", "PWM_MAXCNT", "PWM_BBM_H_BBM_L", "PWM_SV_CHOP",
            "MOTOR_TYPE_N_POLE_PAIRS"],
    "pidconf": ["PID_FLUX_P_FLUX_I", "PID_TORQUE_P_TORQUE_I",
                "PID_VELOCITY_P_VELOCITY_I", "PID_POSITION_P_POSITION_I",
                ],
    "monitor": [
            #"PID_VELOCITY_ACTUAL",
            #"PID_ERROR_PID_POSITION_ERROR",
            #"PID_ERROR_PID_VELOCITY_ERROR",
    ],
    "pid": ["PID_FLUX_P_FLUX_I", "PID_TORQUE_P_TORQUE_I",
            "PID_VELOCITY_P_VELOCITY_I", "PID_POSITION_P_POSITION_I",
            "PID_TORQUE_FLUX_TARGET", "PID_TORQUE_FLUX_OFFSET",
            "PID_VELOCITY_TARGET", "PID_POSITION_TARGET",
            "PID_TORQUE_FLUX_ACTUAL",
            "INTERIM_PIDIN_TARGET_FLUX",
            "PID_ERROR_PID_FLUX_ERROR",
            "PID_ERROR_PID_FLUX_ERROR_SUM",
            "INTERIM_PIDIN_TARGET_TORQUE",
            "PID_ERROR_PID_TORQUE_ERROR",
            "PID_ERROR_PID_TORQUE_ERROR_SUM",
            "PID_VELOCITY_ACTUAL",
            "INTERIM_PIDIN_TARGET_VELOCITY",
            "PID_ERROR_PID_VELOCITY_ERROR",
            "PID_ERROR_PID_VELOCITY_ERROR_SUM",
            "PID_POSITION_ACTUAL",
            "INTERIM_PIDIN_TARGET_POSITION",
            "PID_ERROR_PID_POSITION_ERROR",
            "PID_ERROR_PID_POSITION_ERROR_SUM",
            ],
    "step": ["STEP_WIDTH", "PHI_E", "MODE_RAMP_MODE_MOTION", "STATUS_FLAGS",
             "PID_POSITION_TARGET"],
    "filters": [ "CONFIG_BIQUAD_X_A_1", "CONFIG_BIQUAD_X_A_2",
                "CONFIG_BIQUAD_X_B_0", "CONFIG_BIQUAD_X_B_1",
                "CONFIG_BIQUAD_X_B_2", "CONFIG_BIQUAD_X_ENABLE",
                "CONFIG_BIQUAD_V_A_1", "CONFIG_BIQUAD_V_A_2",
                "CONFIG_BIQUAD_V_B_0", "CONFIG_BIQUAD_V_B_1",
                "CONFIG_BIQUAD_V_B_2", "CONFIG_BIQUAD_V_ENABLE",
                "CONFIG_BIQUAD_T_A_1", "CONFIG_BIQUAD_T_A_2",
                "CONFIG_BIQUAD_T_B_0", "CONFIG_BIQUAD_T_B_1",
                "CONFIG_BIQUAD_T_B_2", "CONFIG_BIQUAD_T_ENABLE",
                "CONFIG_BIQUAD_F_A_1", "CONFIG_BIQUAD_F_A_2",
                "CONFIG_BIQUAD_F_B_0", "CONFIG_BIQUAD_F_B_1",
                "CONFIG_BIQUAD_F_B_2", "CONFIG_BIQUAD_F_ENABLE",],
}

######################################################################
# PI controller utilities
######################################################################

# S-IMC PI controller design, "Improved Method"
# See https://folk.ntnu.no/skoge/publications/2012/skogestad-improved-simc-pid/PIDbook-chapter5.pdf
# and http://npcw17.imm.dtu.dk/Proceedings/Session%207%20Control%20Theory/The%20improved%20SIMC%20method%20for%20PI%20controller%20tuning.pdf
def simc(k, theta, tau1, tauc):
    Kc = (1.0/k) * ((tau1 + theta / 3.0) / (tauc + theta))
    taui = min((tau1 + theta / 3.0), 4*(tauc + theta))
    return Kc, taui


######################################################################
# Field manipulation helpers
######################################################################


# Return the position of the first bit set in a mask
def ffs(mask):
    return (mask & -mask).bit_length() - 1

class FieldHelper:
    def __init__(self, all_fields, signed_fields=[], float_fields=[], field_formatters={}, field_setters={},
                 registers=None, prefix="driver_"):
        self.all_fields = all_fields
        self.signed_fields = {sf: 1 for sf in signed_fields}
        self.float_fields = {ff: 1 for ff in float_fields}
        self.field_formatters = field_formatters
        self.field_setters = field_setters
        self.registers = registers
        if self.registers is None:
            self.registers = collections.OrderedDict()
        self.field_to_register = { f: r for r, fields in self.all_fields.items()
                                   for f in fields }
        self.prefix = prefix
    def lookup_register(self, field_name, default=None):
        if field_name in Registers:
            return field_name
        return self.field_to_register.get(field_name, default)
    def get_field(self, field_name, reg_value=None, reg_name=None):
        # Returns value of the register field
        if reg_name is None:
            reg_name = self.lookup_register(field_name)
        if reg_value is None:
            reg_value = self.registers.get(reg_name, 0)
        if reg_name not in self.all_fields:
            mask = 0xffffffff
        else:
            mask = self.all_fields[reg_name][field_name]
        field_value = (reg_value & mask) >> ffs(mask)
        if field_name in self.signed_fields and ((reg_value & mask)<<1) > mask:
            field_value -= (1 << field_value.bit_length())
        return field_value
    def set_field(self, field_name, field_value, reg_value=None, reg_name=None):
        # Returns register value with field bits filled with supplied value
        if reg_name is None:
            reg_name = self.lookup_register(field_name)
        if reg_value is None:
            reg_value = self.registers.get(reg_name, 0)
        if reg_name == field_name:
            mask = 0xffffffff
        else:
            mask = self.all_fields[reg_name][field_name]
        new_value = (reg_value & ~mask) | ((field_value << ffs(mask)) & mask)
        self.registers[reg_name] = new_value
        return new_value
    def set_config_field(self, config, field_name, default, convert=lambda x: x):
        # Allow a field to be set from the config file
        config_name = self.prefix + field_name
        reg_name = self.lookup_register(field_name)
        if reg_name == field_name:
            mask = 0xffffffff
        else:
            mask = self.all_fields[reg_name][field_name]
        maxval = mask >> ffs(mask)
        if field_name in self.float_fields:
            val = config.getfloat(config_name, default)
        elif maxval == 1:
            val = config.getboolean(config_name, default)
        elif field_name in self.signed_fields:
            val = config.getint(config_name, default,
                                minval=-(maxval//2 + 1), maxval=maxval//2)
        else:
            val = config.getint(config_name, default, minval=0, maxval=maxval)
        self.field_setters[field_name] = convert
        return self.set_field(field_name, convert(val), reg_name=reg_name)
    def pretty_format(self, reg_name, reg_value):
        # Provide a string description of a register
        reg_fields = self.all_fields.get(reg_name, {reg_name: 0xffffffff})
        reg_fields = sorted([(mask, name) for name, mask in reg_fields.items()])
        fields = []
        for mask, field_name in reg_fields:
            field_value = self.get_field(field_name, reg_value, reg_name)
            sval = self.field_formatters.get(field_name, str)(field_value)
            if sval and sval != "0":
                fields.append(" %s=%s" % (field_name.lower(), sval))
        return "%-11s %08x%s" % (reg_name + ":", reg_value, "".join(fields))
    def get_reg_fields(self, reg_name, reg_value):
        # Provide fields found in a register
        reg_fields = self.all_fields.get(reg_name, {reg_name: 0})
        return {field_name: self.get_field(field_name, reg_value, reg_name)
                for field_name, mask in reg_fields.items()}


######################################################################
# Live field accessor: FieldProxy, SingleFieldAccessor, MultiFieldAccessor
######################################################################


@dataclasses.dataclass(frozen=True)
class FieldDesc:
    reg: int          # hardware SPI register address
    addr: object      # mux selector value, or None for direct registers
    mask: int         # bitmask for this field within the 32-bit register
    shift: int        # ffs(mask) — precomputed


def _build_field_descs(helper, name_to_reg):
    """Build {name: FieldDesc | list[(name, FieldDesc)]} from FieldHelper + name_to_reg.

    List values mean the key is a multi-field register exposed via MultiFieldAccessor.
    FieldDesc values are single sub-fields or undivided whole-register entries.
    """
    descs = {}
    for reg_name, (reg, addr) in name_to_reg.items():
        reg_fields = helper.all_fields.get(reg_name)
        if reg_fields and len(reg_fields) > 1:
            field_list = []
            for field_name, mask in reg_fields.items():
                d = FieldDesc(reg=reg, addr=addr, mask=mask, shift=ffs(mask))
                descs[field_name] = d
                field_list.append((field_name, d))
            descs[reg_name] = field_list
        elif reg_fields and len(reg_fields) == 1:
            field_name, mask = next(iter(reg_fields.items()))
            d = FieldDesc(reg=reg, addr=addr, mask=mask, shift=ffs(mask))
            descs[field_name] = d
            descs[reg_name] = d
        else:
            d = FieldDesc(reg=reg, addr=addr, mask=0xffffffff, shift=0)
            descs[reg_name] = d
    return descs


class SingleFieldAccessor:
    __slots__ = ('_proxy', '_desc')

    def __init__(self, proxy, desc):
        object.__setattr__(self, '_proxy', proxy)
        object.__setattr__(self, '_desc', desc)

    def read(self):
        d = object.__getattribute__(self, '_desc')
        p = object.__getattribute__(self, '_proxy')
        raw = p._spi_read(d.reg, d.addr)
        val = (raw & d.mask) >> d.shift
        if p._name_for_desc(d) in p._signed:
            bits = (d.mask >> d.shift).bit_length()
            if val >= (1 << (bits - 1)):
                val -= 1 << bits
        return val

    def write(self, val, *, verify=False):
        d = object.__getattribute__(self, '_desc')
        p = object.__getattribute__(self, '_proxy')
        if d.mask == 0xffffffff:
            new_reg = int(val) & 0xffffffff
        else:
            current = p._shadow_get(d.reg, d.addr)
            if current is None:
                current = p._spi_read(d.reg, d.addr)
            new_reg = (current & ~d.mask) | ((int(val) << d.shift) & d.mask)
        p._spi_write(d.reg, d.addr, new_reg, verify=verify)


class MultiFieldAccessor:
    __slots__ = ('_proxy', '_reg_name', '_descs')

    def __init__(self, proxy, reg_name, descs):
        object.__setattr__(self, '_proxy', proxy)
        object.__setattr__(self, '_reg_name', reg_name)
        object.__setattr__(self, '_descs', descs)

    def read(self):
        descs = object.__getattribute__(self, '_descs')
        p = object.__getattribute__(self, '_proxy')
        raw = p._spi_read(descs[0][1].reg, descs[0][1].addr)
        return tuple((raw & d.mask) >> d.shift for _, d in descs)

    def write(self, *values, verify=False):
        descs = object.__getattribute__(self, '_descs')
        reg_name = object.__getattribute__(self, '_reg_name')
        p = object.__getattribute__(self, '_proxy')
        if len(values) != len(descs):
            field_names = ', '.join(n for n, _ in descs)
            raise ValueError(
                "%s.write() expects %d arguments (%s), got %d"
                % (reg_name, len(descs), field_names, len(values)))
        new_reg = 0
        for val, (_, d) in zip(values, descs):
            new_reg |= (int(val) << d.shift) & d.mask
        d0 = descs[0][1]
        p._spi_write(d0.reg, d0.addr, new_reg, verify=verify)


class FieldProxy:

    def __init__(self, helper, mcu_tmc):
        object.__setattr__(self, '_helper', helper)
        object.__setattr__(self, '_mcu_tmc', mcu_tmc)
        object.__setattr__(self, '_shadow', {})
        descs = _build_field_descs(helper, mcu_tmc.name_to_reg)
        object.__setattr__(self, '_descs', descs)
        object.__setattr__(self, '_desc_to_name',
                           {id(d): n for n, d in descs.items()
                            if isinstance(d, FieldDesc)})
        object.__setattr__(self, '_signed', helper.signed_fields)

    @property
    def all_fields(self):
        return object.__getattribute__(self, '_helper').all_fields

    @property
    def signed_fields(self):
        return object.__getattribute__(self, '_helper').signed_fields

    @property
    def registers(self):
        return object.__getattribute__(self, '_helper').registers

    @property
    def field_to_register(self):
        return object.__getattribute__(self, '_helper').field_to_register

    @property
    def field_setters(self):
        return object.__getattribute__(self, '_helper').field_setters

    def lookup_register(self, *a, **kw):
        return object.__getattribute__(self, '_helper').lookup_register(*a, **kw)

    def get_field(self, *a, **kw):
        return object.__getattribute__(self, '_helper').get_field(*a, **kw)

    def set_field(self, *a, **kw):
        return object.__getattribute__(self, '_helper').set_field(*a, **kw)

    def set_config_field(self, *a, **kw):
        return object.__getattribute__(self, '_helper').set_config_field(*a, **kw)

    def pretty_format(self, *a, **kw):
        return object.__getattribute__(self, '_helper').pretty_format(*a, **kw)

    def get_reg_fields(self, *a, **kw):
        return object.__getattribute__(self, '_helper').get_reg_fields(*a, **kw)

    def __getattr__(self, name):
        descs = object.__getattribute__(self, '_descs')
        entry = descs.get(name)
        if entry is None:
            raise AttributeError("TMC4671 has no field or register %r" % name)
        if isinstance(entry, list):
            return MultiFieldAccessor(self, name, entry)
        return SingleFieldAccessor(self, entry)

    def _name_for_desc(self, desc):
        return object.__getattribute__(self, '_desc_to_name').get(id(desc), "")

    def _shadow_get(self, reg, addr):
        return object.__getattribute__(self, '_shadow').get((reg, addr))

    def _spi_read(self, reg, addr):
        return object.__getattribute__(self, '_mcu_tmc')._read_raw(reg, addr)

    def _spi_write(self, reg, addr, val, *, verify=False):
        object.__getattribute__(self, '_mcu_tmc')._write_raw(
            reg, addr, val, verify=verify)
        object.__getattribute__(self, '_shadow')[(reg, addr)] = val


class PIDHelper:
    def __init__(self, config, mcu_tmc, var, def_v, nvar, def_n):
        self.mcu_tmc = mcu_tmc
        self.fields = FieldProxy(mcu_tmc.get_fields(), mcu_tmc)
        fvar = "PID_" + var
        logging.info("TMC: %s", ','.join((str(i) for i in [var, def_v, nvar, fvar])))
        set_config_field = self.fields.set_config_field
        set_config_field(config, nvar, def_n)
        if self.fields.get_field(nvar):
            self.to_f = to_q4_12
            self.from_f = from_q4_12
        else:
            self.to_f = to_q8_8
            self.from_f = from_q8_8
        FieldFormatters[fvar] = self.from_f
        set_config_field(config, fvar, def_v, convert=self.to_f)

class FFHelper:
    def __init__(self, config, mcu_tmc, var, def_v):
        self.mcu_tmc = mcu_tmc
        self.fields = FieldProxy(mcu_tmc.get_fields(), mcu_tmc)
        logging.info("TMC: %s", ','.join((str(i) for i in [var, def_v])))
        set_config_field = self.fields.set_config_field
        self.to_f = to_q2_30
        self.from_f = from_q2_30
        FieldFormatters[var] = self.from_f
        set_config_field(config, var, def_v, convert=self.to_f)

######################################################################
# Current control
######################################################################


MAX_CURRENT = 10.000

class CurrentHelper:
    def __init__(self, config, mcu_tmc):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.mcu_tmc = mcu_tmc
        self.fields = FieldProxy(mcu_tmc.get_fields(), mcu_tmc)
        rated_current = config.getfloat('rated_current', None, above=0.,
                                        maxval=MAX_CURRENT)
        if rated_current is not None:
            default_run = rated_current * math.sqrt(2)
            self.run_current = config.getfloat('run_current', default_run,
                                               above=0., maxval=MAX_CURRENT)
        else:
            self.run_current = config.getfloat('run_current',
                                               above=0., maxval=MAX_CURRENT)
        self.homing_current = config.getfloat('homing_current', above=0.,
                                              maxval=MAX_CURRENT,
                                              default=self.run_current)
        self.flux_current = config.getfloat('flux_current',
                                              maxval=MAX_CURRENT,
                                              default=0.)
        self.current_scale = config.getfloat('current_scale_ma_lsb', 1.272,
                                       above=0., maxval=10)
        self.flux_limit = self._calc_flux_limit(self.run_current)
        self.fields.set_field("PID_TORQUE_FLUX_LIMITS", self.flux_limit)
        self.flux_limit = self._calc_flux_limit(self.flux_current)
        self.fields.set_field("PID_FLUX_OFFSET", self.flux_limit)
    def _calc_flux_limit(self, current):
        flux_limit = round(current * 1e3 / self.current_scale)
        return flux_limit
    def convert_adc_current(self, adc):
        return adc * self.current_scale * 1e-3
    def get_run_current(self):
        return self.run_current
    def get_homing_current(self):
        return self.homing_current
    def get_current(self):
        c = self.convert_adc_current(self._read_field("PID_TORQUE_FLUX_LIMITS"))
        iux = self.convert_adc_current(self._read_field("ADC_IUX"))
        iv = self.convert_adc_current(self._read_field("ADC_IV"))
        iwy = self.convert_adc_current(self._read_field("ADC_IWY"))
        return c, MAX_CURRENT, iux, iv, iwy
    def get_qd_current(self):
        id = self.convert_adc_current(self._read_field("PID_FLUX_ACTUAL"))
        iq = self.convert_adc_current(self._read_field("PID_TORQUE_ACTUAL"))
        return iq, id
    def set_current(self, run_current):
        self.run_current = run_current
        self.flux_limit = self._calc_flux_limit(self.run_current)
        self._write_field("PID_TORQUE_FLUX_LIMITS", self.flux_limit)
        return self.flux_limit
    def apply_current_limit(self, current):
        flux_limit = self._calc_flux_limit(current)
        self._write_field("PID_TORQUE_FLUX_LIMITS", flux_limit)
        return flux_limit
    def set_flux_current(self, current):
        self.flux_current = current
        self.flux_limit = self._calc_flux_limit(self.flux_current)
        self._write_field("PID_FLUX_OFFSET", self.flux_limit)
        return self.flux_limit
    def _read_field(self, field):
        return getattr(self.fields, field).read()
    def _write_field(self, field, val):
        getattr(self.fields, field).write(val)


######################################################################
# Helper to configure the microstep settings
######################################################################


def StepHelper(config, mcu_tmc):
    fields = FieldProxy(mcu_tmc.get_fields(), mcu_tmc)
    stepper_name = " ".join(config.get_name().split()[1:])
    if not config.has_section(stepper_name):
        raise config.error(
            "Could not find config section '[%s]' required by tmc4671 driver"
            % (stepper_name,))
    sconfig = config.getsection(stepper_name)
    steps = {1<<i: 1<<i for i in range(0, 16)}
    res = sconfig.getchoice('full_steps_per_rotation', steps, default=8)
    mres = sconfig.getchoice('microsteps', steps, default=256)
    # STEP_WIDTH is added to PID_POSITION_TARGET (in position-source counts)
    # on each STEP pulse.  65536 counts = 1 revolution of the position source.
    # With phi_m (POSITION_SELECTION 9-12) that is one mechanical revolution, so
    # step_width = 65536 / (res * mres) is correct.  With phi_e (values 0-8),
    # 65536 counts = 1 electrical revolution = 1/N_POLE_PAIRS mechanical
    # revolutions, so step_width must be scaled up by N_POLE_PAIRS to keep the
    # same physical step size.
    pos_sel = config.getint('position_selection', default=9)
    npp = config.getint('n_pole_pairs', default=4)
    ppoles = 1 if pos_sel >= 9 else npp
    if res * mres > 65536 * ppoles:
        raise config.error(
            "Product of res and mres must not be more than %d for [%s]"
            % (65536 * ppoles, stepper_name,))
    step_width = (65536 * ppoles) // (res * mres)
    fields.set_field("STEP_WIDTH", step_width)


######################################################################
# Periodic error checking
######################################################################


class TMCErrorCheck:
    def __init__(self, config, mcu_tmc, current_helper):
        self.printer = config.get_printer()
        name_parts = config.get_name().split()
        self.stepper_name = ' '.join(name_parts[1:])
        self.mcu_tmc = mcu_tmc
        self.fields = FieldProxy(mcu_tmc.get_fields(), mcu_tmc)
        self.current_helper = current_helper
        self.check_timer = None
        self.is_enabled = False
        self.status_warn_mask = self._make_mask(["PID_IQ_TARGET_LIMIT",
                                                 "PID_ID_TARGET_LIMIT",
                                                 "PID_V_OUTPUT_LIMIT",
                                                 "REF_SW_R",
                                                 "REF_SW_L"])
        # Useful for debugging
        #self.status_warn_mask = 0xffffffff
        self.status_error_mask = self._make_mask([#"PWM_MIN",
                                                  #"PWM_MAX",
                                                  #"AENC_CLIPPED",
                                                  "ADC_I_CLIPPED"
                                                  ])
        self.last_status = 0
        self.monitor_data = {n: None
                             for reg_name in DumpGroups["monitor"]
                             for n in self.fields.get_reg_fields(reg_name, 0)
                             }
        self.monitor_data.update({'current_ux': 0., 'current_v': 0.,
                                  'current_wy': 0.})
        # Setup for temperature query via AGPI_A or AGPI_B
        self.adc_temp = None
        self.adc_temp_reg = config.getchoice("adc_temp_reg",
                                             ADC_GPIO_FIELDS,
                                             default=None)
        self._thermistor = None
        self.temp_callback = None
        self.last_temp = 0.
        self.temp_minmax = (0., 999.)
        if self.adc_temp_reg is not None:
            pullup = config.getfloat("adc_temp_pullup_resistor", 1500.,
                                     above=0.)
            t1 = config.getfloat("adc_temp_t1", 25.)
            r1 = config.getfloat("adc_temp_r1", 10000., above=0.)
            beta = config.getfloat("adc_temp_beta", 4300., above=0.)
            self._thermistor = thermistor.Thermistor(pullup, 0.)
            self._thermistor.setup_coefficients_beta(t1, r1, beta)
            # Register this object by name so tmc4671_temperature_sensor
            # sections can look it up at connect time, regardless of section
            # ordering in the config file.
            obj_name = "tmc4671_agpi %s" % (self.stepper_name,)
            self.printer.add_object(obj_name, self)
    def _make_mask(self, entries):
        mask = 0
        for f in entries:
            mask = self.fields.set_field(f, 1, mask, "STATUS_FLAGS")
        return mask
    def _query_status(self):
        status = self.mcu_tmc.get_register("STATUS_FLAGS")
        # fmt = self.fields.pretty_format("STATUS_FLAGS", status)
        # logging.info("TMC 4671 '%s' raw %s", self.stepper_name, fmt)
        if status & self.status_warn_mask != self.last_status & self.status_warn_mask:
            fmt = self.fields.pretty_format("STATUS_FLAGS", status)
            logging.info("TMC 4671 '%s' reports %s", self.stepper_name, fmt)
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        status = self.mcu_tmc.get_register("STATUS_FLAGS")
        self.last_status = status
        if status & self.status_error_mask:
            fmt = self.fields.pretty_format("STATUS_FLAGS", status)
            raise self.printer.command_error("TMC 4671 '%s' reports error: %s"
                                             % (self.stepper_name, fmt))
    def _query_temperature(self, eventtime):
        if self.adc_temp_reg is None:
            return
        try:
            self.adc_temp = getattr(self.fields, self.adc_temp_reg).read()
            temp = self._convert_temp(self.adc_temp)
            if temp is not None:
                self.last_temp = temp
                if self.temp_callback is not None:
                    self.temp_callback(eventtime, temp)
        except self.printer.command_error:
            self.adc_temp = None
    def _do_periodic_check(self, eventtime):
        try:
            if self.is_enabled:
                self._query_status()
            self._query_temperature(eventtime)
            if self.is_enabled:
                ch = self.current_helper
                self.monitor_data['current_ux'] = ch.convert_adc_current(
                    ch._read_field("ADC_IUX"))
                self.monitor_data['current_v'] = ch.convert_adc_current(
                    ch._read_field("ADC_IV"))
                self.monitor_data['current_wy'] = ch.convert_adc_current(
                    ch._read_field("ADC_IWY"))
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))
            return self.printer.get_reactor().NEVER
        return eventtime + 1.
    def stop_checks(self):
        # Disable full status/current monitoring when motor is disabled.
        # The timer itself keeps running so temperature is always polled.
        self.is_enabled = False
    def start_monitoring(self):
        if self.check_timer is not None:
            return
        reactor = self.printer.get_reactor()
        curtime = reactor.monotonic()
        self.check_timer = reactor.register_timer(self._do_periodic_check,
                                                  curtime + 1.)
    def start_checks(self):
        self.is_enabled = True
        self.start_monitoring()
        return True
    def _convert_temp(self, adc_raw):
        # ADC u16: midscale 0x8000 = 0 V, full range ±2.5 V (single-ended,
        # INN tied to GNDA). adc_fraction = V_AGPI / 2.5 V.
        # Circuit: thermistor on high side, pullup on low side → flip fraction.
        v = adc_raw - 32768
        if v <= 0:
            logging.debug("TMC %s AGPI raw=%d (v=%d ≤ 0, no positive voltage)",
                          self.stepper_name, adc_raw, v)
            return None
        adc_fraction = v / 32767.0
        return self._thermistor.calc_temp(1.0 - adc_fraction)
    def setup_minmax(self, min_temp, max_temp):
        self.temp_minmax = (min_temp, max_temp)
    def setup_callback(self, temperature_callback):
        self.temp_callback = temperature_callback
    def get_report_time_delta(self):
        return 1.
    def get_status(self, eventtime=None):
        res = {'drv_status': None, 'temperature': None}
        if self.is_enabled:
            res.update(self.monitor_data)
        if self.check_timer is None:
            return res
        if self.adc_temp_reg is not None:
            res['temperature'] = self.last_temp
            res['adc_temp_raw'] = self.adc_temp
        return res


######################################################################
# Helper class for "sensorless homing"
######################################################################


class TMCVirtualPinHelper:
    def __init__(self, config, mcu_tmc, current_helper):
        self.printer = config.get_printer()
        self.mcu_tmc = mcu_tmc
        self.fields = FieldProxy(mcu_tmc.get_fields(), mcu_tmc)
        self.current_helper = current_helper
        self.diag_pin = config.get('diag_pin', None)
        self.mcu_endstop = None
        self.en_pwm = False
        self._saved_velocity_limit = 0x10000000
        # PID_V_OUTPUT_LIMIT fires during position-mode homing acceleration
        # (position PID immediately saturates on large position error, velocity
        # I-term winds up before the motor reaches the hard stop), causing false
        # triggers.  PID_IQ_TARGET_LIMIT is the reliable indicator: we set
        # PID_VELOCITY_LIMIT to 0x7FFFFFFF during the homing move so the
        # velocity PID output can grow until it exceeds PID_TORQUE_FLUX_LIMITS
        # (homing current limit), firing within ~1 PWM cycle at true stall.
        self.status_mask_entries = config.getlist("homing_mask",
                                                  ["PID_IQ_OUTPUT_LIMIT",
                                                   "PID_ID_OUTPUT_LIMIT",
                                                   "PID_X_ERRSUM_LIMIT",
                                                   #"PID_IQ_ERRSUM_LIMIT",
                                                   #"PID_ID_ERRSUM_LIMIT",
                                                   "PID_IQ_TARGET_LIMIT",
                                                   "PID_ID_TARGET_LIMIT",
                                                   #"PID_X_OUTPUT_LIMIT",
                                                   #"PID_V_OUTPUT_LIMIT",
                                                   "REF_SW_R",
                                                   "REF_SW_L"])
        self.status_mask = 0
        for f in self.status_mask_entries:
            self.status_mask = self.fields.set_field(f, 1,
                                                     self.status_mask,
                                                     "STATUS_FLAGS")
        # Register virtual_endstop pin
        name_parts = config.get_name().split()
        self.name = "_".join(name_parts)
        logging.info("TMC virtual endstop %s, mask is %x", self.name, self.status_mask)
        ppins = self.printer.lookup_object("pins")
        ppins.register_chip("%s" % (self.name), self)
        self.printer.register_event_handler("homing:homing_move_begin",
                                            self.handle_homing_move_begin)
        self.printer.register_event_handler("homing:homing_move_end",
                                            self.handle_homing_move_end)
    def setup_pin(self, pin_type, pin_params):
        ppins = self.printer.lookup_object('pins')
        if pin_type != 'endstop' or pin_params['pin'] != 'virtual_endstop':
            raise ppins.error("tmc virtual endstop only useful as endstop")
        if pin_params['invert'] or pin_params['pullup']:
            raise ppins.error("Can not pullup/invert tmc virtual pin")
        if self.diag_pin is None:
            raise ppins.error("tmc virtual endstop requires diag pin config")
        self.mcu_endstop = ppins.setup_pin('endstop', self.diag_pin)
        return self.mcu_endstop
    def handle_homing_move_begin(self, hmove):
        # Always observe: set STATUS_MASK and log flags for any homing move on this axis.
        # Homing current change is only applied when this is the active (virtual) endstop.
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        self.printer.lookup_object('toolhead').dwell(0.005)
        self.fields.STATUS_MASK.write(self.status_mask)
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        status = self.mcu_tmc.get_register("STATUS_FLAGS")
        fmt = self.fields.pretty_format("STATUS_FLAGS", status)
        logging.info("TMC 4671 '%s' status at homing start %s", self.name, fmt)
        if self.mcu_endstop not in hmove.get_mcu_endstops():
            return
        self._saved_velocity_limit = self.mcu_tmc.get_register("PID_VELOCITY_LIMIT")
        self.fields.PID_VELOCITY_LIMIT.write(0x7fffffff)
        self.current_helper.apply_current_limit(self.current_helper.get_homing_current())
    def handle_homing_move_end(self, hmove):
        status = self.mcu_tmc.get_register("STATUS_FLAGS")
        fmt = self.fields.pretty_format("STATUS_FLAGS", status)
        logging.info("TMC 4671 '%s' status at homing end %s", self.name, fmt)
        # Always: clear STATUS_MASK after any homing move on this axis.
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        self.fields.STATUS_MASK.write(0)
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        if self.mcu_endstop not in hmove.get_mcu_endstops():
            return
        self.fields.PID_VELOCITY_LIMIT.write(self._saved_velocity_limit)
        self.current_helper.apply_current_limit(self.current_helper.get_run_current())


######################################################################
# SPI communication, fields, and registers
######################################################################

# 4671 does not support chaining, so that's removed
# 4671 protocol does not require dummy reads
# default speed is 1 MHz, conservative for the device.
# would need timing control if going faster than 2 MHz.
class MCU_TMC_SPI_simple:
    def __init__(self, config, pin_option="cs_pin"):
        self.printer = config.get_printer()
        self.mutex = self.printer.get_reactor().mutex()
        self.spi = bus.MCU_SPI_from_config(config, 3, default_speed=1000000, pin_option=pin_option)
    def reg_read(self, reg):
        cmd = [reg, 0x00, 0x00, 0x00, 0x00]
        #self.spi.spi_send(cmd)
        params = self.spi.spi_transfer(cmd)
        pr = bytearray(params['response'])
        return (pr[1] << 24) | (pr[2] << 16) | (pr[3] << 8) | pr[4]
    def reg_write_noread(self, reg, val, print_time=None):
        minclock = 0
        if print_time is not None:
            minclock = self.spi.get_mcu().print_time_to_clock(print_time)
        data = [(reg | 0x80) & 0xff, (val >> 24) & 0xff, (val >> 16) & 0xff,
                (val >> 8) & 0xff, val & 0xff]
        self.spi.spi_send(data, minclock)
    def reg_write(self, reg, val, print_time=None):
        minclock = 0
        if print_time is not None:
            minclock = self.spi.get_mcu().print_time_to_clock(print_time)
        data = [(reg | 0x80) & 0xff, (val >> 24) & 0xff, (val >> 16) & 0xff,
                (val >> 8) & 0xff, val & 0xff]
        self.spi.spi_send(data, minclock)
        return self.reg_read(reg)

# Helper code for working with TMC devices via SPI
# 4671 does have overlay registers, so support those
class MCU_TMC_SPI:
    def __init__(self, config, name_to_reg, fields, tmc_frequency, pin_option):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.tmc_spi = MCU_TMC_SPI_simple(config, pin_option=pin_option)
        self.mutex = self.tmc_spi.mutex
        self.name_to_reg = name_to_reg
        self.fields = fields
        self.tmc_frequency = tmc_frequency
    def get_fields(self):
        return self.fields
    def get_register(self, reg_name):
        reg, addr = self.name_to_reg[reg_name]
        with self.mutex:
            if addr is not None:
                for retry in range(5):
                    v = self.tmc_spi.reg_write(reg+1, addr)
                    if v == addr:
                        break
                else:
                    raise self.printer.command_error(
                        "Unable to write tmc spi '%s' address register %s (last read %x)" % (self.name, reg_name, v))
            read = self.tmc_spi.reg_read(reg)
        return read
    def set_register_once(self, reg_name, val, print_time=None):
        reg, addr = self.name_to_reg[reg_name]
        with self.mutex:
            if addr is not None:
                v = self.tmc_spi.reg_write(reg+1, addr, print_time)
                if v != addr:
                    raise self.printer.command_error(
                        "Unable to write tmc spi '%s' address register %s (last read %x)" % (self.name, reg_name, v))
            v = self.tmc_spi.reg_write(reg, val, print_time)
    def set_register(self, reg_name, val, print_time=None):
        reg, addr = self.name_to_reg[reg_name]
        with self.mutex:
            if addr is not None:
                for retry in range(5):
                    v = self.tmc_spi.reg_write(reg+1, addr, print_time)
                    if v == addr:
                        break
                else:
                    raise self.printer.command_error(
                        "Unable to write tmc spi '%s' address register %s (last read %x)" % (self.name, reg_name, v))
            
            # Certain registers contain highly dynamic fields (e.g., OPENLOOP_PHI in 0x23, or
            # OPENLOOP_VELOCITY_ACTUAL in 0x22) that are constantly updated by the internal DDS
            # and change on every PWM clock cycle. Bypassing verification for these is mandatory
            # to prevent spurious write-verification failures during startup/operation.
            bypass_verify = reg_name in ["OPENLOOP_VELOCITY_ACTUAL", "OPENLOOP_PHI"]
            
            for retry in range(5):
                v = self.tmc_spi.reg_write(reg, val, print_time)
                if bypass_verify or v == val:
                    return
        raise self.printer.command_error(
            "Unable to write tmc spi '%s' address register %s (last read %x)" % (self.name, reg_name, v))
    def get_tmc_frequency(self):
        return self.tmc_frequency
    def read_field(self, field):
        reg_name = self.fields.lookup_register(field)
        reg_value = self.get_register(reg_name)
        return self.fields.get_field(field,
                                     reg_value=reg_value,
                                     reg_name=reg_name)
    def write_field(self, field, val):
        reg_name = self.fields.lookup_register(field)
        reg_value = self.get_register(reg_name)
        self.set_register(reg_name,
                          self.fields.set_field(field,
                                                val,
                                                reg_value=reg_value,
                                                reg_name=reg_name))
    def _read_raw(self, reg, addr):
        with self.mutex:
            if addr is not None:
                for retry in range(5):
                    v = self.tmc_spi.reg_write(reg + 1, addr)
                    if v == addr:
                        break
                else:
                    raise self.printer.command_error(
                        "Unable to write tmc spi '%s' address selector "
                        "(last read %x)" % (self.name, v))
            return self.tmc_spi.reg_read(reg)
    def _write_raw(self, reg, addr, val, *, verify=False):
        with self.mutex:
            if addr is not None:
                for retry in range(5):
                    v = self.tmc_spi.reg_write(reg + 1, addr)
                    if v == addr:
                        break
                else:
                    raise self.printer.command_error(
                        "Unable to write tmc spi '%s' address selector "
                        "(last read %x)" % (self.name, v))
            if not verify:
                self.tmc_spi.reg_write_noread(reg, val)
                return
            for retry in range(5):
                v = self.tmc_spi.reg_write(reg, val)
                if v == val:
                    return
        raise self.printer.command_error(
            "Unable to write tmc spi '%s' register %x "
            "(last read %x)" % (self.name, reg, v))

######################################################################
# Profile resolution helper
######################################################################


def _resolve_profile(printer, config, key, builtin_db, section_prefix):
    """Look up a named motor or board profile and return its values dict.

    Resolution order:
      1. A ``[<section_prefix> <name>]`` config section present in printer.cfg
         (registered as a printer object by foc_motor.py / tmc4671_board.py).
      2. An entry in *builtin_db* (e.g. ``BUILTIN_BOARDS['OpenFFBoard']``).

    Returns an empty dict when *key* is not present in the instance config.
    """
    name = config.get(key, None)
    if name is None:
        return {}
    section_name = "%s %s" % (section_prefix, name)
    obj = printer.lookup_object(section_name, None)
    if obj is not None:
        return obj.get_values()
    if name in builtin_db:
        return builtin_db[name]
    raise config.error(
        "Profile '%s' not found for [%s]. "
        "Available built-in profiles: %s"
        % (name, config.get_name(),
           ', '.join(builtin_db.keys()) or '(none)'))


######################################################################
# Main driver class
######################################################################


class TMC4671:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.stepper_name = ' '.join(config.get_name().split()[1:])
        self.name = config.get_name().split()[-1]
        # Resolve motor and board profiles before any other config reads so
        # that ConfigWithDefaults can inject profile defaults transparently.
        motor_values = _resolve_profile(
            self.printer, config, 'motor_profile', BUILTIN_MOTORS, 'foc_motor')
        board_values = _resolve_profile(
            self.printer, config, 'board_profile', BUILTIN_BOARDS, 'tmc4671_board')
        overlap = set(motor_values) & set(board_values)
        if overlap:
            raise config.error(
                "Motor and board profiles both define: %s in [%s]"
                % (', '.join(sorted(overlap)), config.get_name()))
        if motor_values or board_values:
            config = ConfigWithDefaults(config, motor_values, board_values)
        self.mutex = self.printer.get_reactor().mutex()
        self.init_done = False
        self.alignment_done = False
        self.fields = FieldHelper(Fields,
                                  signed_fields=SignedFields,
                                  float_fields=FloatFields,
                                  field_formatters=FieldFormatters,
                                  prefix="foc_")
        field_meta = self.fields
        # 6100 is optional for boards without one.
        gcode = self.printer.lookup_object("gcode")
        if config.get("drv_cs_pin", None) is not None:
            self.fields6100 = FieldHelper(Fields6100, prefix="drv_")
            self.mcu_tmc6100 = MCU_TMC_SPI(config, Registers6100, self.fields6100,
                                           12e6, pin_option="drv_cs_pin")
            gcode.register_mux_command("DUMP_TMC6100", "STEPPER", self.name,
                                       self.cmd_DUMP_TMC6100,
                                       desc=self.cmd_DUMP_TMC6100_help)
        else:
            self.fields6100 = None
            self.mcu_tmc6100 = None
        # These will be calibrated later, but this is roughly correct
        self.vm_offset = 32768
        self.vm_range = round(32767/2.5)
        # Correct for the OpenFFBoard
        self.voltage_scale = config.getfloat('voltage_scale_ratio', 40.875,
                                       above=0.)
        self.motor_r = 0.0
        self.motor_l = 0.0
        self.motor_ld = 0.0
        self.motor_lq = 0.0
        self.motor_saliency = 1.0
        self.dead_time_v = 0.0
        self.jmotor = config.getfloat('jmotor', 8.45e-6, above=0.)
        self.jload  = config.getfloat('jload',  5e-5,    above=0.)
        # If load_mass is provided, compute the reflected inertia of a linear
        # load driven by a lead-screw or belt.  rotation_distance (mm/rev) is
        # read from the stepper section and converted to m/rev; gear_ratio
        # (same format as the Kalico stepper config: "N:D" pairs) reduces the
        # effective pitch so the formula becomes:
        #   J_load = m * (pitch_m / 2π)²   where pitch_m = rotation_distance_m / gear_ratio
        load_mass = config.getfloat('load_mass', None, minval=0.)
        if load_mass is not None:
            sconfig = config.getsection(self.stepper_name)
            rotation_distance_m = sconfig.getfloat('rotation_distance') / 1000.0
            gr_pairs = sconfig.getlists('gear_ratio', (), seps=(':', ','),
                                        count=2, parser=float)
            gear_ratio = 1.0
            for n, d in gr_pairs:
                gear_ratio *= n / d
            effective_pitch_m = rotation_distance_m / gear_ratio
            self.jload = load_mass * (effective_pitch_m / (2.0 * math.pi)) ** 2
        self.motor_kt = config.getfloat('motor_kt', 0.0156, above=0.)
        # If holding_current and holding_torque are both provided, derive
        # motor_kt (Kt = torque / current, N·m/A).  Both must be specified
        # together.
        holding_current = config.getfloat('holding_current', None, above=0.)
        holding_torque  = config.getfloat('holding_torque',  None, above=0.)
        if (holding_current is None) != (holding_torque is None):
            raise config.error(
                "Both 'holding_current' and 'holding_torque' must be "
                "specified together in [%s]" % (config.get_name(),))
        if holding_current is not None:
            self.motor_kt = holding_torque / holding_current
        self.velocity_alpha = config.getfloat('velocity_alpha', 0.35,
                                              minval=0., maxval=1.)
        self.current_bandwidth = config.getfloat('current_bandwidth', 1200.0,
                                                  above=0.)
        self.flux_bandwidth = config.getfloat('flux_bandwidth',
                                               self.current_bandwidth, above=0.)
        self.torque_bandwidth = config.getfloat('torque_bandwidth',
                                                 self.current_bandwidth, above=0.)
        self.velocity_bandwidth = config.getfloat('velocity_bandwidth', 450.0,
                                                   above=0.)
        self.position_bandwidth = config.getfloat('position_bandwidth', 100.0,
                                                   above=0.)
        self.mcu_tmc = MCU_TMC_SPI(config, Registers, field_meta,
                                   TMC_FREQUENCY, pin_option="cs_pin")
        self.fields = FieldProxy(field_meta, self.mcu_tmc)
        self.read_translate = None
        self.read_registers = Registers.keys()
        self.printer.register_event_handler("klippy:connect",
                                            self._handle_connect)
        #self.printer.register_event_handler("idle_timeout:ready",
        #                                    self._handle_connect)
        self.stepper = None
        self.stepper_enable = self.printer.load_object(config, "stepper_enable")
        self.printer.register_event_handler("klippy:mcu_identify",
                                            self._handle_mcu_identify)
        self.printer.register_event_handler("klippy:disconnect",
                                            self._handle_disconnect)
        self.printer.register_event_handler("homing:home_rails_begin",
                                            self._handle_home_rails_begin)
        # Register commands
        self.step_helper = StepHelper(config, self.mcu_tmc)
        self.current_helper = CurrentHelper(config, self.mcu_tmc)
        self.error_helper = TMCErrorCheck(config, self.mcu_tmc,
                                          self.current_helper)
        TMCVirtualPinHelper(config, self.mcu_tmc, self.current_helper)
        gcode.register_mux_command("SET_TMC_FIELD", "STEPPER", self.name,
                                   self.cmd_SET_TMC_FIELD,
                                   desc=self.cmd_SET_TMC_FIELD_help)
        gcode.register_mux_command("DUMP_TMC", "STEPPER", self.name,
                                   self.cmd_DUMP_TMC,
                                   desc=self.cmd_DUMP_TMC_help)
        gcode.register_mux_command("TMC_DEBUG_MOVE", "STEPPER", self.name,
                                   self.cmd_TMC_DEBUG_MOVE,
                                   desc=self.cmd_TMC_DEBUG_MOVE_help)
        gcode.register_mux_command("TMC_TUNE_MOTION_PID", "STEPPER", self.name,
                                   self.cmd_TMC_TUNE_MOTION_PID,
                                   desc=self.cmd_TMC_TUNE_MOTION_PID_help)
        gcode.register_mux_command("TMC_TUNE_PID", "STEPPER", self.name,
                                   self.cmd_TMC_TUNE_PID,
                                   desc=self.cmd_TMC_TUNE_PID_help)
        gcode.register_mux_command("INIT_TMC", "STEPPER", self.name,
                                   self.cmd_INIT_TMC,
                                   desc=self.cmd_INIT_TMC_help)
        gcode.register_mux_command("SET_TMC_CURRENT", "STEPPER", self.name,
                                   self.cmd_SET_TMC_CURRENT,
                                   desc=self.cmd_SET_TMC_CURRENT_help)
        gcode.register_mux_command(
            "SET_TMC_BIQUAD_FILTER",
            "STEPPER",
            self.name,
            self.cmd_SET_TMC_BIQUAD_FILTER,
            desc=self.cmd_SET_TMC_BIQUAD_FILTER_help,
        )
        gcode.register_mux_command(
            "TMC_DEBUG_VOLTAGE",
            "STEPPER",
            self.name,
            self.cmd_TMC_DEBUG_VOLTAGE,
            desc=self.cmd_TMC_DEBUG_VOLTAGE_help,
        )
        gcode.register_mux_command(
            "TMC_DEBUG_CURRENT",
            "STEPPER",
            self.name,
            self.cmd_TMC_DEBUG_CURRENT,
            desc=self.cmd_TMC_DEBUG_CURRENT_help,
        )
        gcode.register_mux_command(
            "TMC_DEBUG_MOTOR",
            "STEPPER",
            self.name,
            self.cmd_TMC_DEBUG_MOTOR,
            desc=self.cmd_TMC_DEBUG_MOTOR_help,
        )
        gcode.register_mux_command(
            "TMC_DEBUG_TUNING",
            "STEPPER",
            self.name,
            self.cmd_TMC_DEBUG_TUNING,
            desc=self.cmd_TMC_DEBUG_TUNING_help,
        )
        gcode.register_mux_command(
            "TMC_MEASURE_IMPEDANCE",
            "STEPPER",
            self.name,
            self.cmd_TMC_MEASURE_IMPEDANCE,
            desc=self.cmd_TMC_MEASURE_IMPEDANCE_help,
        )
        # Allow other registers to be set from the config
        set_config_field = self.fields.set_config_field
        if self.fields6100 is not None:
            set_config6100_field = self.fields6100.set_config_field
            # defaults as per 4671+6100 BOB datasheet
            set_config6100_field(config, "singleline", 0)
            set_config6100_field(config, "normal", 1)
            set_config6100_field(config, "DRVSTRENGTH", 0)
            set_config6100_field(config, "BBMCLKS", 10)
        self.pwm_freq_target = config.getfloat('pwm_freq_target',
                                               default=142857,
                                               minval=10e3, maxval=150e3)
        maxcnt = int((4.0 * TMC_FREQUENCY / self.pwm_freq_target) - 1)
        set_config_field(config, "PWM_MAXCNT", maxcnt)
        # These are used later by filter definitions
        # Actual frequency
        self.pwmfreq = 4.0 * TMC_FREQUENCY / (maxcnt + 1.0)
        self.pwmT = (maxcnt + 1.0) * 10e-9
        self.mdec = round(self.pwmT / (3.0 * 40e-9) - 2)
        set_config_field(config, "DSADC_MDEC_A", self.mdec)
        set_config_field(config, "DSADC_MDEC_B", self.mdec)
        set_config_field(config, "PWM_BBM_L", 10)
        set_config_field(config, "PWM_BBM_H", 10)
        set_config_field(config, "PWM_CHOP", 7)
        set_config_field(config, "PWM_SV", 1)
        set_config_field(config, "MOTOR_TYPE", 2)
        set_config_field(config, "N_POLE_PAIRS", 4)
        set_config_field(config, "ADC_I_UX_SELECT", 0)
        set_config_field(config, "ADC_I_V_SELECT", 2)
        set_config_field(config, "ADC_I_WY_SELECT", 1)
        set_config_field(config, "ADC_I0_SELECT", 0)
        set_config_field(config, "ADC_I1_SELECT", 1)
        #set_config_field(config, "CFG_ADC_I0", 0)
        #set_config_field(config, "CFG_ADC_I1", 0)
        #set_config_field(config, "CFG_ADC_VM", 4)
        set_config_field(config, "AENC_DEG", 1)    # 120 degree analog hall
        set_config_field(config, "AENC_PPR", 1)    # 120 degree analog hall
        set_config_field(config, "ABN_APOL", 0)
        set_config_field(config, "ABN_BPOL", 0)
        set_config_field(config, "ABN_NPOL", 0)
        set_config_field(config, "ABN_USE_ABN_AS_N", 0)
        set_config_field(config, "ABN_CLN", 0)
        set_config_field(config, "ABN_DIRECTION", 0)
        set_config_field(config, "ABN_DECODER_PPR", 4000)
        set_config_field(config, "HALL_INTERP", 0)
        set_config_field(config, "HALL_SYNC", 1)
        set_config_field(config, "HALL_POLARITY", 0)
        set_config_field(config, "HALL_DIR", 0)
        set_config_field(config, "HALL_DPHI_MAX", 0xAAAA)
        set_config_field(config, "HALL_PHI_E_OFFSET", 0)
        set_config_field(config, "HALL_BLANK", 2)
        # 3: ABN, 5: Hall
        set_config_field(config, "PHI_E_SELECTION", 3)
        # 0: phi_e, 3: ABN_e 5: Hall_e 9: ABN_m 12: Hall_m
        set_config_field(config, "POSITION_SELECTION", 9)
        set_config_field(config, "VELOCITY_SELECTION", 3)
        #set_config_field(config, "VELOCITY_METER_SELECTION", 0) # Default velocity meter
        set_config_field(config, "VELOCITY_METER_SELECTION", 1) # PWM frequency velocity meter
        set_config_field(config, "MODE_PID_SMPL", 0) # Advanced PID samples position at fPWM
        set_config_field(config, "MODE_PID_TYPE", 1) # Advanced PID mode
        # This also acts as anti-windup protection, and needs some headroom
        set_config_field(config, "PIDOUT_UQ_UD_LIMITS", 29000) # Voltage limit, 32768 = Vm
        # TODO: get this from the size of the printer
        set_config_field(config, "PID_POSITION_LIMIT_LOW", -0x10000000)
        set_config_field(config, "PID_POSITION_LIMIT_HIGH", 0x10000000)
        # TODO: Units, what should this be anyway?
        set_config_field(config, "PID_VELOCITY_LIMIT", 0x10000000)
        pid_defaults = [
            ("FLUX_P", 9.4, "CURRENT_P_n", 0),
            ("FLUX_I", 0.087, "CURRENT_I_n", 1),
            ("TORQUE_P", 9.4, "CURRENT_P_n", 0),
            ("TORQUE_I", 0.087, "CURRENT_I_n", 1),
            ("VELOCITY_P", 4.5, "VELOCITY_P_n", 0),
            ("VELOCITY_I", 0.0, "VELOCITY_I_n", 1),
            ("POSITION_P", 2.5, "POSITION_P_n", 0),
            ("POSITION_I", 0.0, "POSITION_I_n", 1)
            ]
        self.pid_helpers = {n: PIDHelper(config, self.mcu_tmc, n, v, nn, nv)
                            for n, v, nn, nv in pid_defaults}

        set_config_field(config, "MODE_FF", 0) # Feed forward off
        self.ff_helpers = {n: FFHelper(config, self.mcu_tmc, n, v)
                           for n, v in [
                                        ("FEED_FORWARD_VELOCITY_GAIN", 0.0),
                                        ("FEED_FORWARD_VELOCITY_FILTER_CONSTANT", 0.0),
                                        ("FEED_FORWARD_TORQUE_GAIN", 0.0),
                                        ("FEED_FORWARD_TORQUE_FILTER_CONSTANT", 0.0)
                                       ]
                           }

        self.monitor_data = {n: None
                             for reg_name in DumpGroups["monitor"]
                             for n in self.fields.get_reg_fields(reg_name, 0)
                             }

        self.tune_current_pid = config.getboolean('tune_current_pid', False)
        self.tune_motion_pid = config.getboolean('tune_motion_pid', False)

        self.biquad_filters = {}
        for target in BIQUAD_FILTER_TARGETS.keys():
            filter_type = config.getchoice(
                f"biquad_{target}_filter",
                BIQUAD_FILTER_TYPES,
                default="lpf",
            )
            freq_kwargs = {}
            if target == 'position' or \
               (self.tune_current_pid and target in ('flux', 'torque')) or \
               (self.tune_motion_pid and target == 'velocity'):
                freq_kwargs['default'] = 0.0
            freq = config.getfloat(
                f"biquad_{target}_frequency",
                minval=0,
                maxval=4.0 * TMC_FREQUENCY,
                **freq_kwargs
            )
            slope = config.getfloat(
                f"biquad_{target}_slope",
                above=0.0,
                default=2**-0.5,
            )
            self.biquad_filters[target] = BiquadFilter(
                type=filter_type,
                freq=freq,
                slope=slope,
            )

    def enable_biquad(self, enable_field, *biquad):
        with self.mcu_tmc.tmc_spi.mutex:
            reg, addr = self.mcu_tmc.name_to_reg[enable_field]
            for o, i in enumerate(biquad):
                self.mcu_tmc.tmc_spi.reg_write(reg+1, addr-6+o)
                self.mcu_tmc.tmc_spi.reg_write(reg, i)
            self.mcu_tmc.tmc_spi.reg_write(reg+1, addr)
            self.mcu_tmc.tmc_spi.reg_write(reg, 1)

    def disable_biquad(self, enable_field):
        with self.mcu_tmc.tmc_spi.mutex:
            reg, addr = self.mcu_tmc.name_to_reg[enable_field]
            self.mcu_tmc.tmc_spi.reg_write(reg+1, addr)
            self.mcu_tmc.tmc_spi.reg_write(reg, 0)

    def _do_enable(self, print_time):
        try:
            with self.mutex:
                self.fields.PID_POSITION_TARGET.write(
                    self.fields.PID_POSITION_ACTUAL.read(), verify=True)
                self.error_helper.start_checks()
                self.fields.MODE_MOTION.write(MotionMode.position_mode,
                                              verify=True)
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))

    def _do_disable(self, print_time):
        try:
            with self.mutex:
                self.error_helper.stop_checks()
                self.fields.MODE_MOTION.write(MotionMode.stopped_mode,
                                              verify=True)
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))

    def _handle_mcu_identify(self):
        # Lookup stepper object
        force_move = self.printer.lookup_object("force_move")
        self.stepper = force_move.lookup_stepper(self.stepper_name)
        # Note default pulse duration and step_both_edge unavailable
        self.stepper.setup_default_pulse_duration(.000000100, False)

    def _handle_stepper_enable(self, print_time, is_enable):
        if is_enable:
            cb = (lambda ev: self._do_enable(print_time))
        else:
            cb = (lambda ev: self._do_disable(print_time))
        self.printer.get_reactor().register_callback(cb)

    def _handle_connect(self):
        enable_line = self.stepper_enable.lookup_enable(self.stepper_name)
        try:
            self._init_registers()
        except self.printer.command_error as e:
            logging.info("TMC %s failed to init: %s", self.name, str(e))
        # Grab a fresh print_time *after* _init_registers() finishes: that function
        # internally runs ~0.5 s of toolhead dwell for ADC calibration, so any
        # print_time captured before it would translate to an MCU clock value
        # already in the past, triggering "Timer too close" on motor_enable.
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        with self.mutex:
            self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
            self.fields.STATUS_MASK.write(0)
            self.fields.PID_TORQUE_FLUX_TARGET.write(0, 0)
            self.fields.PID_VELOCITY_TARGET.write(0)
            self.fields.PID_POSITION_TARGET.write(0)
            if self.fields6100 is not None:
                self.mcu_tmc6100.set_register("GCONF",
                                              self.fields6100.set_field("disable", 0),
                                              print_time)
            enable_line.motor_enable(print_time)
            try:
                # _init_registers() already ran _calibrate_adc(); skip it here.
                self._align_and_measure(True, print_time)
                self.fields.ABN_DECODER_COUNT.write(0)
                self.fields.PID_POSITION_TARGET.write(0)
                self.alignment_done = True
            except self.printer.command_error as e:
                logging.error("TMC %s: startup calibration failed: %s",
                              self.name, str(e))
            print_time = self.printer.lookup_object('toolhead').get_last_move_time()
            enable_line.motor_disable(print_time)
            self.fields.STATUS_MASK.write(0)
            self.fields.PID_TORQUE_FLUX_TARGET.write(0, 0)
            self.fields.PID_VELOCITY_TARGET.write(0)
            self.fields.ABN_DECODER_COUNT.write(0)
            self.fields.PID_POSITION_TARGET.write(0)
            self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
            if self.tune_current_pid:
                try:
                    self._apply_current_pid(self.flux_bandwidth,
                                            self.torque_bandwidth)
                    logging.info("TMC %s: startup current PID tuning complete",
                                 self.name)
                except self.printer.command_error as e:
                    logging.error("TMC %s: startup current PID tuning failed: %s",
                                  self.name, str(e))
            if self.tune_motion_pid:
                try:
                    self._apply_motion_pid(self.velocity_bandwidth,
                                           self.position_bandwidth)
                    logging.info("TMC %s: startup motion PID tuning complete",
                                 self.name)
                except self.printer.command_error as e:
                    logging.error("TMC %s: startup motion PID tuning failed: %s",
                                  self.name, str(e))
            self.init_done = True
        self.error_helper.start_monitoring()
        enable_line.register_state_callback(self._handle_stepper_enable)

    def _handle_disconnect(self):
        if self.fields6100 is not None:
            try:
                self.mcu_tmc6100.set_register(
                    "GCONF", self.fields6100.set_field("disable", 1), None)
            except Exception:
                pass

    def _handle_home_rails_begin(self, homing_state, rails):
        if self.init_done:
            return
        for rail in rails:
            for stepper in rail.get_steppers():
                if stepper.get_name() == self.stepper_name:
                    raise self.printer.command_error(
                        "Cannot home '%s': TMC4671 startup initialisation "
                        "has not completed. Wait for calibration to finish "
                        "or run FIRMWARE_RESTART if it failed."
                        % (self.stepper_name,)
                    )

    def _calibrate_adc(self, print_time):
        self.fields.PWM_CHOP.write(0)
        self.fields.CFG_ADC_I0.write(0)
        self.fields.CFG_ADC_I1.write(0)
        i0_off, i1_off = self._sample_adc("ADC_I1_RAW_ADC_I0_RAW")
        # Following code would calibrate the scalers as well.
        # However, not doing that makes things simpler, and the
        # calibration result is always +- 1 from nominal.
        #self.fields.CFG_ADC_I0.write(2)
        #self.fields.CFG_ADC_I1.write(2)
        #i0_l, i1_l = self._sample_adc("ADC_I1_RAW_ADC_I0_RAW")
        #self.fields.CFG_ADC_I0.write(3)
        #self.fields.CFG_ADC_I1.write(3)
        #i0_h, i1_h = self._sample_adc("ADC_I1_RAW_ADC_I0_RAW")
        #self.fields.CFG_ADC_I0.write(0)
        #self.fields.CFG_ADC_I1.write(0)
        #self.fields.ADC_I1_SCALE.write((256*(i1_h-i1_l))//32768)
        #self.fields.ADC_I0_SCALE.write((256*(i0_h-i0_l))//32768)
        self.fields.ADC_I1_SCALE.write(256)
        self.fields.ADC_I0_SCALE.write(256)
        self.fields.ADC_I1_OFFSET.write(i1_off)
        self.fields.ADC_I0_OFFSET.write(i0_off)
        # Calibrate for VM measurement
        # Chip errata? This doesn't work.
        #self.fields.CFG_ADC_VM.write(5)
        #vml, vmh = self._sample_vm()
        #self.vm_offset = round(mean((vml, vmh)))
        #self.fields.CFG_ADC_VM.write(7)
        #vml, vmh = self._sample_vm()
        #self.vm_range = self.vm_offset - round(mean((vml, vmh)))
        #self.fields.CFG_ADC_VM.write(4)
        logging.info("TMC 4671 %s ADC offsets I0=%d I1=%d", self.name, i0_off, i1_off)
        #logging.info("TMC 4671 %s ADC VM offset=%d range=%s VM=%g", self.name,
        #             self.vm_offset, self.vm_range, self._read_vm())
        # Now calibrate for brake chopper
        vml, vmh = self._sample_vm()
        vmr = abs(vmh - vml)
        logging.info("TMC 4671 %s VM samples low=%d high=%d", self.name, vml, vmh)
        high = math.ceil(0.05*self.voltage_scale) + vmr//2 + vmh
        if high < 65536:
            self.fields.ADC_VM_LIMIT_HIGH.write(high)
            self.fields.ADC_VM_LIMIT_LOW.write(vmr//2 + vmh)
            logging.info("TMC 4671 %s brake thresholds low=%d(%g V) high=%d(%g V)", self.name,
                         vmr//2+vmh, self._convert_vm(vmr//2+vmh),
                         high, self._convert_vm(high))
        else:
            # What else can we do but turn the brake off?
            self.fields.ADC_VM_LIMIT_HIGH.write(0)
            self.fields.ADC_VM_LIMIT_LOW.write(0)
        self.fields.PWM_CHOP.write(7)

    def _sample_adc(self, reg_name):
        self.printer.lookup_object('toolhead').dwell(0.2)
        reg, addr = self.mcu_tmc.name_to_reg[reg_name]
        i1 = []
        i0 = []
        n = 100
        with self.mcu_tmc.tmc_spi.mutex:
            self.mcu_tmc.tmc_spi.reg_write(reg+1, addr)
            for i in range(n):
                v = self.fields.get_reg_fields(reg_name,
                                               self.mcu_tmc.tmc_spi.reg_read(reg))
                i1.append(v["ADC_I1_RAW"])
                i0.append(v["ADC_I0_RAW"])
                self.printer.lookup_object('toolhead').dwell(0.0005)
        return int(round(fmean(i0))), int(round(fmean(i1)))

    def _sample_vm(self):
        self.printer.lookup_object('toolhead').dwell(0.2)
        vm = []
        n = 100
        for i in range(n):
            vm.append(self.fields.ADC_VM_RAW.read())
            self.printer.lookup_object('toolhead').dwell(0.0005)
        return min(vm), max(vm)

    def _convert_vm(self, val):
        return ((val - self.vm_offset) / float(self.vm_range)) * self.voltage_scale

    def _read_vm(self):
        return self._convert_vm(self.fields.ADC_VM_RAW.read())

    def _reset_targets(self):
        self.fields.PID_TORQUE_TARGET.write(0)
        self.fields.PID_VELOCITY_TARGET.write(0)
        self.fields.PID_POSITION_TARGET.write(0)
        self.fields.PID_POSITION_ACTUAL.write(0)

    def _average_currents(self, samples=20, interval=0.005):
        dwell = self.printer.lookup_object('toolhead').dwell
        iux_samples = []
        iwy_samples = []
        c = 0
        for i in range(samples):
            c, MAX_I, tmp_iux, iv, tmp_iwy = self.current_helper.get_current()
            iux_samples.append(tmp_iux)
            iwy_samples.append(tmp_iwy)
            dwell(interval)
        return sum(iux_samples) / float(samples), sum(iwy_samples) / float(samples), c

    def _tune_flux_pid(self, test_existing, derate, print_time):
        return self._tune_pid("FLUX", 2.5, derate, test_existing, print_time)

    def _tune_torque_pid(self, test_existing, derate, print_time):
        return self._tune_pid("TORQUE", 1.0, derate, test_existing, print_time)

    def _tune_current_pid(self, current_bandwidth, motor_r=None, motor_l=None):
        if motor_r is None:
            motor_r = self.motor_r
        if motor_l is None:
            motor_l = self.motor_l
        # 1. Calculate continuous physical gains
        omega_bw = 2.0 * math.pi * current_bandwidth
        Kp_physical = omega_bw * motor_l

        # 2. Extract hardware loop scaling factors
        # current_scale is in mA/LSB, convert to A/LSB
        amps_per_adc_count = self.current_helper.current_scale * 1e-3
        vm_voltage = self._read_vm()

        hardware_loop_gain = (amps_per_adc_count * 32768.0) / max(vm_voltage, 0.001)

        # 3. Apply loop gain to P
        P = Kp_physical * hardware_loop_gain

        # 4. Calculate I as an analytical plant ratio for Advanced Mode (Serial structure)
        # I = R / (L * f_pwm)
        I = motor_r / (motor_l * self.pwmfreq)
        return P, I

    def vpoles(self):
        """Return the velocity pole-pair scale factor.

        VELOCITY_SELECTION values 9-12 select a mechanical angle source
        (phi_m_abn, phi_m_abn_2, phi_m_aenc, phi_m_hal), meaning velocity
        registers are in mechanical RPM and no pole-pair conversion is needed,
        so this returns 1.  Values 0-8 select an electrical angle source
        (phi_e_*), meaning velocity registers are in electrical RPM, so this
        returns N_POLE_PAIRS.
        """
        if self.fields.VELOCITY_SELECTION.read() >= 9:
            return 1
        return self.fields.N_POLE_PAIRS.read()

    def ppoles(self):
        """Return the position pole-pair scale factor.

        POSITION_SELECTION values 9-12 select a mechanical angle source
        (phi_m_abn, phi_m_abn_2, phi_m_aenc, phi_m_hal), meaning position
        registers are in mechanical angle units and no pole-pair conversion
        is needed, so this returns 1.  Values 0-8 select an electrical angle
        source (phi_e_*), meaning position registers are in electrical angle
        units, so this returns N_POLE_PAIRS.
        """
        if self.fields.POSITION_SELECTION.read() >= 9:
            return 1
        return self.fields.N_POLE_PAIRS.read()

    def _tune_motion_pid(self, Kt, l_v, l_p):
        Kadc = self.current_helper.current_scale * 1e-3
        NPP = self.vpoles()
        t_d = 1.

        k_v = Kadc / (Kt * math.pi)
        t_iv = 2.*l_v + t_d
        p_v = t_iv / (k_v * (l_v + t_d) ** 2)
        i_v = 1. / t_iv

        k_p = NPP / (256. * 50.)
        t_ip = 2.*l_p + t_d
        p_p = t_ip / (k_p * (l_p + t_d) ** 2)
        i_p = 1. / t_ip

        return p_v, i_v, p_p, i_p, k_v, k_p

    def _calc_velocity_pid(self, bandwidth):
        omega_bw = 2.0 * math.pi * bandwidth
        npoles = self.vpoles()
        j_total = self.jmotor + self.jload
        # velocity_p units: the TMC4671 applies PID_VELOCITY_P directly to the
        # ERPM error value with no implicit unit conversion.  omega_bw already
        # converts the bandwidth spec to rad/s; introducing a further 2π/60
        # RPM→rad/s factor here would make the gain ~10× too small.
        velocity_p = omega_bw * j_total / (npoles * self.motor_kt)
        nsmpl = self.fields.MODE_PID_SMPL.read()
        f_loop = self.pwmfreq / (nsmpl + 1)
        velocity_i = (1.0 - self.velocity_alpha) * omega_bw / (4.0 * f_loop)
        return velocity_p, velocity_i

    def _calc_position_pid(self, position_bandwidth):
        # The position controller output is a velocity command (in RPM of whatever
        # type VELOCITY_SELECTION uses).  ERROR_POSITION is in angle counts where
        # 65536 counts = one revolution of the *selected position source*:
        #   phi_m sources (POSITION_SELECTION 9-12): 65536 = one mechanical rev
        #   phi_e sources (POSITION_SELECTION 0-8):  65536 = one electrical rev
        #                                             = 1/N_POLE_PAIRS mech rev
        #
        # Switching from phi_m to phi_e multiplies ERROR_POSITION by N_POLE_PAIRS
        # for the same physical error, so position_p must be divided by ppoles()
        # to keep the same closed-loop bandwidth.  Similarly vpoles() accounts for
        # whether the velocity controller uses mechanical or electrical RPM.
        position_p = (2.0 * math.pi * position_bandwidth
                      / (self.vpoles() * self.ppoles()))
        return position_p

    def _apply_current_pid(self, flux_bw, torque_bw):
        flux_l = self.motor_ld if self.motor_ld != 0.0 else self.motor_l
        torque_l = self.motor_lq if self.motor_lq != 0.0 else self.motor_l
        if flux_l == 0.0 or torque_l == 0.0:
            raise self.printer.command_error(
                "Motor inductance not measured. Run "
                "FIRMWARE_RESTART to trigger startup calibration first.")
        P_flux, I_flux = self._tune_current_pid(flux_bw, motor_l=flux_l)
        P_torque, I_torque = self._tune_current_pid(torque_bw, motor_l=torque_l)
        for target, bw in (('flux', flux_bw), ('torque', torque_bw)):
            bf = BiquadFilter(
                type='lpf', freq=round(bw),
                slope=self.biquad_filters[target].slope)
            self.biquad_filters[target] = bf
            self._setup_filter(BIQUAD_FILTER_TARGETS[target], bf)
        self.fields.PID_FLUX_P.write(self.pid_helpers["FLUX_P"].to_f(P_flux))
        self.fields.PID_FLUX_I.write(self.pid_helpers["FLUX_I"].to_f(I_flux))
        self.fields.PID_TORQUE_P.write(self.pid_helpers["TORQUE_P"].to_f(P_torque))
        self.fields.PID_TORQUE_I.write(self.pid_helpers["TORQUE_I"].to_f(I_torque))
        cfgname = "tmc4671 %s" % (self.name,)
        configfile = self.printer.lookup_object('configfile')
        configfile.set(cfgname, 'foc_PID_FLUX_P', "%.3f" % (P_flux,))
        configfile.set(cfgname, 'foc_PID_FLUX_I', "%.3f" % (I_flux,))
        configfile.set(cfgname, 'foc_PID_TORQUE_P', "%.3f" % (P_torque,))
        configfile.set(cfgname, 'foc_PID_TORQUE_I', "%.3f" % (I_torque,))
        for target in ('flux', 'torque'):
            bf = self.biquad_filters[target]
            configfile.set(cfgname, 'biquad_%s_filter' % (target,), bf.type)
            configfile.set(cfgname, 'biquad_%s_frequency' % (target,),
                           "%.6g" % (bf.freq,))
            configfile.set(cfgname, 'biquad_%s_slope' % (target,),
                           "%.6g" % (bf.slope,))
        return P_flux, I_flux, P_torque, I_torque

    def _apply_motion_pid(self, v_bw, p_bw):
        p_v, i_v = self._calc_velocity_pid(v_bw)
        p_p = self._calc_position_pid(p_bw)
        i_p = 0.0
        vel_filter = BiquadFilter(
            type='lpf', freq=round(v_bw),
            slope=self.biquad_filters['velocity'].slope)
        self.biquad_filters['velocity'] = vel_filter
        self._setup_filter(BIQUAD_FILTER_TARGETS['velocity'], vel_filter)
        self.fields.PID_VELOCITY_P.write(self.pid_helpers["VELOCITY_P"].to_f(p_v))
        self.fields.PID_VELOCITY_I.write(self.pid_helpers["VELOCITY_I"].to_f(i_v))
        self.fields.PID_POSITION_P.write(self.pid_helpers["POSITION_P"].to_f(p_p))
        self.fields.PID_POSITION_I.write(self.pid_helpers["POSITION_I"].to_f(i_p))
        cfgname = "tmc4671 %s" % (self.name,)
        configfile = self.printer.lookup_object('configfile')
        configfile.set(cfgname, 'foc_PID_VELOCITY_P', "%.3f" % (p_v,))
        configfile.set(cfgname, 'foc_PID_VELOCITY_I', "%.3f" % (i_v,))
        configfile.set(cfgname, 'foc_PID_POSITION_P', "%.3f" % (p_p,))
        configfile.set(cfgname, 'foc_PID_POSITION_I', "%.3f" % (i_p,))
        bf = self.biquad_filters['velocity']
        configfile.set(cfgname, 'biquad_velocity_filter', bf.type)
        configfile.set(cfgname, 'biquad_velocity_frequency', "%.6g" % (bf.freq,))
        configfile.set(cfgname, 'biquad_velocity_slope', "%.6g" % (bf.slope,))
        return p_v, i_v, p_p, i_p

    def _prepare_for_alignment(self):
        """Stop the motor and restore motion-mode and external-input registers to
        their power-on defaults prior to running _align_and_measure.

        _align_and_measure was designed to run from the chip's hardware-reset
        state.  After a normal klippy:ready initialisation the following
        registers may hold stale values that cause the procedure to misbehave:

        * MODE_MOTION          – may be position_mode or velocity_mode from a
                                 prior motor-enable or motion command
        * PWM_CHOP             – gate driver left enabled from a prior run
        * UQ_UD_EXT            – residual external voltage command
        * PHI_E_EXT            – residual external angle
        * OPENLOOP_VELOCITY_TARGET / ACCELERATION / VELOCITY_ACTUAL / PHI
                               – residual DDS state from a previous inductance
                                 measurement.  VELOCITY_ACTUAL must be written
                                 explicitly: the DDS counter does not track
                                 TARGET when ACCELERATION is 0.  PHI holds the
                                 DDS accumulated phase angle, which persists
                                 after VELOCITY_ACTUAL is zeroed.
        * STATUS_MASK          – interrupt mask left set from a prior run
        * PID_TORQUE_FLUX_TARGET / PID_VELOCITY_TARGET / PID_POSITION_TARGET
                               – residual PID setpoints from a prior motor-
                               enable sequence (_handle_connect)
        * ABN_DECODER_COUNT    – residual encoder position from a prior run
        """
        self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
        self.fields.STATUS_MASK.write(0)
        self.fields.PWM_CHOP.write(0)
        self.fields.UQ_UD_EXT.write(0, 0)
        self.fields.PHI_E_EXT.write(0)
        self.fields.PID_TORQUE_FLUX_TARGET.write(0, 0)
        self.fields.PID_VELOCITY_TARGET.write(0)
        self.fields.PID_POSITION_TARGET.write(0)
        self.fields.ABN_DECODER_COUNT.write(0)
        self.fields.OPENLOOP_VELOCITY_TARGET.write(0)
        self.fields.OPENLOOP_ACCELERATION.write(0)
        self.fields.OPENLOOP_VELOCITY_ACTUAL.write(0)
        self.fields.OPENLOOP_PHI.write(0)

    # Align motor and measure resistance and inductance on startup
    def _align_and_measure(self, offsets, print_time):
        self._prepare_for_alignment()
        dwell = self.printer.lookup_object('toolhead').dwell
        old_phi_e_selection = self.fields.PHI_E_SELECTION.read()

        # Temporarily disable biquad filters during measurement to prevent attenuation of the 1 kHz signal
        for register in BIQUAD_FILTER_TARGETS.values():
            self.disable_biquad(register)

        self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
        self.fields.PHI_E_SELECTION.write(1) # external mode, so PHI_E won't change.
        self.fields.PHI_E_EXT.write(0) # and, set this to be PHI_E = 0
        # Start at some low voltage and see if we can read a current.
        # Read VM once; physical motor voltage = (UD_EXT / 32767) * vm.
        vm = self._read_vm()
        test_U = round(32767.0 / vm)
        # Gently pre-align the motor to angle 0 before the measurement. Without
        # this, a motor displaced from angle 0 after normal printing snaps hard
        # and rings at its natural frequency (~30-40 Hz); the oscillation may not
        # decay within the 300 ms measurement dwell and biases the averaged
        # current, leading to wrong R → wrong test2_U → wrong L.
        pre_align_U = max(1, test_U // 4)
        self.fields.UQ_UD_EXT.write(pre_align_U, 0)
        self._reset_targets()
        self.fields.MODE_MOTION.write(MotionMode.uq_ud_ext_mode)
        self.fields.PWM_CHOP.write(7)
        dwell(2.0)
        self.fields.PWM_CHOP.write(0)
        self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
        dwell(0.1)
        self.fields.UQ_UD_EXT.write(test_U, 0)
        self._reset_targets()
        self.fields.MODE_MOTION.write(MotionMode.uq_ud_ext_mode)
        # Turn on the chopper and wait a bit to measure the resistance
        self.fields.PWM_CHOP.write(7)
        dwell(0.3)
        # Average current readings to filter noise and ripple
        iux_first, iwy_first, c = self._average_currents(20, 0.005)
        self.fields.PWM_CHOP.write(0)
        logging.info("TMC 4671 '%s' initial averaged I: Ux=%0.4fA, Wy=%0.4fA", self.stepper_name, iux_first, iwy_first)
        I1 = max(abs(iux_first), abs(iwy_first))
        if I1 < 1e-6:
            # something is horribly wrong
             raise self.printer.command_error("TMC 4671 is seeing no motor current. Check wiring.")
        # Ok, calculate a voltage that will give us about a third of the configured current limit
        test2_U = round((c / 2.0) * test_U / I1)
        logging.info("TMC 4671 '%s' test U %g %g", self.stepper_name, test_U, test2_U)
        # Switch back on, and this time motor should self-align
        self.fields.UD_EXT.write(test2_U)
        self.fields.PWM_CHOP.write(7)
        dwell(0.5)
        # Average current readings to filter mechanical ringing and noise
        iux_second, iwy_second, _ = self._average_currents(20, 0.005)
        logging.info("TMC 4671 '%s' alignment averaged I: Ux=%0.4fA, Wy=%0.4fA", self.stepper_name, iux_second, iwy_second)
        I2 = max(abs(iux_second), abs(iwy_second))

        # Two-point differential measurement to exclude inverter dead-time
        V1 = (test_U  / 32767.0) * vm
        V2 = (test2_U / 32767.0) * vm

        delta_V = V2 - V1
        delta_I = I2 - I1

        if delta_I > 0.01:
            R = delta_V / delta_I
            self.dead_time_v = max(0.0, V2 - I2 * R)
            logging.info("TMC 4671 '%s' differential calculation: R=%g Ω, V_dead=%g V",
                         self.stepper_name, R, self.dead_time_v)
        else:
            R = V2 / I2
            self.dead_time_v = 0.0
            logging.warning("TMC 4671 '%s' differential current delta too small (%g A). "
                            "Falling back to single-point R=%g Ω.",
                            self.stepper_name, delta_I, R)
        self.motor_r = R
        logging.info("TMC 4671 '%s' est. motor R=%g Ω", self.stepper_name, R)

        # Inductance Measurement Procedure
        # Step 1: Magnetic Alignment (DC)
        # Keep PHI_E_SELECTION=1 (external angle, fixed at PHI_E_EXT=0) here.  Switching to
        # open-loop DDS mode (2) would expose the DC step to residual DDS velocity from a
        # previous run: the chip ignores writes to OPENLOOP_VELOCITY_ACTUAL when
        # ACCELERATION=0, so the DDS keeps spinning at the prior injection frequency.
        # A fixed external angle is completely immune to that state.
        self.fields.PWM_CHOP.write(0)
        self.fields.OPENLOOP_VELOCITY_TARGET.write(0)
        self.fields.OPENLOOP_VELOCITY_ACTUAL.write(0)  # Best-effort; may be ignored when ACCELERATION=0
        self.fields.UQ_EXT.write(0)
        self.fields.PWM_CHOP.write(7) # Re-enable the gate driver (crucial to apply AC voltage)

        # Automated AC Voltage Calculation
        I_target_A = 0.4
        V_req = (I_target_A * self.motor_r * 2.0) + 1.2
        vm = self._read_vm()
        if self.fields.MOTOR_TYPE.read() == 3:
            V_max_phase = vm / math.sqrt(3.0)
        else:
            V_max_phase = vm

        if V_req > V_max_phase:
            ac_U = 32767
        else:
            ac_U = int(32767.0 * (V_req / V_max_phase))
        ac_U = max(ac_U, 500)

        # Apply the exact same voltage for both tests to calibrate out dead-time
        self.fields.UD_EXT.write(ac_U)
        dwell(0.75)  # 750 ms mechanical settling delay

        # --- Measure True DC Current Magnitude AND Raw Averages ---
        dc_raw_qd_pairs = []
        for i in range(10):
            dc_raw_qd_pairs.append(self.current_helper.get_qd_current())
            dwell(0.001)

        dc_mag_samples = []
        id_dc_raw_samples = []
        iq_dc_raw_samples = []
        for iq, id in dc_raw_qd_pairs:
            dc_mag_samples.append(math.sqrt(id**2 + iq**2))
            id_dc_raw_samples.append(id)
            iq_dc_raw_samples.append(iq)

        I_DC_MAG = mean(dc_mag_samples)
        I_DC_RAW_D = mean(id_dc_raw_samples)
        I_DC_RAW_Q = mean(iq_dc_raw_samples)

        # Step 2: High-Frequency AC Injection
        # We inject a sine wave from the open-loop generator. This is high enough that the rotor stays
        # completely stationary.
        # The register value is an angle added to phi_e every cycle, angle units are 2^16 counts/revolution.
        # However, it's also a Q16.16 fixed-point value, so use 2^32.
        f_test = 1000
        dds_value = int(f_test * (2**32) / self.pwmfreq)

        self.fields.PHI_E_SELECTION.write(2)  # Open Loop (DDS) — only needed for AC injection
        self.fields.OPENLOOP_ACCELERATION.write(dds_value)  # We want snap acceleration for this test
        self.fields.OPENLOOP_VELOCITY_TARGET.write(dds_value)
        dwell(1.0)  # 1.0 s electrical settling delay (increased from 200 ms to ensure stability)

        # Step 3: Read Currents
        # --- Measure True AC Current Magnitude AND Raw Averages ---
        ac_raw_qd_pairs = []
        t_start = time.time()
        for i in range(100):
            t0 = time.time()
            qd = self.current_helper.get_qd_current()
            t1 = time.time()
            ac_raw_qd_pairs.append((qd, t0, t1))
            dwell(0.001)

        ac_mag_samples = []
        id_ac_raw_samples = []
        iq_ac_raw_samples = []
        ac_samples_with_time = []
        for qd, t0, t1 in ac_raw_qd_pairs:
            iq, id = qd
            mag = math.sqrt(id**2 + iq**2)
            ac_mag_samples.append(mag)
            id_ac_raw_samples.append(id)
            iq_ac_raw_samples.append(iq)
            t_mid = (t0 + t1) / 2.0 - t_start
            ac_samples_with_time.append((mag, t_mid))

        I_AC_MAG = mean(ac_mag_samples)
        I_AC_RAW_D = mean(id_ac_raw_samples)
        I_AC_RAW_Q = mean(iq_ac_raw_samples)

        # Step 4: Cleanup and Re-alignment
        self.fields.UQ_UD_EXT.write(0, 0)
        self.fields.OPENLOOP_VELOCITY_TARGET.write(0)
        self.fields.OPENLOOP_ACCELERATION.write(0)
        self.fields.OPENLOOP_VELOCITY_ACTUAL.write(0)  # Stop DDS; ACTUAL does not follow TARGET when ACCELERATION=0

        # CRITICAL: Since the motor was spun electrically, we MUST re-align and magnetically
        # lock the rotor back to the electrical zero position (PHI_E_EXT = 0) before continuing,
        # otherwise the subsequent encoder calibration will be misaligned, causing a runaway ("yeeting the toolhead").
        self.fields.PHI_E_EXT.write(0)
        self.fields.PHI_E_SELECTION.write(1)  # External angle mode
        self.fields.UD_EXT.write(test2_U)
        dwell(0.75)  # Let the rotor settle completely back to the aligned position
        # Now we should be mechanically aligned

        if offsets:
            # While we're here, set the offsets
            self.fields.HALL_PHI_E_OFFSET.write(-self.fields.HALL_PHI_E.read() % 65536)
            self.fields.ABN_DECODER_COUNT.write(0)
            self.fields.ABN_DECODER_PHI_E_OFFSET.write(0)
        # Put motion config back how it was / safe stopped state
        self.fields.UQ_UD_EXT.write(0, 0)
        self._reset_targets()
        self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
        self.fields.PHI_E_SELECTION.write(old_phi_e_selection)

        # Re-enable the configured biquad filters
        self._setup_filters()

        # =================================================================
        # Step 4: Hardware-Agnostic Impedance Math
        # =================================================================

        # Calculate the true voltage passing through the MOSFETs using the DC pulse
        # V_true = I * R
        V_true = I_DC_MAG * self.motor_r

        omega = 2.0 * math.pi * f_test

        if I_AC_MAG > 0 and V_true > 0:
            # Calculate total AC Impedance
            Z = V_true / I_AC_MAG

            # Isolate the Inductive Reactance (Z^2 = R^2 + X_L^2)
            Z_sq = Z**2
            R_sq = self.motor_r**2

            if Z_sq > R_sq:
                self.motor_l = math.sqrt(Z_sq - R_sq) / omega
            else:
                self.motor_l = 0.0
        else:
            self.motor_l = 0.0

        if I_AC_MAG > 0 and V_true > 0 and self.motor_l > 0.0:
            I_ripple_fit, Ld_fit, Lq_fit, sal_fit = self._calculate_impedance_method_b(
                ac_samples_with_time, I_AC_MAG, f_test, V_true, omega, self.motor_r
            )
            self.motor_ld = Ld_fit
            self.motor_lq = Lq_fit
            self.motor_saliency = sal_fit
        else:
            self.motor_ld = 0.0
            self.motor_lq = 0.0
            self.motor_saliency = 1.0

        logging.info("TMC 4671 '%s' L=%g H (ac_U=%d, Vm=%.1f)",
                     self.stepper_name, self.motor_l, ac_U, vm)
        logging.info("TMC 4671 '%s' Method B startup: Ld=%g H, Lq=%g H, saliency=%g",
                     self.stepper_name, self.motor_ld, self.motor_lq, self.motor_saliency)
        logging.info("   -> DC: Mag=%.3f A (Raw ID=%.3f, IQ=%.3f)",
                     I_DC_MAG, I_DC_RAW_D, I_DC_RAW_Q)
        logging.info("   -> AC: Mag=%.3f A (Raw ID=%.3f, IQ=%.3f)",
                     I_AC_MAG, I_AC_RAW_D, I_AC_RAW_Q)

    # Tune PID via a setpoint change experiment
    # See https://folk.ntnu.no/skoge/publications/2012/skogestad-improved-simc-pid/PIDbook-chapter5.pdf
    def _tune_pid(self, X, Kc, derate, test_existing, print_time):
        ch = self.current_helper
        dwell = self.printer.lookup_object('toolhead').dwell
        old_mode = self.fields.MODE_MOTION.read()
        self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
        limit_cur = self.fields.PID_TORQUE_FLUX_LIMITS.read()
        old_flux_offset = self.fields.PID_FLUX_OFFSET.read()
        self._reset_targets()

        # Switch to torque mode for the setpoint change experiment
        self.fields.MODE_MOTION.write(MotionMode.torque_mode)
        test_cur = limit_cur
        dwell(0.2)
        if not test_existing:
            Kc0 = Kc
            getattr(self.fields, "PID_%s_P"%X).write(self.pid_helpers["%s_P"%X].to_f(Kc0))
            getattr(self.fields, "PID_%s_I"%X).write(self.pid_helpers["%s_I"%X].to_f(0.0))
        else:
            Kc0 = from_q4_12(getattr(self.fields, "PID_%s_P"%X).read())

        # Do a setpoint change experiment
        getattr(self.fields, "PID_%s_TARGET"%X).write(0)
        logging.info("test_cur = %d"%test_cur)
        n = 100
        c = self._dump_pid(n, X)
        getattr(self.fields, "PID_%s_TARGET"%X).write(test_cur)
        c += self._dump_pid(n, X)

        # Experiment over, switch off target and restore motion settings
        getattr(self.fields, "PID_%s_TARGET"%X).write(0)
        self._reset_targets()
        self.fields.MODE_MOTION.write(old_mode)
        self.fields.PID_FLUX_OFFSET.write(old_flux_offset)

        # Analysis and logging of setpoint change experiment results
        # At this point we can determine system model
        y0 = sum(float(a[1]) for a in c[0:n])/float(n)
        yinf = sum(float(a[1]) for a in c[3*n//2:2*n])/float(2*n - 3*n//2) - y0
        if yinf < 0.0:
            # Wups, turned out negative...
            yinf *= -1.0
            c = [(t, -y) for t, y in c]
        yp = -100000 # Not a possible value
        tp = 0
        for tpt, ypt in c[n+1:-1]:
            if ypt < yp:
                break
            yp, tp = ypt, tpt
        yp -= y0
        # It is better to overestimate tp than under.
        tp -= c[n][0]
        tp *= 1e-9 # it was in nanoseconds, we want seconds
        D = (yp - yinf) / yinf
        B = abs((test_cur-yinf) / yinf)
        A = 1.152*D**2 - 1.607*D + 1
        r = 2*A / B
        logging.info("yinf = %g, yp = %g, tp = %g"%(yinf, yp, tp))
        k = 1.0 / (Kc0*B)
        theta = tp * (0.309 + 0.209 * math.exp(-0.61*r))
        tau1 = r*theta
        logging.info("TMC 4671 %s %s PID system model k=%g, theta=%g, tau1=%g"%(self.name, X, k, theta, tau1,))
        Kc, taui = simc(k, theta, tau1, theta)
        # Account for sampling frequency etc
        Kc *= 2.0
        Ki = 2.0*Kc/(taui*self.pwmfreq)
        logging.info("TMC 4671 %s %s PID coefficients Kc=%g, Ti=%g (Ki=%g)"%(self.name, X, Kc, taui, Ki))
        return Kc, Ki

    def _dump_pid(self, n, X):
        f = "PID_%s_ACTUAL"%X
        c = [(0,0)]*(n)
        dwell = self.printer.lookup_object('toolhead').dwell
        for i in range(n):
            cur = getattr(self.fields, f).read()
            c[i]=(monotonic_ns(), cur,)
            dwell(0.005)
        return c

    def _init_registers(self, print_time=None):
        with self.mutex:
            if print_time is None:
                print_time = self.printer.lookup_object('toolhead').get_last_move_time()
            ping = self.mcu_tmc.get_register("CHIPINFO_SI_TYPE")
            if ping != 0x34363731:
                raise self.printer.command_error(
                    "TMC 4671 not identified, identification register returned %x" % (ping,))
            ping = self.mcu_tmc.get_register("CHIPINFO_SI_VERSION")
            logging.info("TMC 4671 detected, version is 0x%x", ping)

            # Disable 6100
            if self.fields6100 is not None:
                self.mcu_tmc6100.set_register("GCONF",
                                              self.fields6100.set_field("disable", 1),
                                              print_time)
            self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
            # Set torque and current in 4671 to zero
            self.fields.PID_TORQUE_FLUX_TARGET.write(0, 0)
            self.fields.PID_VELOCITY_TARGET.write(0)
            self.fields.PID_POSITION_TARGET.write(0)
            self.fields.PWM_CHOP.write(7)
            # Send registers, 6100 first if configured then 4671
            if self.fields6100 is not None:
                for reg_name in list(self.fields6100.registers.keys()):
                    val = self.fields6100.registers[reg_name] # Val may change during loop
                    self.mcu_tmc6100.set_register(reg_name, val, print_time)
            for reg_name in list(self.fields.registers.keys()):
                if reg_name == "STATUS_FLAGS":
                    continue
                val = self.fields.registers[reg_name] # Val may change during loop
                self.mcu_tmc.set_register(reg_name, val, print_time)
            self._calibrate_adc(print_time)
            self._setup_filters()

    def _setup_filter(self, register: str, biquad_filter: BiquadFilter) -> None:
        enabled = int(biquad_filter.freq > 0)
        if not enabled:
            self.disable_biquad(register)
            return

        params = None

        logging.info(
            "Setting up biquad filter: register=%s, enabled=%s, filter=%s",
            register,
            enabled,
            biquad_filter,
        )

        freq_s = self.pwmfreq
        if register == "CONFIG_BIQUAD_X_ENABLE":
            freq_s = self.pwmfreq/(self.fields.MODE_PID_SMPL.read()+1.0)

        if biquad_filter.type == "lpf":
            params = biquad_lpf(freq_s, biquad_filter.freq, biquad_filter.slope)
        elif biquad_filter.type == "notch":
            params = biquad_notch(freq_s, biquad_filter.freq, biquad_filter.slope)
        elif biquad_filter.type == "apf":
            params = biquad_apf(freq_s, biquad_filter.freq, biquad_filter.slope)

        if enabled and params is not None:
            self.enable_biquad(register, *biquad_tmc(*params))


    def _setup_filters(self) -> None:
        for target, biquad_filter in self.biquad_filters.items():
            register = BIQUAD_FILTER_TARGETS[target]
            self._setup_filter(register, biquad_filter)

    # ------------------------------------------------------------------
    # Kinematics helpers: torque, acceleration, and SCV limits
    # ------------------------------------------------------------------

    def get_available_torque(self) -> float:
        """Return the maximum available steady-state torque (N·m).

        Uses the configured ``run_current`` from :class:`CurrentHelper` and
        the resolved ``motor_kt``.  This is the torque that can be *sustained*
        by the PI controller stack without clipping at ``PID_TORQUE_FLUX_LIMITS``.

        :returns: torque in newton-metres (N·m)
        """
        run_i = self.current_helper.get_run_current()
        if run_i <= 0 or self.motor_kt <= 0:
            return 0.0
        # TMC4671 run_current is peak phase current; Kt in profiles is typically
        # defined relative to RMS current. Scale by 1/sqrt(2) for physical torque.
        i_rms = run_i / math.sqrt(2.0)
        return i_rms * self.motor_kt

    def get_available_acceleration(self, linear: bool = False) -> float:
        """Return the maximum sustainable acceleration (rad/s² or m/s²).

        Computes ``available_torque / total_inertia`` using the same
        ``run_current`` basis as :meth:`get_available_torque`.

        If *linear* is ``True``, converts angular acceleration to linear
        acceleration via the effective pitch.  The effective pitch is derived
        from ``rotation_distance`` divided by any gear ratio, matching how
        ``jload`` is computed in :meth:`~TMC4671.__init__`.

        :param linear: if True, return m/s²; otherwise rad/s².
        :returns: acceleration value
        """
        torque = self.get_available_torque()
        if torque <= 0 or self.jmotor + self.jload <= 0:
            return 0.0

        accel_rad = torque / (self.jmotor + self.jload)

        if not linear:
            return accel_rad

        # Convert to m/s² via effective pitch
        if self.stepper is None:
            return accel_rad  # Can't compute pitch without stepper
        sd = getattr(self.stepper, 'rotation_distance', 0.0)
        if sd <= 0:
            return accel_rad

        gr_pairs = self.printer.lookup_object('configfile').getsection(
            self.stepper_name).getlists(
            'gear_ratio', (), seps=(':', ','), count=2, parser=float)
        gear_ratio = 1.0
        for n, d in gr_pairs:
            gear_ratio *= n / d

        pitch_m = sd / (1000.0 * gear_ratio)
        return accel_rad * pitch_m / (2.0 * math.pi)

    def get_scv_limits(self, entry_speed: float = 0.0,
                       junction_deviation: float = 0.0) -> dict:
        """Return Square Corner Velocity limits (kinematic and bandwidth-aware).

        Two limits are returned:

        * **kinematic** — the SCV ceiling imposed by ``junction_deviation``
          (the same value Kalico's toolhead uses to compute virtual radius at
          corners).  If ``junction_deviation`` is zero or not provided, returns
          ``None`` for this key.

        * **bandwidth** — the SCV ceiling imposed by the velocity PI loop's
          ability to track cornering force.  Based on the time constant
          :math:`\\tau = 1/(2\\pi·BW_v)` and available torque.

        Both limits are in m/s (linear) for a corner at *entry_speed*.

        :param entry_speed: target speed through the corner (m/s).
        :param junction_deviation: virtual radius deviation; uses toolhead's
            current value if zero.
        :returns: dict with keys ``kinematic`` and ``bandwidth`` (both in m/s).
        """
        # --- Kinematic limit ---
        if junction_deviation <= 0 or self.max_accel_to_decel <= 0:
            kinematic = None
        else:
            # SCV² = jd × accel / (√2 − 1)
            scv_sq = junction_deviation * self.max_accel_to_decel / (
                math.sqrt(2.0) - 1.0)
            kinematic = math.sqrt(max(scv_sq, 0.0))

        # --- Bandwidth limit ---
        if self.velocity_bandwidth <= 0 or self.jmotor + self.jload <= 0:
            bandwidth = None
        else:
            tau_v = 1.0 / (2.0 * math.pi * self.velocity_bandwidth)
            torque = self.get_available_torque()
            if torque <= 0:
                bandwidth = None
            else:
                accel_rad = torque / (self.jmotor + self.jload)

                # Effective pitch for linear conversion
                if self.stepper is not None:
                    sd = getattr(self.stepper, 'rotation_distance', 0.0)
                    if sd > 0:
                        gr_pairs = self.printer.lookup_object(
                            'configfile').getsection(
                            self.stepper_name).getlists(
                            'gear_ratio', (), seps=(':', ','), count=2,
                            parser=float)
                        gear_ratio = 1.0
                        for n, d in gr_pairs:
                            gear_ratio *= n / d
                        pitch_m = sd / (1000.0 * gear_ratio)
                    else:
                        pitch_m = 0.0
                else:
                    pitch_m = 0.0

                accel_linear = accel_rad * pitch_m / (2.0 * math.pi) \
                    if pitch_m > 0 else accel_rad

                # SCV_bandwidth ≈ entry_speed × (1 − e^(−Δt/τ_v))
                # Δt is the time spent traversing the corner arc
                scv_bw = entry_speed * (1.0 - math.exp(
                    -min(entry_speed, 2.0) / (accel_linear * tau_v + 1e-9)))
                bandwidth = max(scv_bw, 0.0)

        return {
            'kinematic': kinematic,
            'bandwidth': bandwidth,
        }

    def get_status(self, eventtime=None):
        if not self.init_done:
            return {}
        # run_current is cached; phase currents come from error_helper's
        # periodic timer callback (_query_status) which may safely do SPI reads
        res = {'run_current': self.current_helper.run_current}
        res.update(self.monitor_data)
        res.update(self.error_helper.get_status(eventtime))
        return res

    cmd_INIT_TMC_help = "Initialize TMC stepper driver registers"
    def cmd_INIT_TMC(self, gcmd):
        logging.info("INIT_TMC %s", self.name)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self._init_registers(print_time)

    cmd_TMC_TUNE_MOTION_PID_help = "Tune velocity and position PID coefficients"
    def cmd_TMC_TUNE_MOTION_PID(self, gcmd):
        v_bw = gcmd.get_float('VELOCITY_BANDWIDTH', self.velocity_bandwidth,
                              above=0.)
        p_bw = gcmd.get_float('POSITION_BANDWIDTH', self.position_bandwidth,
                              above=0.)
        l_v = gcmd.get_float('LAMBDA_V', None)
        l_p = gcmd.get_float('LAMBDA_P', None)
        I_h = gcmd.get_float('HOLDING_CURRENT', None)
        T_h = gcmd.get_float('HOLDING_TORQUE', None)
        Kt = gcmd.get_float('KT', None)
        if Kt is None and I_h is not None and T_h is not None:
            Kt = T_h / I_h

        if Kt is not None:
            l_v = l_v if l_v is not None else 100.0
            l_p = l_p if l_p is not None else 400.0
            p_v, i_v, p_p, i_p, k_v, k_p = self._tune_motion_pid(Kt, l_v, l_p)
            vel_filter_freq = round(3.0 * self.pwmfreq / l_v)
            vel_filter = BiquadFilter(
                type='lpf', freq=vel_filter_freq,
                slope=self.biquad_filters['velocity'].slope)
            self.biquad_filters['velocity'] = vel_filter
            self._setup_filter(BIQUAD_FILTER_TARGETS['velocity'], vel_filter)
            self.fields.PID_VELOCITY_P.write(
                self.pid_helpers["VELOCITY_P"].to_f(p_v))
            self.fields.PID_VELOCITY_I.write(
                self.pid_helpers["VELOCITY_I"].to_f(i_v))
            self.fields.PID_POSITION_P.write(
                self.pid_helpers["POSITION_P"].to_f(p_p))
            self.fields.PID_POSITION_I.write(
                self.pid_helpers["POSITION_I"].to_f(i_p))
            cfgname = "tmc4671 %s" % (self.name,)
            configfile = self.printer.lookup_object('configfile')
            configfile.set(cfgname, 'foc_PID_VELOCITY_P', "%.3f" % (p_v,))
            configfile.set(cfgname, 'foc_PID_VELOCITY_I', "%.3f" % (i_v,))
            configfile.set(cfgname, 'foc_PID_POSITION_P', "%.3f" % (p_p,))
            configfile.set(cfgname, 'foc_PID_POSITION_I', "%.3f" % (i_p,))
            bf = self.biquad_filters['velocity']
            configfile.set(cfgname, 'biquad_velocity_filter', bf.type)
            configfile.set(cfgname, 'biquad_velocity_frequency',
                           "%.6g" % (bf.freq,))
            configfile.set(cfgname, 'biquad_velocity_slope',
                           "%.6g" % (bf.slope,))
            msg = (
                "Motion PID %s (SIMC/lambda).\n"
                "k_v=%.5f  k_p=%.5f  KT=%.5f\n"
                "Velocity P=%.5f  I=%.5f\n"
                "Position  P=%.5f  I=%.5f\n"
                "Velocity biquad LPF set to %d Hz\n"
                "SAVE_CONFIG will write these values and restart."
                % (self.name, k_v, k_p, Kt, p_v, i_v, p_p, i_p, vel_filter_freq)
            )
        else:
            p_v, i_v, p_p, i_p = self._apply_motion_pid(v_bw, p_bw)
            msg = (
                "Motion PID %s (bandwidth).\n"
                "Velocity bandwidth=%.1f Hz  Position bandwidth=%.1f Hz\n"
                "Velocity P=%.5f  I=%.5f\n"
                "Position  P=%.5f  I=%.5f\n"
                "Velocity biquad LPF set to %d Hz\n"
                "SAVE_CONFIG will write these values and restart."
                % (self.name, v_bw, p_bw, p_v, i_v, p_p, i_p, round(v_bw))
            )

        gcmd.respond_info(msg)

    cmd_TMC_TUNE_PID_help = "Tune the current and torque PID coefficients"
    def cmd_TMC_TUNE_PID(self, gcmd):
        test_existing = gcmd.get_int('CHECK', 0)
        derate = gcmd.get_float('DERATE', 1.6)
        simc_flag = gcmd.get_int('SIMC', 0)
        current_bandwidth = gcmd.get_float('CURRENT_BANDWIDTH',
                                            self.current_bandwidth)
        flux_bandwidth = gcmd.get_float('FLUX_BANDWIDTH', self.flux_bandwidth)
        torque_bandwidth = gcmd.get_float('TORQUE_BANDWIDTH',
                                           self.torque_bandwidth)
        logging.info("TMC_TUNE_PID %s (SIMC=%d, flux_bw=%.1f, torque_bw=%.1f)",
                     self.name, simc_flag, flux_bandwidth, torque_bandwidth)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        with self.mutex:
            if simc_flag:
                P_flux, I_flux = self._tune_flux_pid(test_existing, derate,
                                                     print_time)
                P_torque, I_torque = self._tune_torque_pid(test_existing,
                                                           derate, print_time)
                self.fields.PID_FLUX_P.write(
                    self.pid_helpers["FLUX_P"].to_f(P_flux))
                self.fields.PID_FLUX_I.write(
                    self.pid_helpers["FLUX_I"].to_f(I_flux))
                self.fields.PID_TORQUE_P.write(
                    self.pid_helpers["TORQUE_P"].to_f(P_torque))
                self.fields.PID_TORQUE_I.write(
                    self.pid_helpers["TORQUE_I"].to_f(I_torque))
                cfgname = "tmc4671 %s" % (self.name,)
                configfile = self.printer.lookup_object('configfile')
                configfile.set(cfgname, 'foc_PID_FLUX_P', "%.3f" % (P_flux,))
                configfile.set(cfgname, 'foc_PID_FLUX_I', "%.3f" % (I_flux,))
                configfile.set(cfgname, 'foc_PID_TORQUE_P',
                               "%.3f" % (P_torque,))
                configfile.set(cfgname, 'foc_PID_TORQUE_I',
                               "%.3f" % (I_torque,))
            else:
                P_flux, I_flux, P_torque, I_torque = \
                    self._apply_current_pid(flux_bandwidth, torque_bandwidth)

        biquad_msg = ""
        if not simc_flag:
            biquad_msg = (
                "\n  Flux biquad LPF: %d Hz"
                "\n  Torque biquad LPF: %d Hz"
                % (round(flux_bandwidth), round(torque_bandwidth)))
        gcmd.respond_info(
            "PID %s parameters:%s\n"
            "  Flux:   Kc=%.4f Ki=%.4f\n"
            "  Torque: Kc=%.4f Ki=%.4f\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with these parameters and restart the printer."
            % (self.name, biquad_msg, P_flux, I_flux, P_torque, I_torque))

    cmd_TMC_DEBUG_MOVE_help = "Test TMC motion mode (motor must be free to move)"
    def cmd_TMC_DEBUG_MOVE(self, gcmd):
        logging.info("TMC_DEBUG_MOVE %s", self.name)
        velocity = gcmd.get_int('VELOCITY', None)
        torque = gcmd.get_int('TORQUE', None)
        pos = gcmd.get_int('POSITION', None)
        open_loop_velocity = gcmd.get_int('OPENVEL', None)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        if velocity is not None:
            self._debug_pid_motion(velocity, MotionMode.velocity_mode,
                                        "PID_VELOCITY_TARGET", print_time)
        elif torque is not None:
            self._debug_pid_motion(torque, MotionMode.torque_mode,
                                        "PID_TORQUE_TARGET", print_time)
        elif pos is not None:
            self._debug_pid_motion(pos, MotionMode.position_mode,
                                        "PID_POSITION_TARGET", print_time)
        elif open_loop_velocity is not None:
            self._debug_openloop_velocity_motion(open_loop_velocity, print_time)

    def _debug_pid_motion(self, velocity, mode, target_reg, print_time):
        with self.mutex:
            #self.fields.PWM_CHOP.write(7)
            old_mode = self.fields.MODE_MOTION.read()
            self.fields.PID_POSITION_ACTUAL.write(0)
            self.printer.lookup_object('toolhead').dwell(0.2)
            # Clear all the status flags for later reference
            self.mcu_tmc.set_register_once(reg, 0, print_time)
            limit_cur = self.fields.PID_TORQUE_FLUX_LIMITS.read()
            self.fields.PID_TORQUE_FLUX_TARGET.write(0, 0)
            getattr(self.fields, target_reg).write(0)
            self.fields.MODE_MOTION.write(mode)
            n2 = 20
            if mode == MotionMode.stopped_mode:
                v = [velocity * i // (2*n2) for i in range(n2,2*n2)] + [velocity for i in range(n2*2)]
            else:
                v = [velocity for i in range(n2,2*n2)] + [velocity for i in range(n2*2)]
            n = 500
            c = self._dump_motion(n, f=lambda x : getattr(self.fields, target_reg).write(x), v=v)
            self.fields.MODE_MOTION.write(old_mode)
            getattr(self.fields, target_reg).write(0)
            #self.fields.PWM_CHOP.write(0)
        for i in range(n):
            logging.info(",".join(map(str, c[i])))

    def _dump_motion(self, n, f=None, v=None):
        n2 = n
        if v is not None:
            n2 = len(v)+1
        iv = 0
        c = [(0,0)]*(n)
        for i in range(n):
            if f is not None and i%n2 == 0:
                f(v[i//n2])
            c[i]=(monotonic_ns()/1e9,
                  self.fields.PID_POSITION_ACTUAL.read(),
                  self.fields.PID_VELOCITY_ACTUAL.read(),
                  self.fields.PID_ERROR_PID_VELOCITY_ERROR.read(),
                  self.fields.INTERIM_PIDIN_TARGET_TORQUE.read(),
                  self.fields.PID_TORQUE_ACTUAL.read(),
                  self.fields.PID_ERROR_PID_TORQUE_ERROR.read(),
                  self.fields.PID_ERROR_PID_TORQUE_ERROR_SUM.read(),
                  self.fields.INTERIM_PIDIN_TARGET_FLUX.read(),
                  self.fields.PID_FLUX_ACTUAL.read(),
                  self.fields.PID_ERROR_PID_FLUX_ERROR.read(),
                  self.fields.PID_ERROR_PID_FLUX_ERROR_SUM.read(),
                  ":::",
                  self.fields.ADC_I0_RAW.read(),
                  self.fields.ADC_I1_RAW.read(),
                  self.fields.ADC_IUX.read(),
                  self.fields.INTERIM_PWM_UX.read(),
                  self.fields.ADC_IV.read(),
                  self.fields.INTERIM_PWM_UV.read(),
                  self.fields.ADC_IWY.read(),
                  self.fields.INTERIM_PWM_WY.read(),
                  ":::",
                  self.fields.ABN_DECODER_PHI_M.read()%65536,
                  self.fields.ABN_DECODER_PHI_E.read()%65536,
                  self.fields.HALL_PHI_M.read()%65536,
                  self.fields.HALL_PHI_E.read()%65536,
                  self.fields.PHI_E.read()%65536,
                  (self.fields.PHI_E.read()-self.fields.HALL_PHI_E.read()) % 65536,
                  (self.fields.PHI_E.read()-self.fields.ABN_DECODER_PHI_E.read()) % 65536,
                  )
            self.printer.lookup_object('toolhead').dwell(15./n)
        return c

    def _debug_openloop_velocity_motion(self, velocity, print_time):
        with self.mutex:
            self.fields.PWM_CHOP.write(7)
            self.fields.MODE_MOTION.write(MotionMode.uq_ud_ext_mode)
            limit_cur = self.fields.PID_TORQUE_FLUX_LIMITS.read()
            self.fields.UQ_UD_EXT.write(limit_cur, 0)
            old_phi_e_sel = self.fields.PHI_E_SELECTION.read()
            self.fields.PHI_E_SELECTION.write(2)
            phi_e = self.fields.PHI_E.read()
            # Clear all the status flags for later reference
            self.mcu_tmc.set_register_once(reg, 0, print_time)
            # might not stick, so write with a one-shot
            n = 500
            self.fields.OPENLOOP_VELOCITY_TARGET.write(velocity)
            self.fields.OPENLOOP_ACCELERATION.write(1000)
            c = self._dump_motion(n)
            self.fields.OPENLOOP_VELOCITY_TARGET.write(0)
            self.fields.OPENLOOP_ACCELERATION.write(0)
            self.fields.UQ_UD_EXT.write(0, 0)
            self.printer.lookup_object('toolhead').dwell(0.2)
            self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
            self.fields.PHI_E_SELECTION.write(old_phi_e_sel)
            self.fields.PWM_CHOP.write(0)
            for i in range(n):
                logging.info(",".join(map(str, c[i])))


    cmd_DUMP_TMC6100_help = "Read and display TMC6100 stepper driver registers"
    def cmd_DUMP_TMC6100(self, gcmd):
        logging.info("DUMP_TMC6100 %s", self.name)
        field_name = gcmd.get('FIELD', None)
        if field_name is not None:
            reg_name = self.fields6100.lookup_register(field_name.upper())
            if reg_name is None:
                reg_name = field_name
        else:
            reg_name = gcmd.get('REGISTER', None)
        if reg_name is not None:
            reg_name = reg_name.upper()
            if reg_name in self.read_registers:
                # readable register
                val = self.mcu_tmc6100.get_register(reg_name)
                if self.read_translate is not None:
                    reg_name, val = self.read_translate(reg_name, val)
                gcmd.respond_info(self.fields6100.pretty_format(reg_name, val))
            else:
                raise gcmd.error("Unknown register name '%s'" % (reg_name))
        else:
            group = gcmd.get('GROUP', 'Default').lower()
            if group not in DumpGroups6100:
                raise gcmd.error("Unknown group name '%s'" % (group))
            gcmd.respond_info("========== Queried registers ==========")
            for reg_name in DumpGroups6100[group]:
                val = self.mcu_tmc6100.get_register(reg_name)
                if self.read_translate is not None:
                    reg_name, val = self.read_translate(reg_name, val)
                gcmd.respond_info(self.fields6100.pretty_format(reg_name, val))

    cmd_DUMP_TMC_help = "Read and display TMC stepper driver registers"
    def cmd_DUMP_TMC(self, gcmd):
        logging.info("DUMP_TMC %s", self.name)
        field_name = gcmd.get('FIELD', None)
        if field_name is not None:
            reg_name = self.fields.lookup_register(field_name.upper())
            if reg_name is None:
                reg_name = field_name
        else:
            reg_name = gcmd.get('REGISTER', None)
        if reg_name is not None:
            reg_name = reg_name.upper()
            if reg_name in self.read_registers:
                # readable register
                val = self.mcu_tmc.get_register(reg_name)
                if self.read_translate is not None:
                    reg_name, val = self.read_translate(reg_name, val)
                gcmd.respond_info(self.fields.pretty_format(reg_name, val))
            else:
                raise gcmd.error("Unknown register name '%s'" % (reg_name))
        else:
            group = gcmd.get('GROUP', 'Default').lower()
            if group not in DumpGroups:
                raise gcmd.error("Unknown group name '%s'" % (group))
            gcmd.respond_info("========== Queried registers ==========")
            for reg_name in DumpGroups[group]:
                val = self.mcu_tmc.get_register(reg_name)
                if self.read_translate is not None:
                    reg_name, val = self.read_translate(reg_name, val)
                gcmd.respond_info(self.fields.pretty_format(reg_name, val))

    cmd_SET_TMC_FIELD_help = "Set a register field of a TMC driver"
    def cmd_SET_TMC_FIELD(self, gcmd):
        field_name = gcmd.get('FIELD').upper()
        reg_name = self.fields.lookup_register(field_name, None)
        if reg_name is None:
            raise gcmd.error("Unknown field name '%s'" % (field_name,))
        value = gcmd.get_int('VALUE', None)
        fval = gcmd.get_float('FVAL', None)
        velocity = gcmd.get_float('VELOCITY', None, minval=0.)
        if all(((value is None), (fval is None), (velocity is None))):
            reg_name = reg_name.upper()
            if reg_name in self.read_registers:
                # readable register
                val = self.mcu_tmc.get_register(reg_name)
                if self.read_translate is not None:
                    reg_name, val = self.read_translate(reg_name, val)
                gcmd.respond_info(self.fields.pretty_format(reg_name, val))
            return
        if fval is not None:
            convert = self.fields.field_setters.get(field_name)
            if convert is None:
                raise gcmd.error("FVAL parameters not supported by %s" % (field_name,))
            value = convert(fval)
        if velocity is not None:
            value = TMCtstepHelper(self.mcu_tmc, velocity,
                                   pstepper=self.stepper)
        with self.mutex:
            reg_val = self.fields.set_field(field_name, value)
            print_time = self.printer.lookup_object('toolhead').get_last_move_time()
            self.mcu_tmc.set_register(reg_name, reg_val, print_time)

    cmd_SET_TMC_CURRENT_help = "Set the current of a TMC driver"
    def cmd_SET_TMC_CURRENT(self, gcmd):
        ch = self.current_helper
        # Use cached run_current to avoid live SPI reads (get_current() triggers
        # spi_transfer which may fail in certain reactor contexts)
        prev_cur = ch.run_current
        max_cur = MAX_CURRENT
        run_current = gcmd.get_float('CURRENT', None, minval=0., maxval=max_cur)
        if run_current is not None:
            with self.mutex:
                reg_val = ch.set_current(run_current)
                prev_cur = ch.run_current
                print_time = self.printer.lookup_object('toolhead').get_last_move_time()
                self.mcu_tmc.set_register("PID_TORQUE_FLUX_LIMITS", reg_val, print_time)
        gcmd.respond_info("Run Current: %0.2fA" % (prev_cur,))

    cmd_SET_TMC_BIQUAD_FILTER_help = ("Set the cutoff frequency of one of the biquad filters")
    def cmd_SET_TMC_BIQUAD_FILTER(self, gcmd):
        biquad_target = gcmd.get("FILTER").lower()
        if biquad_target not in BIQUAD_FILTER_TARGETS.keys():
            raise gcmd.error(
                "Invalid FILTER '%s': must be one of %s"
                % (biquad_target, ", ".join(BIQUAD_FILTER_TARGETS.keys()))
            )

        current_filter = self.biquad_filters[biquad_target]

        filter_type = gcmd.get("TYPE", default=current_filter.type).lower()
        if filter_type not in BIQUAD_FILTER_TYPES:
            raise gcmd.error(
                "Invalid FILTER '%s': must be one of %s"
                % (filter_type, ", ".join(BIQUAD_FILTER_TYPES))
            )

        freq = gcmd.get_float(
            "FREQUENCY", minval=0, maxval=4 * TMC_FREQUENCY, default=current_filter.freq,
        )
        slope = gcmd.get_float("SLOPE", above=0.0, default=current_filter.slope)
        enabled = str(freq > 0)

        self.biquad_filters[biquad_target] = BiquadFilter(
            type=filter_type, freq=freq, slope=slope,
        )

        self._setup_filter(
            BIQUAD_FILTER_TARGETS[biquad_target], self.biquad_filters[biquad_target]
        )
        self.printer.lookup_object('toolhead').dwell(0.2)
        gcmd.respond_info(
            f"Configured {biquad_target} biquad filter: filter={filter_type}, "
            f"freq={freq}, slope={slope}, enabled={enabled}"
        )

    cmd_TMC_DEBUG_VOLTAGE_help = "Measure and report VM and FOC voltages (Ud, Uq)"
    def cmd_TMC_DEBUG_VOLTAGE(self, gcmd):
        vm = self._read_vm()
        
        # Read FOC voltages (target)
        reg_val = self.mcu_tmc.get_register("INTERIM_FOC_UQ_UD")
        ud_raw = reg_val & 0xFFFF
        uq_raw = (reg_val >> 16) & 0xFFFF
        ud = ud_raw if ud_raw < 32768 else ud_raw - 65536
        uq = uq_raw if uq_raw < 32768 else uq_raw - 65536
        
        # Read FOC voltages (limited)
        reg_lim_val = self.mcu_tmc.get_register("INTERIM_FOC_UQ_UD_LIMITED")
        ud_lim_raw = reg_lim_val & 0xFFFF
        uq_lim_raw = (reg_lim_val >> 16) & 0xFFFF
        ud_lim = ud_lim_raw if ud_lim_raw < 32768 else ud_lim_raw - 65536
        uq_lim = uq_lim_raw if uq_lim_raw < 32768 else uq_lim_raw - 65536

        # Read external target voltages
        reg_ext_val = self.mcu_tmc.get_register("UQ_UD_EXT")
        ud_ext_raw = reg_ext_val & 0xFFFF
        uq_ext_raw = (reg_ext_val >> 16) & 0xFFFF
        ud_ext = ud_ext_raw if ud_ext_raw < 32768 else ud_ext_raw - 65536
        uq_ext = uq_ext_raw if uq_ext_raw < 32768 else uq_ext_raw - 65536

        # Convert to Volts
        # 32768 in raw units corresponds to full VM supply voltage
        vm_ref = max(vm, 0.001)  # Avoid division by zero
        vd = (ud / 32768.0) * vm_ref
        vq = (uq / 32768.0) * vm_ref
        vd_lim = (ud_lim / 32768.0) * vm_ref
        vq_lim = (uq_lim / 32768.0) * vm_ref
        vd_ext = (ud_ext / 32768.0) * vm_ref
        vq_ext = (uq_ext / 32768.0) * vm_ref

        gcmd.respond_info(
            f"TMC 4671 '{self.name}' Voltage Debug Report:\n"
            f"  Supply Voltage (VM): {vm:.3f} V\n"
            f"  FOC Target:          Ud={ud:6d} ({vd:.3f} V) | Uq={uq:6d} ({vq:.3f} V)\n"
            f"  FOC Limited:         Ud={ud_lim:6d} ({vd_lim:.3f} V) | Uq={uq_lim:6d} ({vq_lim:.3f} V)\n"
            f"  External Target:     Ud={ud_ext:6d} ({vd_ext:.3f} V) | Uq={uq_ext:6d} ({vq_ext:.3f} V)"
        )

    cmd_TMC_DEBUG_CURRENT_help = "Measure and report FOC and phase currents"
    def cmd_TMC_DEBUG_CURRENT(self, gcmd):
        ch = self.current_helper
        
        # Read configured limits and status
        run_current = ch.run_current
        homing_current = ch.homing_current
        limit_raw = self.fields.PID_TORQUE_FLUX_LIMITS.read()
        limit_a = ch.convert_adc_current(limit_raw)
        
        # Read raw phase currents (ADC)
        iux = ch.convert_adc_current(self.fields.ADC_IUX.read())
        iv = ch.convert_adc_current(self.fields.ADC_IV.read())
        iwy = ch.convert_adc_current(self.fields.ADC_IWY.read())
        
        # Read FOC Target Currents (d/q axis)
        flux_target_raw, torque_target_raw = self.fields.PID_TORQUE_FLUX_TARGET.read()
        flux_target = ch.convert_adc_current(flux_target_raw)
        torque_target = ch.convert_adc_current(torque_target_raw)
        
        # Read FOC Actual Currents (d/q axis)
        flux_actual_raw, torque_actual_raw = self.fields.PID_TORQUE_FLUX_ACTUAL.read()
        flux_actual = ch.convert_adc_current(flux_actual_raw)
        torque_actual = ch.convert_adc_current(torque_actual_raw)
        
        # Read FOC Interim Currents
        reg_foc_val = self.mcu_tmc.get_register("INTERIM_FOC_IQ_ID")
        id_raw = reg_foc_val & 0xFFFF
        iq_raw = (reg_foc_val >> 16) & 0xFFFF
        id_foc = id_raw if id_raw < 32768 else id_raw - 65536
        iq_foc = iq_raw if iq_raw < 32768 else iq_raw - 65536
        id_foc_a = ch.convert_adc_current(id_foc)
        iq_foc_a = ch.convert_adc_current(iq_foc)

        gcmd.respond_info(
            f"TMC 4671 '{self.name}' Current Debug Report:\n"
            f"  Run Current Limit:    {run_current:.3f} A\n"
            f"  Homing Current Limit: {homing_current:.3f} A\n"
            f"  Active Current Limit:  {limit_a:.3f} A (raw: {limit_raw:d})\n"
            f"  Phase Currents:\n"
            f"    I_ux (Phase U/X):   {iux: .3f} A\n"
            f"    I_v  (Phase V):     {iv: .3f} A\n"
            f"    I_wy (Phase W/Y):   {iwy: .3f} A\n"
            f"  FOC Target Currents:\n"
            f"    Id (Flux Target):   {flux_target: .3f} A\n"
            f"    Iq (Torque Target): {torque_target: .3f} A\n"
            f"  FOC Actual Currents:\n"
            f"    Id (Flux Actual):   {flux_actual: .3f} A\n"
            f"    Iq (Torque Actual): {torque_actual: .3f} A\n"
            f"  FOC Interim (ID/IQ):\n"
            f"    Id (Interim Flux):  {id_foc_a: .3f} A (raw: {id_foc:6d})\n"
            f"    Iq (Interim Torque): {iq_foc_a: .3f} A (raw: {iq_foc:6d})"
        )

    cmd_TMC_DEBUG_MOTOR_help = "Report estimated motor parameters (resistance and inductance)"
    def cmd_TMC_DEBUG_MOTOR(self, gcmd):
        res_str = f"{self.motor_r:.4f} Ohms" if self.motor_r != 0.0 else "Not yet calibrated"
        ind_str = f"{self.motor_l:.6f} H ({self.motor_l * 1000.0:.3f} mH)" if self.motor_l != 0.0 else "Not yet calibrated"
        ld_str = f"{self.motor_ld:.6f} H ({self.motor_ld * 1000.0:.3f} mH)" if self.motor_ld != 0.0 else "Not yet calibrated / measured"
        lq_str = f"{self.motor_lq:.6f} H ({self.motor_lq * 1000.0:.3f} mH)" if self.motor_lq != 0.0 else "Not yet calibrated / measured"
        sal_str = f"{self.motor_saliency:.4f}" if self.motor_saliency != 1.0 else "Not yet calibrated / measured"

        def _biquad_str(target):
            bf = self.biquad_filters[target]
            if bf.freq == 0:
                return "disabled"
            return f"{bf.type.upper()} {bf.freq:g} Hz (slope={bf.slope:.4f})"

        gcmd.respond_info(
            f"TMC 4671 '{self.name}' Motor Debug Report:\n"
            f"  Estimated Resistance (motor_r): {res_str}\n"
            f"  Estimated Inductance (motor_l): {ind_str}\n"
            f"  Estimated Ld Inductance (motor_ld): {ld_str}\n"
            f"  Estimated Lq Inductance (motor_lq): {lq_str}\n"
            f"  Saliency Ratio (motor_saliency): {sal_str}\n"
            f"  Current Loop Filters:\n"
            f"    Flux:   {_biquad_str('flux')}\n"
            f"    Torque: {_biquad_str('torque')}"
        )

    cmd_TMC_DEBUG_TUNING_help = (
        "Report what PID tuning helpers would compute without applying changes"
    )
    def cmd_TMC_DEBUG_TUNING(self, gcmd):
        current_bandwidth = gcmd.get_float('CURRENT_BANDWIDTH', 1200.0)
        l_v = gcmd.get_float('LAMBDA_V', 100.0)
        l_p = gcmd.get_float('LAMBDA_P', 400.0)
        v_bw = gcmd.get_float('VELOCITY_BANDWIDTH', 450.0, above=0.)
        p_bw = gcmd.get_float('POSITION_BANDWIDTH', 100.0, above=0.)
        I_h = gcmd.get_float('HOLDING_CURRENT', None)
        T_h = gcmd.get_float('HOLDING_TORQUE', None)
        Kt = gcmd.get_float('KT', None)
        r_override = gcmd.get_float('R', None, minval=0.0)
        l_override = gcmd.get_float('L', None, minval=0.0)
        if Kt is None and I_h is not None and T_h is not None:
            Kt = T_h / I_h

        eff_r = r_override if r_override is not None else self.motor_r
        eff_l = l_override if l_override is not None else self.motor_l
        eff_ld = l_override if l_override is not None else (
            self.motor_ld if self.motor_ld != 0.0 else self.motor_l)
        eff_lq = l_override if l_override is not None else (
            self.motor_lq if self.motor_lq != 0.0 else self.motor_l)

        lines = ["TMC 4671 '%s' Tuning Debug Report" % self.name]

        # Motor parameters
        if eff_r == 0.0 or eff_l == 0.0:
            lines.append(
                "Motor parameters: not yet calibrated (startup alignment pending)"
            )
        else:
            r_src = " (override)" if r_override is not None else ""
            l_src = " (override)" if l_override is not None else ""
            lines.append(
                "Motor parameters: R=%.4f Ω%s  L=%.6f H (%.3f mH)%s"
                "  Ld=%.6f H (%.3f mH)  Lq=%.6f H (%.3f mH)"
                % (eff_r, r_src, eff_l, eff_l * 1000.0, l_src,
                   eff_ld, eff_ld * 1000.0, eff_lq, eff_lq * 1000.0)
            )

        # --- Current PID ---
        lines.append("")
        lines.append(
            "--- Current PID (bandwidth method, CURRENT_BANDWIDTH=%.1f Hz) ---"
            % current_bandwidth
        )
        if eff_r == 0.0 or eff_l == 0.0:
            lines.append("  Cannot compute: motor parameters not yet calibrated")
        else:
            P_flux_new, I_flux_new = self._tune_current_pid(
                current_bandwidth, motor_r=eff_r, motor_l=eff_ld
            )
            P_torq_new, I_torq_new = self._tune_current_pid(
                current_bandwidth, motor_r=eff_r, motor_l=eff_lq
            )
            P_flux_cur = self.pid_helpers["FLUX_P"].from_f(
                self.fields.PID_FLUX_P.read()
            )
            I_flux_cur = self.pid_helpers["FLUX_I"].from_f(
                self.fields.PID_FLUX_I.read()
            )
            P_torq_cur = self.pid_helpers["TORQUE_P"].from_f(
                self.fields.PID_TORQUE_P.read()
            )
            I_torq_cur = self.pid_helpers["TORQUE_I"].from_f(
                self.fields.PID_TORQUE_I.read()
            )
            lines.append(
                "  Computed:  Flux   P=%.4f  I=%.4f" % (P_flux_new, I_flux_new)
            )
            lines.append(
                "             Torque P=%.4f  I=%.4f" % (P_torq_new, I_torq_new)
            )
            lines.append(
                "  Active:    Flux   P=%.4f  I=%.4f" % (P_flux_cur, I_flux_cur)
            )
            lines.append(
                "             Torque P=%.4f  I=%.4f" % (P_torq_cur, I_torq_cur)
            )

        # --- Motion PID ---
        lines.append("")
        lines.append(
            "--- Motion PID (LAMBDA_V=%.1f  LAMBDA_P=%.1f) ---" % (l_v, l_p)
        )
        if Kt is None:
            lines.append(
                "  Supply KT or both HOLDING_CURRENT and HOLDING_TORQUE to compute"
            )
        else:
            lines.append("  KT=%.5f Nm/A" % Kt)
            p_v_new, i_v_new, p_p_new, i_p_new, k_v, k_p = self._tune_motion_pid(
                Kt, l_v, l_p
            )
            p_v_cur = self.pid_helpers["VELOCITY_P"].from_f(
                self.fields.PID_VELOCITY_P.read()
            )
            i_v_cur = self.pid_helpers["VELOCITY_I"].from_f(
                self.fields.PID_VELOCITY_I.read()
            )
            p_p_cur = self.pid_helpers["POSITION_P"].from_f(
                self.fields.PID_POSITION_P.read()
            )
            i_p_cur = self.pid_helpers["POSITION_I"].from_f(
                self.fields.PID_POSITION_I.read()
            )
            lines.append(
                "  Computed:  Velocity P=%.5f  I=%.5f" % (p_v_new, i_v_new)
            )
            lines.append(
                "             Position  P=%.5f  I=%.5f" % (p_p_new, i_p_new)
            )
            lines.append(
                "  Active:    Velocity P=%.5f  I=%.5f" % (p_v_cur, i_v_cur)
            )
            lines.append(
                "             Position  P=%.5f  I=%.5f" % (p_p_cur, i_p_cur)
            )
            lines.append(
                "  Suggested filter frequency: %d Hz"
                % round(3.0 * self.pwmfreq / l_v)
            )

        lines.append("")
        lines.append(
            "--- Motion PID (bandwidth, VELOCITY_BANDWIDTH=%.1f Hz"
            "  POSITION_BANDWIDTH=%.1f Hz) ---" % (v_bw, p_bw)
        )
        p_v_bw, i_v_bw = self._calc_velocity_pid(v_bw)
        p_p_bw = self._calc_position_pid(p_bw)
        p_v_cur = self.pid_helpers["VELOCITY_P"].from_f(
            self.fields.PID_VELOCITY_P.read()
        )
        i_v_cur = self.pid_helpers["VELOCITY_I"].from_f(
            self.fields.PID_VELOCITY_I.read()
        )
        p_p_cur = self.pid_helpers["POSITION_P"].from_f(
            self.fields.PID_POSITION_P.read()
        )
        i_p_cur = self.pid_helpers["POSITION_I"].from_f(
            self.fields.PID_POSITION_I.read()
        )
        lines.append(
            "  Computed:  Velocity P=%.5f  I=%.5f" % (p_v_bw, i_v_bw)
        )
        lines.append(
            "             Position  P=%.5f  I=0.00000" % (p_p_bw,)
        )
        lines.append(
            "  Active:    Velocity P=%.5f  I=%.5f" % (p_v_cur, i_v_cur)
        )
        lines.append(
            "             Position  P=%.5f  I=%.5f" % (p_p_cur, i_p_cur)
        )


        # --- Kinematics & Motion Limits ---
        lines.append("")
        lines.append("--- Kinematics & Motion Limits ---")

        torq = self.get_available_torque()
        accel_rad = self.get_available_acceleration()
        accel_lin = self.get_available_acceleration(True)
        
        if torq > 0:
            lines.append(
                f"  Max available torque: {torq:.4f} N·m "
                f"(I_peak={self.current_helper.get_run_current():.2f}A, "
                f"I_RMS={self.current_helper.get_run_current()/math.sqrt(2):.2f}A, "
                f"Kt={self.motor_kt:.4f})"
            )
            lines.append(
                f"  Max sustainable acceleration: {accel_rad:.1f} rad/s² / {accel_lin * 1000.0:.1f} mm/s² "
                f"(J_motor={self.jmotor:.2e}, J_load={self.jload:.2e})"
            )
        else:
            lines.append("  Kinematics data unavailable (motor not calibrated or current zero)")

        # Calculate and report SCV limits from toolhead state
        try:
            th = self.printer.lookup_object('toolhead')
            jd = getattr(th, 'junction_deviation', 0.0)
            scv_cfg = getattr(th, 'square_corner_velocity', 5.0)

            if hasattr(self, 'max_accel_to_decel') and self.max_accel_to_decel > 0 and jd > 0:
                # Kinematic limit from junction deviation: SCV² = jd × accel / (√2 − 1)
                scv_kin_lim = math.sqrt(jd * self.max_accel_to_decel / (math.sqrt(2.0) - 1.0))
                lines.append(f"  SCV kinematic limit: {scv_kin_lim:.3f} mm/s (from jd={jd:.3f})")

            if self.velocity_bandwidth > 0 and torq > 0:
                tau_v = 1.0 / (2.0 * math.pi * self.velocity_bandwidth)

                # Get effective pitch for linear conversion
                pitch_m = 0.0
                if hasattr(self, 'stepper') and self.stepper is not None:
                    sd = getattr(self.stepper, 'rotation_distance', 0.0)
                    if sd > 0:
                        gr_pairs = self.printer.lookup_object('configfile').getsection(
                            self.stepper_name).getlists(
                            'gear_ratio', (), seps=(':', ','), count=2, parser=float)
                        gear_ratio = 1.0
                        for n, d in gr_pairs:
                            gear_ratio *= n / d
                        pitch_m = sd / (1000.0 * gear_ratio)

                if pitch_m > 0:
                    accel_lin_scv = torq / (self.jmotor + self.jload) * pitch_m / (2.0 * math.pi)
                else:
                    accel_lin_scv = torq / (self.jmotor + self.jload)

                # Bandwidth-limited SCV: motor can only reach a fraction of config limit in the time available
                # Using exponential response model: Δv = V_max × (1 − e^(−t/τ))
                t_corner = 2.0 * scv_cfg / (accel_lin_scv + 1e-9)  # estimated cornering time
                fraction_reached = 1.0 - math.exp(-t_corner / tau_v)
                scv_bw_lim = min(scv_cfg, scv_cfg * fraction_reached)
                lines.append(f"  SCV bandwidth limit: {scv_bw_lim:.3f} mm/s (BW_v={self.velocity_bandwidth:.1f} Hz, τ_v={tau_v*1000:.1f}ms)")
            else:
                lines.append("  SCV bandwidth limit: unavailable (velocity_bw=0 or torque=0)")

        except Exception as e:
            lines.append(f"  SCV limits: toolhead state unavailable ({e})")

        gcmd.respond_info("\n".join(lines))

    def _calculate_ac_injection_voltage(self, target_current=None):
        if target_current is None:
            target_current = self.current_helper.run_current * 0.25
        V_req = (target_current * self.motor_r * 2.0) + 1.2
        vm = self._read_vm()
        if self.fields.MOTOR_TYPE.read() == 3:
            v_max_phase = vm / math.sqrt(3.0)
        else:
            v_max_phase = vm
        
        if V_req > v_max_phase:
            ac_U = 32767
        else:
            ac_U = int(32767.0 * (V_req / v_max_phase))
        ac_U = max(ac_U, 500)
        v_applied = ac_U * v_max_phase / 32767.0
        v_ac = max(0.01, v_applied - self.dead_time_v)
        return ac_U, v_applied, v_ac

    def _measure_impedance_dc_baseline(self, dwell, n_dc_samples=100):
        # Helper function for variance
        def calculate_variance(data):
            if len(data) < 2:
                return 0.0
            mu = sum(data) / len(data)
            return sum((x - mu) ** 2 for x in data) / (len(data) - 1)

        # Allow mechanical/electrical settling for DC alignment
        dwell(0.5)
        
        # Phase 1: Pure register acquisition pass (minimized latency inside loop)
        reg_vals = []
        for _ in range(n_dc_samples):
            reg_vals.append(self.mcu_tmc.get_register("PID_TORQUE_FLUX_ACTUAL"))
            dwell(0.001)

        # Phase 2: Post-processing DSP mathematical calculation pass
        dc_mags = []
        convert_adc = self.current_helper.convert_adc_current
        for reg_val in reg_vals:
            flux_raw = reg_val & 0xffff
            if flux_raw >= 32768:
                flux_raw -= 65536
            torque_raw = (reg_val >> 16) & 0xffff
            if torque_raw >= 32768:
                torque_raw -= 65536
            
            id = convert_adc(flux_raw)
            iq = convert_adc(torque_raw)
            dc_mags.append(math.sqrt(id**2 + iq**2))
            
        I_dc_avg = sum(dc_mags) / len(dc_mags) if dc_mags else 0.0
        var_noise = calculate_variance(dc_mags)
        return I_dc_avg, var_noise

    def _acquire_impedance_ac_samples(self, f_inject, n_samples, ac_U, dwell):
        # Configure and Start High-Frequency AC Injection
        dds_value = int(f_inject * (2**32) / self.pwmfreq)
        self.fields.OPENLOOP_ACCELERATION.write(dds_value)
        self.fields.OPENLOOP_VELOCITY_TARGET.write(dds_value)
        
        # Allow electrical settling for the rotating field
        dwell(0.5)
        
        # Phase 1: Stochastic real-time physical acquisition pass
        raw_samples = []
        t_start = time.time()
        for _ in range(n_samples):
            t0 = time.time()
            reg_val = self.mcu_tmc.get_register("PID_TORQUE_FLUX_ACTUAL")
            t1 = time.time()
            raw_samples.append((reg_val, t0, t1))
            dwell(0.001)  # Jitter allows equivalent time sampling
            
        # Phase 2: Post-processing DSP mathematical calculation pass
        ac_samples = []
        convert_adc = self.current_helper.convert_adc_current
        for reg_val, t0, t1 in raw_samples:
            flux_raw = reg_val & 0xffff
            if flux_raw >= 32768:
                flux_raw -= 65536
            torque_raw = (reg_val >> 16) & 0xffff
            if torque_raw >= 32768:
                torque_raw -= 65536
            
            id = convert_adc(flux_raw)
            iq = convert_adc(torque_raw)
            
            mag = math.sqrt(id**2 + iq**2)
            t_mid = (t0 + t1) / 2.0 - t_start
            ac_samples.append((mag, t_mid))
            
        return ac_samples

    def _calculate_axis_inductances(self, I_avg, I_ripple, V_ac_eff, omega_inject, motor_r):
        I_max = I_avg + I_ripple
        I_min = max(1e-6, I_avg - I_ripple)
        Ld = math.sqrt(max(0.0, (V_ac_eff / I_max)**2 - motor_r**2)) / omega_inject
        Lq = math.sqrt(max(0.0, (V_ac_eff / I_min)**2 - motor_r**2)) / omega_inject
        saliency = Lq / Ld if Ld > 1e-9 else 1.0
        return Ld, Lq, saliency

    def _calculate_impedance_method_a(self, ac_mags, var_noise, I_avg, V_ac_eff, omega_inject, motor_r):
        def calculate_variance(data):
            if len(data) < 2:
                return 0.0
            mu = sum(data) / len(data)
            return sum((x - mu) ** 2 for x in data) / (len(data) - 1)
        
        var_total = calculate_variance(ac_mags)
        var_ripple = max(0.0, var_total - var_noise)
        I_ripple_stdev = math.sqrt(2.0 * var_ripple)
        Ld, Lq, saliency = self._calculate_axis_inductances(
            I_avg, I_ripple_stdev, V_ac_eff, omega_inject, motor_r
        )
        return I_ripple_stdev, Ld, Lq, saliency

    def _calculate_impedance_method_b(self, ac_samples, I_avg, f_inject, V_ac_eff, omega_inject, motor_r):
        ac_mags = [mag for mag, _ in ac_samples]
        y_vals = [mag - I_avg for mag in ac_mags]
        omega_ripple = 4.0 * math.pi * f_inject
        
        S_cc = sum(math.cos(omega_ripple * t)**2 for _, t in ac_samples)
        S_ss = sum(math.sin(omega_ripple * t)**2 for _, t in ac_samples)
        S_cs = sum(math.cos(omega_ripple * t) * math.sin(omega_ripple * t) for _, t in ac_samples)
        S_yc = sum(y * math.cos(omega_ripple * t) for y, (_, t) in zip(y_vals, ac_samples))
        S_ys = sum(y * math.sin(omega_ripple * t) for y, (_, t) in zip(y_vals, ac_samples))
        
        det = S_cc * S_ss - S_cs**2
        if det > 1e-12:
            A_fit = (S_yc * S_ss - S_ys * S_cs) / det
            B_fit = (S_ys * S_cc - S_yc * S_cs) / det
        else:
            A_fit, B_fit = 0.0, 0.0
        I_ripple_fit = math.sqrt(A_fit**2 + B_fit**2)
        Ld, Lq, saliency = self._calculate_axis_inductances(
            I_avg, I_ripple_fit, V_ac_eff, omega_inject, motor_r
        )
        return I_ripple_fit, Ld, Lq, saliency

    cmd_TMC_MEASURE_IMPEDANCE_help = (
        "Measure motor d/q axis inductances (Ld, Lq) and saliency ratio"
    )
    def cmd_TMC_MEASURE_IMPEDANCE(self, gcmd):
        f_inject = gcmd.get_float('F_INJECT', 2317.0, minval=1.0)
        n_samples = gcmd.get_int('N_SAMPLES', 500, minval=10)
        
        toolhead = self.printer.lookup_object('toolhead')
        enable_line = self.stepper_enable.lookup_enable(self.stepper_name)
        
        with self.mutex:
            print_time = toolhead.get_last_move_time()
            dwell = toolhead.dwell
            old_phi_e_selection = self.fields.PHI_E_SELECTION.read()
            old_mode_motion = self.fields.MODE_MOTION.read()
            
            # Enable motor hardware & gate driver (vital to allow current flow)
            if self.fields6100 is not None:
                self.mcu_tmc6100.set_register("GCONF",
                                              self.fields6100.set_field("disable", 0),
                                              print_time)
            enable_line.motor_enable(print_time)
            
            # 2. Disable biquads to prevent attenuation
            for register in BIQUAD_FILTER_TARGETS.values():
                self.disable_biquad(register)
                
            try:
                if not self.motor_r or self.motor_r < 1e-3:
                    self._align_and_measure(False, print_time)
                    for register in BIQUAD_FILTER_TARGETS.values():
                        self.disable_biquad(register)

                # 3. Calculate safe AC Voltage Amplitude (V_ac)
                ac_U, v_applied, v_ac = self._calculate_ac_injection_voltage()
                
                # 4. Configure TMC4671 for DC Static Bias (Rotor Alignment & Noise Calibration)
                # Use PHI_E_SELECTION=1 (external angle locked at PHI_E_EXT=0) rather than
                # open-loop DDS mode.  The DDS updates OPENLOOP_VELOCITY_ACTUAL every PWM
                # cycle and ignores host writes when ACCELERATION=0, so OPENLOOP_PHI keeps
                # spinning at the injection frequency from a previous call.  A fixed external
                # angle is completely immune to that state.
                self.fields.PWM_CHOP.write(7)
                self.fields.PHI_E_SELECTION.write(1)
                self.fields.PHI_E_EXT.write(0)
                self.fields.UQ_EXT.write(0)
                self.fields.UD_EXT.write(ac_U)
                self.fields.MODE_MOTION.write(MotionMode.uq_ud_ext_mode)
                
                # Sample baseline DC/Noise currents
                I_dc_avg, var_noise = self._measure_impedance_dc_baseline(dwell, 100)

                # 5. Switch to open-loop DDS mode for AC injection
                self.fields.OPENLOOP_VELOCITY_TARGET.write(0)
                self.fields.OPENLOOP_ACCELERATION.write(0)
                self.fields.OPENLOOP_VELOCITY_ACTUAL.write(0)
                self.fields.PHI_E_SELECTION.write(2)

                # 6. Configure and Start High-Frequency AC Injection
                # 7. Stochastic AC/Saliency Polling Loop
                ac_samples = self._acquire_impedance_ac_samples(f_inject, n_samples, ac_U, dwell)
                
                # 7. Disable injection immediately
                self.fields.UD_EXT.write(0)
                self.fields.MODE_MOTION.write(MotionMode.stopped_mode)
                
                # =================================================================
                # 8. DSP & Extraction Algorithms
                # =================================================================
                ac_mags = [mag for mag, _ in ac_samples]
                I_avg = sum(ac_mags) / len(ac_mags)
                omega_inject = 2.0 * math.pi * f_inject
                # Derive effective AC voltage from the DC baseline measurement at the same
                # ac_U amplitude (V = I*R at DC, pure resistive), mirroring the startup path.
                # This avoids the circular dependency on the previously stored self.motor_l.
                V_ac_eff = I_dc_avg * self.motor_r
                if I_avg > 1e-6 and V_ac_eff > 1e-6:
                    Z_sq = (V_ac_eff / I_avg) ** 2
                    R_sq = self.motor_r ** 2
                    if Z_sq > R_sq:
                        self.motor_l = math.sqrt(Z_sq - R_sq) / omega_inject
                
                # --- Method A ---
                I_ripple_stdev, Ld_stdev, Lq_stdev, sal_stdev = self._calculate_impedance_method_a(
                    ac_mags, var_noise, I_avg, V_ac_eff, omega_inject, self.motor_r
                )
                
                # --- Method B ---
                I_ripple_fit, Ld_fit, Lq_fit, sal_fit = self._calculate_impedance_method_b(
                    ac_samples, I_avg, f_inject, V_ac_eff, omega_inject, self.motor_r
                )
                self.motor_ld = Ld_fit
                self.motor_lq = Lq_fit
                self.motor_saliency = sal_fit
                
                # Report Results
                lines = [
                    f"TMC4671 '{self.name}' Robust Saliency Measurement Results:",
                    f"  R (measured): {self.motor_r:.4f} Ohm",
                    f"  L_avg (baseline): {self.motor_l * 1000.0:.3f} mH",
                    f"  V_ac (nominal applied): {v_ac:.4f} V (ac_U={ac_U}, V_applied={v_applied:.4f}V, V_dead={self.dead_time_v:.4f}V)",
                    f"  V_ac_effective (calibrated): {V_ac_eff:.4f} V",
                    f"  DC Bias Current: {I_dc_avg:.4f} A",
                    f"  DC Background Noise (stdev): {math.sqrt(var_noise):.4f} A",
                    f"  AC Average Current: {I_avg:.4f} A",
                    "",
                    "  [Method A] Noise-Calibrated Standard Deviation:",
                    f"    I_ripple: {I_ripple_stdev * 1000.0:.2f} mA",
                    f"    Extracted Ld: {Ld_stdev * 1000.0:.3f} mH",
                    f"    Extracted Lq: {Lq_stdev * 1000.0:.3f} mH",
                    f"    Saliency Ratio (Lq/Ld): {sal_stdev:.3f}",
                    "",
                    "  [Method B] Least-Squares Sine Fit (Targeted Lomb-Scargle) (Recommended):",
                    f"    I_ripple: {I_ripple_fit * 1000.0:.2f} mA",
                    f"    Extracted Ld: {Ld_fit * 1000.0:.3f} mH",
                    f"    Extracted Lq: {Lq_fit * 1000.0:.3f} mH",
                    f"    Saliency Ratio (Lq/Ld): {sal_fit:.3f}"
                ]
                gcmd.respond_info("\n".join(lines))
                
            finally:
                # 9. Restore initial state
                self.fields.UQ_UD_EXT.write(0, 0)
                self.fields.OPENLOOP_VELOCITY_TARGET.write(0)
                self.fields.OPENLOOP_ACCELERATION.write(0)
                self.fields.OPENLOOP_VELOCITY_ACTUAL.write(0)
                self.fields.PHI_E_SELECTION.write(old_phi_e_selection)
                self._setup_filters()
                
                # Disable motor hardware & gate driver to return to safe idle state
                print_time = toolhead.get_last_move_time()
                enable_line.motor_disable(print_time)

def load_config_prefix(config):
    return TMC4671(config)
