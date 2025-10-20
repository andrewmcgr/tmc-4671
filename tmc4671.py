# TMC4671 servo driver support
#
# Copyright (C) 2024       Andrew McGregor <andrewmcgr@gmail.com>
#
# Based heavily on Klipper TMC stepper drivers which are:
#
# Copyright (C) 2018-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging, collections
import math
from time import monotonic_ns
from enum import IntEnum
from typing import NamedTuple
from statistics import median_low, mean
from extras import bus, tmc, thermistor

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

class BiquadFilter(NamedTuple):
    type: str
    freq: int
    slope: float

# Tuple is the address followed by a value to put in the next higher address
# to select that sub-register, or none to just go straight there.
# Not used for 6100, but there to use the same code.

######################################################################
# Register map for the 6100 companion chip
######################################################################


Registers6100 = {
    "GCONF": (0x00, None),
    "GSTAT": (0x01, None),
    "IOIN": (0x04, None),
    "SHORT_CONF": (0x09, None),
    "DRV_CONF": (0x0A, None)
}

Fields6100 = {}

Fields6100["GCONF"] = {
    "disable": 0x1, "singleline": 0x1 << 1,
    "faultdirect": 0x1 << 2, "normal": 0x1 <<6,
}

Fields6100["GSTAT"] = {
    "reset": 0x01,
    "drv_otpw": 0x01 << 1,
    "drv_ot": 0x01 << 2,
    "uv_cp": 0x01 << 3,
    "shortdet_u": 0x01 << 4,
    "s2gu": 0x01 << 5,
    "s2vsu": 0x01 << 6,
    "shortdet_u": 0x01 << 8,
    "s2gu": 0x01 << 9,
    "s2vsu": 0x01 << 10,
    "shortdet_u": 0x01 << 12,
    "s2gu": 0x01 << 13,
    "s2vsu": 0x01 << 14,
}

Fields6100["IOIN"] = {
    "UL": 0x01,
    "UH": 0x01 << 1,
    "VL": 0x01 << 2,
    "VH": 0x01 << 3,
    "WL": 0x01 << 4,
    "WH": 0x01 << 5,
    "DRV_EN": 0x01 << 6,
    "OTPW": 0x01 << 8,
    "OT136C": 0x01 << 9,
    "OT143C": 0x01 << 10,
    "OT150C": 0x01 << 11,
    "VERSION": 0xFF << 24,
}

# TODO: SHORT_CONF (defaults are reasonable)

Fields6100["DRV_CONF"] = {
    "BBMCLKS": 0x0F,
    "OTSELECT": 0x03 << 16,
    "DRVSTRENGTH": 0x03 << 19,
}

DumpGroups6100 = {
    "Default": ["GCONF", "GSTAT", "IOIN", "SHORT_CONF", "DRV_CONF",],
}


######################################################################
# Register map for the 4671
######################################################################


Registers = {
    "CHIPINFO_DATA": (0x00, None), # R,Test
    "CHIPINFO_ADDR": (0x01, None), # RW,Test

    "CHIPINFO_SI_TYPE": (0x00, 0),
    "CHIPINFO_SI_VERSION": (0x00, 1),
    "CHIPINFO_SI_DATE": (0x00, 2),
    "CHIPINFO_SI_TIME": (0x00, 3),
    "CHIPINFO_SI_VARIANT": (0x00, 4),
    "CHIPINFO_SI_BUILD": (0x00, 5),

    "ADC_RAW_DATA": (0x02, None), # R,Monitor
    "ADC_RAW_ADDR": (0x03, None), # RW,Monitor

    "ADC_I1_RAW_ADC_I0_RAW": (0x02, 0),
    "ADC_AGPI_A_RAW_ADC_VM_RAW": (0x02, 1),
    "ADC_AENC_UX_RAW_ADC_AGPI_B_RAW": (0x02, 2),
    "ADC_AENC_WY_RAW_ADC_AENC_VN_RAW": (0x02, 3),

    "DSADC_MCFG_B_MCFG_A": (0x04, None), # RW,Init
    "DSADC_MCLK_A": (0x05, None), # RW,Init
    "DSADC_MCLK_B": (0x06, None), # RW,Init
    "DSADC_MDEC_B_MDEC_A": (0x07, None), # RW,Init
    "ADC_I1_SCALE_OFFSET": (0x08, None), # RW,Init
    "ADC_I0_SCALE_OFFSET": (0x09, None), # RW,Init
    "ADC_I_SELECT": (0x0A, None), # RW,Init
    "ADC_I1_I0_EXT": (0x0B, None), # RW,Test
    "DS_ANALOG_INPUT_STAGE_CFG": (0x0C, None), # RW,Test

    "AENC_0_SCALE_OFFSET": (0x0D, None), # RW,Init
    "AENC_1_SCALE_OFFSET": (0x0E, None), # RW,Init
    "AENC_2_SCALE_OFFSET": (0x0F, None), # RW,Init
    "AENC_SELECT": (0x11, None), # RW,Init
    "ADC_IWY_IUX": (0x12, None), # R,Monitor
    "ADC_IV": (0x13, None), # R,Monitor
    "AENC_WY_UX": (0x15, None), # R,Monitor
    "AENC_VN": (0x16, None), # R,Monitor

    "PWM_POLARITIES": (0x17, None), # RW,Init
    "PWM_MAXCNT": (0x18, None), # RW,Init
    "PWM_BBM_H_BBM_L": (0x19, None), # RW,Init
    "PWM_SV_CHOP": (0x1A, None), # RW,Init
    "MOTOR_TYPE_N_POLE_PAIRS": (0x1B, None), # RW,Init
    "PHI_E_EXT": (0x1C, None), # RW,Test

    "OPENLOOP_MODE": (0x1F, None), # RW,Init
    "OPENLOOP_ACCELERATION": (0x20, None), # RW,Init
    "OPENLOOP_VELOCITY_TARGET": (0x21, None), # RW,Init
    "OPENLOOP_VELOCITY_ACTUAL": (0x22, None), # RW,Monitor
    "OPENLOOP_PHI": (0x23, None), # RW,Monitor/Test

    "UQ_UD_EXT": (0x24, None), # RW,Init/Test

    "ABN_DECODER_MODE": (0x25, None), # RW,Init
    "ABN_DECODER_PPR": (0x26, None), # RW,Init
    "ABN_DECODER_COUNT": (0x27, None), # RW,Init/Test/Monitor
    "ABN_DECODER_COUNT_N": (0x28, None), # RW,Init/Test/Monitor
    "ABN_DECODER_PHI_E_PHI_M_OFFSET": (0x29, None), # RW,Init
    "ABN_DECODER_PHI_E_PHI_M": (0x2A, None), # R,Monitor
    "ABN_2_DECODER_MODE": (0x2C, None), # RW,Init
    "ABN_2_DECODER_PPR": (0x2D, None), # RW,Init
    "ABN_2_DECODER_COUNT": (0x2E, None), # RW,Init/Test/Monitor
    "ABN_2_DECODER_COUNT_N": (0x2F, None), # RW,Init/Test/Monitor
    "ABN_2_DECODER_PHI_M_OFFSET": (0x30, None), # RW,Init
    "ABN_2_DECODER_PHI_M": (0x31, None), # R,Monitor
    "HALL_MODE": (0x33, None), # RW,Init
    "HALL_POSITION_060_000": (0x34, None), # RW,Init
    "HALL_POSITION_180_120": (0x35, None), # RW,Init
    "HALL_POSITION_300_240": (0x36, None), # RW,Init
    "HALL_PHI_E_PHI_M_OFFSET": (0x37, None), # RW,Init
    "HALL_DPHI_MAX": (0x38, None), # RW,Init
    "HALL_PHI_E_INTERPOLATED_PHI_E": (0x39, None), # R,Monitor
    "HALL_PHI_M": (0x3A, None), # R,Monitor
    "AENC_DECODER_MODE": (0x3B, None), # RW,Init
    "AENC_DECODER_N_THRESHOLD": (0x3C, None), # RW,Init
    "AENC_DECODER_PHI_A_RAW": (0x3D, None), # R,Monitor
    "AENC_DECODER_PHI_A_OFFSET": (0x3E, None), # RW,Init
    "AENC_DECODER_PHI_A": (0x3F, None), # R,Monitor
    "AENC_DECODER_PPR": (0x40, None), # RW,Init
    "AENC_DECODER_COUNT": (0x41, None), # RW,Monitor
    "AENC_DECODER_COUNT_N": (0x42, None), # RW,Monitor/Init
    "AENC_DECODER_PHI_E_PHI_M_OFFSET": (0x45, None), # RW,Init
    "AENC_DECODER_PHI_E_PHI_M": (0x46, None), # R,Monitor

    "CONFIG_DATA": (0x4D, None), # RW,Init
    "CONFIG_ADDR": (0x4E, None), # RW,Init

    "CONFIG_BIQUAD_X_A_1": (0x4D, 1),
    "CONFIG_BIQUAD_X_A_2": (0x4D, 2),
    "CONFIG_BIQUAD_X_B_0": (0x4D, 4),
    "CONFIG_BIQUAD_X_B_1": (0x4D, 5),
    "CONFIG_BIQUAD_X_B_2": (0x4D, 6),
    "CONFIG_BIQUAD_X_ENABLE": (0x4D, 7),
    "CONFIG_BIQUAD_V_A_1": (0x4D, 9),
    "CONFIG_BIQUAD_V_A_2": (0x4D, 10),
    "CONFIG_BIQUAD_V_B_0": (0x4D, 12),
    "CONFIG_BIQUAD_V_B_1": (0x4D, 13),
    "CONFIG_BIQUAD_V_B_2": (0x4D, 14),
    "CONFIG_BIQUAD_V_ENABLE": (0x4D, 15),
    "CONFIG_BIQUAD_T_A_1": (0x4D, 17),
    "CONFIG_BIQUAD_T_A_2": (0x4D, 18),
    "CONFIG_BIQUAD_T_B_0": (0x4D, 20),
    "CONFIG_BIQUAD_T_B_1": (0x4D, 21),
    "CONFIG_BIQUAD_T_B_2": (0x4D, 22),
    "CONFIG_BIQUAD_T_ENABLE": (0x4D, 23),
    "CONFIG_BIQUAD_F_A_1": (0x4D, 25),
    "CONFIG_BIQUAD_F_A_2": (0x4D, 26),
    "CONFIG_BIQUAD_F_B_0": (0x4D, 28),
    "CONFIG_BIQUAD_F_B_1": (0x4D, 29),
    "CONFIG_BIQUAD_F_B_2": (0x4D, 30),
    "CONFIG_BIQUAD_F_ENABLE": (0x4D, 31),

    "FEED_FORWARD_VELOCITY_GAIN": (0x4D, 40),
    "FEED_FORWARD_VELOCITY_FILTER_CONSTANT": (0x4D, 41),
    "FEED_FORWARD_TORQUE_GAIN": (0x4D, 42),
    "FEED_FORWARD_TORQUE_FILTER_CONSTANT": (0x4D, 43),

    "CONFIG_REF_SWITCH_CONFIG": (0x4D, 51),
    "CONFIG_SINGLE_PIN_IF_STATUS_CFG": (0x4D, 60),
    "CONFIG_SINGLE_PIN_IF_SCALE_OFFSET": (0x4D, 61),

    "CONFIG_ADVANCED_PI_REPRESENT": (0x4D, 62),
    "VELOCITY_SELECTION": (0x50, None), # RW,Init
    "POSITION_SELECTION": (0x51, None), # RW,Init
    "PHI_E_SELECTION": (0x52, None), # RW,Init
    "PHI_E": (0x53, None), # R,Monitor
    "PID_FLUX_P_FLUX_I": (0x54, None), # RW,Init
    "PID_TORQUE_P_TORQUE_I": (0x56, None), # RW,Init
    "PID_VELOCITY_P_VELOCITY_I": (0x58, None), # RW,Init
    "PID_POSITION_P_POSITION_I": (0x5A, None), # RW,Init
    "PIDOUT_UQ_UD_LIMITS": (0x5D, None), # RW,Init
    "PID_TORQUE_FLUX_LIMITS": (0x5E, None), # RW,Init
    "PID_VELOCITY_LIMIT": (0x60, None), # RW,Init
    "PID_POSITION_LIMIT_LOW": (0x61, None), # RW,Init
    "PID_POSITION_LIMIT_HIGH": (0x62, None), # RW,Init
    "MODE_RAMP_MODE_MOTION": (0x63, None), # RW,Init
    "PID_TORQUE_FLUX_TARGET": (0x64, None), # RW,Control
    "PID_TORQUE_FLUX_OFFSET": (0x65, None), # RW,Control
    "PID_VELOCITY_TARGET": (0x66, None), # RW,Control
    "PID_VELOCITY_OFFSET": (0x67, None), # RW,Control
    "PID_POSITION_TARGET": (0x68, None), # RW,Control
    "PID_TORQUE_FLUX_ACTUAL": (0x69, None), # R,Monitor
    "PID_VELOCITY_ACTUAL": (0x6A, None), # R,Monitor
    "PID_POSITION_ACTUAL": (0x6B, None), # RW,Monitor/Init
    "PID_ERROR_DATA": (0x6C, None), # R,Test
    "PID_ERROR_ADDR": (0x6D, None), # RW,Test

    "PID_ERROR_PID_TORQUE_ERROR": (0x6C, 0),
    "PID_ERROR_PID_FLUX_ERROR": (0x6C, 1),
    "PID_ERROR_PID_VELOCITY_ERROR": (0x6C, 2),
    "PID_ERROR_PID_POSITION_ERROR": (0x6C, 3),
    "PID_ERROR_PID_TORQUE_ERROR_SUM": (0x6C, 4),
    "PID_ERROR_PID_FLUX_ERROR_SUM": (0x6C, 5),
    "PID_ERROR_PID_VELOCITY_ERROR_SUM": (0x6C, 6),
    "PID_ERROR_PID_POSITION_ERROR_SUM": (0x6C, 7),

    "INTERIM_DATA": (0x6E, None), # RW,Monitor
    "INTERIM_ADDR": (0x6F, None), # RW,Monitor

    "INTERIM_PIDIN_TARGET_TORQUE": (0x6E, 0),
    "INTERIM_PIDIN_TARGET_FLUX": (0x6E, 1),
    "INTERIM_PIDIN_TARGET_VELOCITY": (0x6E, 2),
    "INTERIM_PIDIN_TARGET_POSITION": (0x6E, 3),
    "INTERIM_PIDOUT_TARGET_TORQUE": (0x6E, 4),
    "INTERIM_PIDOUT_TARGET_FLUX": (0x6E, 5),
    "INTERIM_PIDOUT_TARGET_VELOCITY": (0x6E, 6),
    "INTERIM_PIDOUT_TARGET_POSITION": (0x6E, 7),
    "INTERIM_FOC_IWY_IUX": (0x6E, 8),
    "INTERIM_FOC_IV": (0x6E, 9),
    "INTERIM_FOC_IB_IA": (0x6E, 10),
    "INTERIM_FOC_IQ_ID": (0x6E, 11),
    "INTERIM_FOC_UQ_UD": (0x6E, 12),
    "INTERIM_FOC_UQ_UD_LIMITED": (0x6E, 13),
    "INTERIM_FOC_UB_UA": (0x6E, 14),
    "INTERIM_FOC_UWY_UUX": (0x6E, 15),
    "INTERIM_FOC_UV": (0x6E, 16),
    "INTERIM_PWM_WY_UX": (0x6E, 17),
    "INTERIM_PWM_UV": (0x6E, 18),
    "INTERIM_ADC_I1_I0": (0x6E, 19),
    "INTERIM_PID_TORQUE_TARGET_FLUX_TARGET_TORQUE_ACTUAL_FLUX_ACTUAL_DIV256": (0x6E, 20),
    "INTERIM_PID_TORQUE_TARGET_TORQUE_ACTUAL": (0x6E, 21),
    "INTERIM_PID_FLUX_TARGET_FLUX_ACTUAL": (0x6E, 22),
    "INTERIM_PID_VELOCITY_TARGET_VELOCITY_ACTUAL_DIV256": (0x6E, 23),
    "INTERIM_PID_VELOCITY_TARGET_VELOCITY_ACTUAL": (0x6E, 24),
    "INTERIM_PID_POSITION_TARGET_POSITION_ACTUAL_DIV256": (0x6E, 25),
    "INTERIM_PID_POSITION_TARGET_POSITION_ACTUAL": (0x6E, 26),
    "INTERIM_FF_VELOCITY": (0x6E, 27),
    "INTERIM_FF_TORQUE": (0x6E, 28),
    "INTERIM_ACTUAL_VELOCITY_PPTM": (0x6E, 29),
    "INTERIM_REF_SWITCH_STATUS": (0x6E, 30),
    "INTERIM_HOME_POSITION": (0x6E, 31),
    "INTERIM_LEFT_POSITION": (0x6E, 32),
    "INTERIM_RIGHT_POSITION": (0x6E, 33),
    "INTERIM_SINGLE_PIN_IF_PWM_DUTY_CYCLE_TORQUE_TARGET": (0x6E, 42),
    "INTERIM_SINGLE_PIN_IF_VELOCITY_TARGET": (0x6E, 43),
    "INTERIM_SINGLE_PIN_IF_POSITION_TARGET": (0x6E, 44),

    "ADC_VM_LIMITS": (0x75, None), # RW,Init
    "TMC4671_INPUTS_RAW": (0x76, None), # R,Test/Monitor
    "TMC4671_OUTPUTS_RAW": (0x77, None), # R,Test/Monitor
    "STEP_WIDTH": (0x78, None), # RW,Init
    "UART_BPS": (0x79, None), # RW,Init
    "GPIO_DSADCI_CONFIG": (0x7B, None), # RW,Init

    "STATUS_FLAGS": (0x7C, None), # RW,Monitor
    "STATUS_MASK": (0x7D, None), # RW,Monitor
}

# These are read-only
ReadOnlyRegisters = {
    "CHIPINFO_DATA", "ADC_RAW_DATA", "ADC_IWY_IUX", "ADC_IV", "AENC_WY_UX",
    "AENC_VN", "ABN_DECODER_PHI_E_PHI_M", "ABN_2_DECODER_PHI_M",
    "HALL_PHI_E_INTERPOLATED_PHI_E", "HALL_PHI_M", "AENC_DECODER_PHI_A_RAW",
    "AENC_DECODER_PHI_A", "AENC_DECODER_PHI_E_PHI_M", "PHI_E",
    "PID_TORQUE_FLUX_ACTUAL", "PID_VELOCITY_ACTUAL", "PID_ERROR_DATA",
    "TMC4671_INPUTS_RAW", "TMC4671_OUTPUTS_RAW",
    }

ADC_GPIO_FIELDS = {
    "AGPI_A": "ADC_AGPI_A_RAW",
    "AGPI_B": "ADC_AGPI_B_RAW",
    None: None
}

Fields = {}

Fields["ADC_I1_RAW_ADC_I0_RAW"] = {
    "ADC_I0_RAW": 0xffff, "ADC_I1_RAW": 0xffff << 16
}
Fields["ADC_AGPI_A_RAW_ADC_VM_RAW"] = {
    "ADC_AGPI_A_RAW": 0xffff, "ADC_VM_RAW": 0xffff << 16
}
Fields["ADC_AENC_UX_RAW_ADC_AGPI_B_RAW"] = {
    "ADC_AENC_UX_RAW": 0xffff, "ADC_AGPI_B_RAW": 0xffff << 16
}
Fields["ADC_AENC_WY_RAW_ADC_AENC_VN_RAW"] = {
    "ADC_AENC_WY_RAW": 0xffff, "ADC_AENC_VN_RAW": 0xffff << 16
}

Fields["DSADC_MCFG_B_MCFG_A"] = {
    "CFG_DSMODULATOR_A": 3,
    "MCLK_POLARITY_A": 1 << 2,
    "MDAT_POLARITY_A": 1 << 3,
    "SEL_NCLK_MCLK_I_A": 1 << 4,
    "CFG_DSMODULATOR_B": 3 <<16,
    "MCLK_POLARITY_B": 1 << 18,
    "MDAT_POLARITY_B": 1 << 19,
    "SEL_NCLK_MCLK_I_B": 1 << 20
}

Fields["DSADC_MDEC_B_MDEC_A"] = {
    "DSADC_MDEC_A": 0xffff,
    "DSADC_MDEC_B": 0xffff << 16
}

Fields["ADC_I1_SCALE_OFFSET"] = {
    "ADC_I1_OFFSET": 0xffff,
    "ADC_I1_SCALE": 0xffff << 16
}

Fields["ADC_I0_SCALE_OFFSET"] = {
    "ADC_I0_OFFSET": 0xffff,
    "ADC_I0_SCALE": 0xffff << 16
}

Fields["ADC_I_SELECT"] = {
    "ADC_I0_SELECT": 0xff,
    "ADC_I1_SELECT": 0xff << 8,
    "ADC_I_UX_SELECT": 0x3 << 24,
    "ADC_I_V_SELECT": 0x3 << 26,
    "ADC_I_WY_SELECT": 0x3 << 28,
}

Fields["ADC_I1_I0_EXT"] = {
    "ADC_I0_EXT": 0xffff,
    "ADC_I1_EXT": 0xffff << 16
}


Fields["DS_ANALOG_INPUT_STAGE_CFG"] = {
    "CFG_ADC_I0": 0xf,
    "CFG_ADC_I1": 0xf << 4,
    "CFG_ADC_VM": 0xf << 8,
    "CFG_ADC_AGPI_A": 0xf << 12,
    "CFG_ADC_AGPI_B": 0xf << 16,
    "CFG_ADC_AENC_UX": 0xf << 20,
    "CFG_ADC_AENC_VN": 0xf << 24,
    "CFG_ADC_AENC_WY": 0xf << 28,
}

Fields["AENC_0_SCALE_OFFSET"] = {
    "AENC_0_OFFSET": 0xffff,
    "AENC_0_SCALE": 0xffff << 16
}

Fields["AENC_1_SCALE_OFFSET"] = {
    "AENC_1_OFFSET": 0xffff,
    "AENC_1_SCALE": 0xffff << 16
}

Fields["AENC_2_SCALE_OFFSET"] = {
    "AENC_2_OFFSET": 0xffff,
    "AENC_2_SCALE": 0xffff << 16
}

Fields["AENC_SELECT"] = {
    "AENC_0_SELECT": 0xff,
    "AENC_1_SELECT": 0xff << 8,
    "AENC_2_SELECT": 0xff << 16,
}

Fields["ADC_IWY_IUX"] = {
    "ADC_IUX": 0xffff,
    "ADC_IWY": 0xffff << 16
}

Fields["ADC_IV"] = {
    "ADC_IV": 0xffff,
}

Fields["AENC_WY_UX"] = {
    "AENC_UX": 0xffff,
    "AENC_WY": 0xffff << 16
}

Fields["AENC_VN"] = {
    "AENC_VN": 0xffff,
}

Fields["PWM_POLARITIES"] = {
    "PWM_POLARITIES_0": 1,
    "PWM_POLARITIES_1": 1 << 1,
}

Fields["PWM_BBM_H_BBM_L"] = {
    "PWM_BBM_L": 0xff,
    "PWM_BBM_H": 0xff << 8,
}

Fields["PWM_SV_CHOP"] = {
    "PWM_CHOP": 0xff,
    "PWM_SV": 1 << 8,
}

Fields["MOTOR_TYPE_N_POLE_PAIRS"] = {
    "N_POLE_PAIRS": 0xffff,
    "MOTOR_TYPE": 0xff << 16,
}

Fields["OPENLOOP_MODE"] = {
    "OPENLOOP_PHI_DIRECTION": 0x1 << 12,
}

Fields["UQ_UD_EXT"] = {
    "UD_EXT": 0xffff,
    "UQ_EXT": 0xffff << 16
}

Fields["ABN_DECODER_MODE"] = {
    "ABN_APOL": 1,
    "ABN_BPOL": 1 << 1,
    "ABN_NPOL": 1 << 2,
    "ABN_USE_ABN_AS_N": 1 <<3,
    "ABN_CLN": 1 << 8,
    "ABN_DIRECTION": 1 << 12,
}

Fields["ABN_DECODER_PHI_E_PHI_M_OFFSET"] = {
    "ABN_DECODER_PHI_M_OFFSET": 0xffff,
    "ABN_DECODER_PHI_E_OFFSET": 0xffff << 16
}

Fields["ABN_DECODER_PHI_E_PHI_M"] = {
    "ABN_DECODER_PHI_M": 0xffff,
    "ABN_DECODER_PHI_E": 0xffff << 16
}

Fields["ABN_2_DECODER_MODE"] = {
    "ABN_2_APOL": 1,
    "ABN_2_BPOL": 1 << 1,
    "ABN_2_NPOL": 1 << 2,
    "ABN_2_USE_ABN_AS_N": 1 <<3,
    "ABN_2_CLN": 1 << 8,
    "ABN_2_DIRECTION": 1 << 12,
}

Fields["ABN_2_DECODER_PHI_E_PHI_M_OFFSET"] = {
    "ABN_2_DECODER_PHI_M_OFFSET": 0xffff,
    "ABN_2_DECODER_PHI_E_OFFSET": 0xffff << 16
}

Fields["ABN_2_DECODER_PHI_E_PHI_M"] = {
    "ABN_2_DECODER_PHI_M": 0xffff,
    "ABN_2_DECODER_PHI_E": 0xffff << 16
}

Fields["HALL_MODE"] = {
    "HALL_POLARITY": 1,
    "HALL_SYNC": 1 << 4,
    "HALL_INTERP": 1 << 8,
    "HALL_DIR": 1 << 12,
    "HALL_BLANK": 0xfff << 16,
}

Fields["HALL_POSITION_060_000"] = {
    "HALL_POSITION_000": 0xffff,
    "HALL_POSITION_060": 0xffff << 16
}

Fields["HALL_POSITION_180_120"] = {
    "HALL_POSITION_120": 0xffff,
    "HALL_POSITION_180": 0xffff << 16
}

Fields["HALL_POSITION_300_240"] = {
    "HALL_POSITION_240": 0xffff,
    "HALL_POSITION_300": 0xffff << 16
}

Fields["HALL_PHI_E_PHI_M_OFFSET"] = {
    "HALL_PHI_M_OFFSET": 0xffff,
    "HALL_PHI_E_OFFSET": 0xffff << 16
}

Fields["HALL_PHI_E_INTERPOLATED_PHI_E"] = {
    "HALL_PHI_E": 0xffff,
    "HALL_PHI_E_INTERPOLATED": 0xffff << 16
}

Fields["AENC_DECODER_MODE"] = {
    "AENC_DEG": 1,
    "AENC_DIR": 1 << 12,
}

Fields["AENC_DECODER_PPR"] = {
    "AENC_PPR": 0xffff,
}

Fields["AENC_DECODER_PHI_E_PHI_M_OFFSET"] = {
    "AENC_DECODER_PHI_M_OFFSET": 0xffff,
    "AENC_DECODER_PHI_E_OFFSET": 0xffff << 16
}

Fields["AENC_DECODER_PHI_E_PHI_M"] = {
    "AENC_DECODER_PHI_M": 0xffff,
    "AENC_DECODER_PHI_E": 0xffff << 16
}

# CONFIG_DATA changes layout depending on the selected address
Fields["CONFIG_ADVANCED_PI_REPRESENT"] = {
    "CURRENT_I_n": 1 << 0,
    "CURRENT_P_n": 1 << 1,
    "VELOCITY_I_n": 1 << 2,
    "VELOCITY_P_n": 1 << 3,
    "POSITION_I_n": 1 << 4,
    "POSITION_P_n": 1 << 5,
}

Fields["VELOCITY_SELECTION"] = {
    "VELOCITY_SELECTION": 0xff,
    "VELOCITY_METER_SELECTION": 0xff << 8,
}

Fields["PID_FLUX_P_FLUX_I"] = {
    "PID_FLUX_I": 0xffff,
    "PID_FLUX_P": 0xffff << 16
}

Fields["PID_TORQUE_P_TORQUE_I"] = {
    "PID_TORQUE_I": 0xffff,
    "PID_TORQUE_P": 0xffff << 16
}

Fields["PID_VELOCITY_P_VELOCITY_I"] = {
    "PID_VELOCITY_I": 0xffff,
    "PID_VELOCITY_P": 0xffff << 16
}

Fields["PID_POSITION_P_POSITION_I"] = {
    "PID_POSITION_I": 0xffff,
    "PID_POSITION_P": 0xffff << 16
}

Fields["MODE_RAMP_MODE_MOTION"] = {
    "MODE_MOTION": 0xff,
    "MODE_PID_SMPL": 0x7f << 24,
    "MODE_FF": 0xff << 16,
    "MODE_PID_TYPE": 1 << 31
}

Fields["PID_TORQUE_FLUX_TARGET"] = {
    "PID_FLUX_TARGET": 0xffff,
    "PID_TORQUE_TARGET": 0xffff << 16
}

Fields["PID_TORQUE_FLUX_OFFSET"] = {
    "PID_FLUX_OFFSET": 0xffff,
    "PID_TORQUE_OFFSET": 0xffff << 16
}

Fields["PID_TORQUE_FLUX_ACTUAL"] = {
    "PID_FLUX_ACTUAL": 0xffff,
    "PID_TORQUE_ACTUAL": 0xffff << 16
}

Fields["INTERIM_PWM_WY_UX"] = {
    "INTERIM_PWM_UX": 0xffff,
    "INTERIM_PWM_WY": 0xffff << 16
}


Fields["ADC_VM_LIMITS"] = {
    "ADC_VM_LIMIT_LOW": 0xffff,
    "ADC_VM_LIMIT_HIGH": 0xffff << 16
}

Fields["STATUS_FLAGS"] = {
    "PID_X_TARGET_LIMIT": 1 << 0,
    "PID_X_ERRSUM_LIMIT": 1 << 2,
    "PID_X_OUTPUT_LIMIT": 1 << 3,
    "PID_V_TARGET_LIMIT": 1 << 4,
    "PID_V_ERRSUM_LIMIT": 1 << 6,
    "PID_V_OUTPUT_LIMIT": 1 << 7,
    "PID_ID_TARGET_LIMIT": 1 << 8,
    "PID_ID_ERRSUM_LIMIT": 1 << 10,
    "PID_ID_OUTPUT_LIMIT": 1 << 11,
    "PID_IQ_TARGET_LIMIT": 1 << 12,
    "PID_IQ_ERRSUM_LIMIT": 1 << 14,
    "PID_IQ_OUTPUT_LIMIT": 1 << 15,
    "IPARK_CIRLIM_LIMIT_U_D": 1 << 16,
    "IPARK_CIRLIM_LIMIT_U_Q": 1 << 17,
    "IPARK_CIRLIM_LIMIT_U_R": 1 << 18,
    "REF_SW_R": 1 << 20,
    "REF_SW_H": 1 << 21,
    "REF_SW_L": 1 << 22,
    "PWM_MIN": 1 << 24,
    "PWM_MAX": 1 << 25,
    "ADC_I_CLIPPED": 1 << 26,
    "AENC_CLIPPED": 1 << 27,
    "ENC_N": 1 << 28,
    "ENC_2_N": 1 << 29,
    "AENC_N": 1 << 30,
}

# Mask has same structure as the status field
FloatFields = {"PID_FLUX_I", "PID_FLUX_P",
               "PID_TORQUE_I", "PID_TORQUE_P", "PID_VELOCITY_I",
               "PID_VELOCITY_P", "PID_POSITION_I", "PID_POSITION_P",
               "FEED_FORWARD_VELOCITY_GAIN",
               "FEED_FORWARD_VELOCITY_FILTER_CONSTANT",
               "FEED_FORWARD_TORQUE_GAIN",
               "FEED_FORWARD_TORQUE_FILTER_CONSTANT",
}
SignedFields = {"ADC_I1_SCALE", "ADC_I0_SCALE", "AENC_0_SCALE", "AENC_1_SCALE",
                "AENC_2_SCALE", "ADC_IUX", "ADC_IWY", "ADC_IV", "AENC_UX",
                "AENC_WY", "AENC_VN", "PHI_E_EXT", "OPENLOOP_VELOCITY_TARGET",
                "OPENLOOP_VELOCITY_ACTUAL", "OPENLOOP_PHI", "UD_EXT", "UQ_EXT",
                "ABN_DECODER_PHI_M_OFFSET", "ABN_DECODER_PHI_E_OFFSET",
                "ABN_DECODER_PHI_M", "ABN_DECODER_PHI_E",
                "ABN_2_DECODER_PHI_M_OFFSET", "ABN_2_DECODER_PHI_M",
                "HALL_POSITION_000", "HALL_POSITION_060", "HALL_POSITION_120",
                "HALL_POSITION_180", "HALL_POSITION_240", "HALL_POSITION_300",
                "HALL_PHI_M_OFFSET", "HALL_PHI_E_OFFSET", "HALL_PHI_E",
                "HALL_PHI_E_INTERPOLATED", "HALL_PHI_M",
                "AENC_DECODER_PHI_A_RAW", "AENC_DECODER_PHI_A_OFFSET",
                "AENC_DECODER_PHI_A", "AENC_DECODER_PPR", "AENC_DECODER_COUNT",
                "AENC_DECODER_COUNT_N", "AENC_DECODER_PHI_M_OFFSET",
                "AENC_DECODER_PHI_E_OFFSET", "AENC_DECODER_PHI_M",
                "AENC_DECODER_PHI_E", "PHI_E",
                "PIDOUT_UQ_UD_LIMITS", "PID_POSITION_LIMIT_LOW",
                "PID_POSITION_LIMIT_HIGH", "PID_FLUX_TARGET",
                "PID_TORQUE_TARGET", "PID_FLUX_OFFSET", "PID_TORQUE_OFFSET",
                "PID_VELOCITY_TARGET", "PID_VELOCITY_OFFSET",
                "PID_POSITION_TARGET", "PID_FLUX_ACTUAL", "PID_TORQUE_ACTUAL",
                "PID_VELOCITY_ACTUAL", "PID_POSITION_ACTUAL",
                "PID_ERROR_PID_TORQUE_ERROR", "PID_ERROR_PID_FLUX_ERROR", "PID_ERROR_PID_VELOCITY_ERROR",
                "PID_ERROR_PID_POSITION_ERROR", "PID_ERROR_PID_TORQUE_ERROR_SUM",
                "PID_ERROR_PID_FLUX_ERROR_SUM", "PID_ERROR_PID_VELOCITY_ERROR_SUM",
                "PID_ERROR_PID_POSITION_ERROR_SUM", "STEP_WIDTH",
                "INTERIM_PIDIN_TARGET_TORQUE",
                "INTERIM_PIDIN_TARGET_FLUX",
                "INTERIM_PIDIN_TARGET_VELOCITY",
                "INTERIM_PIDIN_TARGET_POSITION",
                "INTERIM_PIDOUT_TARGET_TORQUE",
                "INTERIM_PIDOUT_TARGET_FLUX",
                "INTERIM_PIDOUT_TARGET_VELOCITY",
                "INTERIM_PIDOUT_TARGET_POSITION",
                "INTERIM_FOC_IWY_IUX",
                "INTERIM_FOC_IV",
                "INTERIM_FOC_IB_IA",
                "INTERIM_FOC_IQ_ID",
                "INTERIM_FOC_UQ_UD",
                "INTERIM_FOC_UQ_UD_LIMITED",
                "INTERIM_FOC_UB_UA",
                "INTERIM_FOC_UWY_UUX",
                "INTERIM_FOC_UV",
                "INTERIM_PWM_WY_UX",
                "INTERIM_PWM_UV",
                "INTERIM_ADC_I1_I0",
                "INTERIM_PID_TORQUE_TARGET_FLUX_TARGET_TORQUE_ACTUAL_FLUX_ACTUAL_DIV256",
                "INTERIM_PID_TORQUE_TARGET_TORQUE_ACTUAL",
                "INTERIM_PID_FLUX_TARGET_FLUX_ACTUAL",
                "INTERIM_PID_VELOCITY_TARGET_VELOCITY_ACTUAL_DIV256",
                "INTERIM_PID_VELOCITY_TARGET_VELOCITY_ACTUAL",
                "INTERIM_PID_POSITION_TARGET_POSITION_ACTUAL_DIV256",
                "INTERIM_PID_POSITION_TARGET_POSITION_ACTUAL",
                "INTERIM_FF_VELOCITY",
                "INTERIM_FF_TORQUE",
                "INTERIM_ACTUAL_VELOCITY_PPTM",
                "INTERIM_REF_SWITCH_STATUS",
                "INTERIM_HOME_POSITION",
                "INTERIM_LEFT_POSITION",
                "INTERIM_RIGHT_POSITION",
                "INTERIM_SINGLE_PIN_IF_PWM_DUTY_CYCLE_TORQUE_TARGET",
                "INTERIM_SINGLE_PIN_IF_VELOCITY_TARGET",
                "INTERIM_SINGLE_PIN_IF_POSITION_TARGET",
                }

def format_phi(val):
    phi = (val * 360.0 / 65536.0)
    if phi < 0.0:
        phi += 360
    return "%.3f" % (phi)

def format_q4_12(val):
    return "%.4f" % (val * 2**-12)

def to_q4_12(val):
    return round(val * 2**12) & 0xffff

def from_q4_12(val):
    return val * 2**-12

def format_q0_15(val):
    return "%.7f" % (val * 2**-15)

def from_q8_8(val):
    return val * 2**-8

def format_q8_8(val):
    return "%.3f" % (from_q8_8(val))

def to_q8_8(val):
    return round(val * 2**8) & 0xffff

def format_q3_29(val):
    return "%.9f" % (val * 2**-29)

def to_q2_30(val):
    return round(val * 2**30) & 0xffffffff

def from_q2_30(val):
    return val * 2**-30

def format_q2_30(val):
    return "%.9f" % (val * 2**-30)

FieldFormatters = {
    "CONFIG_BIQUAD_X_A_1": format_q3_29,
    "CONFIG_BIQUAD_X_A_2": format_q3_29,
    "CONFIG_BIQUAD_X_B_0": format_q3_29,
    "CONFIG_BIQUAD_X_B_1": format_q3_29,
    "CONFIG_BIQUAD_X_B_2": format_q3_29,
    "CONFIG_BIQUAD_V_A_1": format_q3_29,
    "CONFIG_BIQUAD_V_A_2": format_q3_29,
    "CONFIG_BIQUAD_V_B_0": format_q3_29,
    "CONFIG_BIQUAD_V_B_1": format_q3_29,
    "CONFIG_BIQUAD_V_B_2": format_q3_29,
    "CONFIG_BIQUAD_T_A_1": format_q3_29,
    "CONFIG_BIQUAD_T_A_2": format_q3_29,
    "CONFIG_BIQUAD_T_B_0": format_q3_29,
    "CONFIG_BIQUAD_T_B_1": format_q3_29,
    "CONFIG_BIQUAD_T_B_2": format_q3_29,
    "CONFIG_BIQUAD_F_A_1": format_q3_29,
    "CONFIG_BIQUAD_F_A_2": format_q3_29,
    "CONFIG_BIQUAD_F_B_0": format_q3_29,
    "CONFIG_BIQUAD_F_B_1": format_q3_29,
    "CONFIG_BIQUAD_F_B_2": format_q3_29,
    "FEED_FORWARD_VELOCITY_GAIN": format_q2_30,
    "FEED_FORWARD_VELOCITY_FILTER_CONSTANT": format_q2_30,
    "FEED_FORWARD_TORQUE_GAIN": format_q2_30,
    "FEED_FORWARD_TORQUE_FILTER_CONSTANT": format_q2_30,
    "HALL_POSITION_000": format_phi,
    "HALL_POSITION_120": format_phi,
    "HALL_POSITION_240": format_phi,
    "HALL_POSITION_060": format_phi,
    "HALL_POSITION_180": format_phi,
    "HALL_POSITION_300": format_phi,
    "HALL_PHI_E": format_phi,
    "HALL_PHI_E_INTERPOLATED": format_phi,
    "HALL_PHI_E_PHI_M_OFFSET": format_phi,
    "HALL_PHI_M": format_phi,
    "PHI_E": format_phi,
    "HALL_PHI_E_OFFSET": format_phi,
    "HALL_PHI_M_OFFSET": format_phi,
    "ABN_DECODER_PHI_M": format_phi,
    "ABN_DECODER_PHI_E": format_phi,
    "ABN_DECODER_PHI_E_OFFSET": format_phi,
    "ABN_DECODER_PHI_M_OFFSET": format_phi,
    "PID_FLUX_P": format_q4_12,
    "PID_FLUX_I": format_q4_12,
    "PID_TORQUE_P": format_q4_12,
    "PID_TORQUE_I": format_q4_12,
    "PID_VELOCITY_P": format_q8_8,
    "PID_VELOCITY_I": format_q4_12,
    "PID_POSITION_P": format_q8_8,
    "PID_POSITION_I": format_q4_12,
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
    a1 = - 2.0 * cw0
    a2 = 1 - alpha
    return b0, b1, b2, a0, a1, a2

# Design a biquad notch filter in canonical form
def biquad_notch(fs, f, Q):
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
    dcgain = 1.0
    e29 = 2**29
    b0 = round(b0z/(a0*dcgain) * e29)
    b1 = round(b1z/(a0*dcgain) * e29)
    b2 = round(b2z/(a0*dcgain) * e29)
    a1 = round(-a1z/a0 * e29)
    a2 = round(-a2z/a0 * e29)
    # return in the same order as the config registers
    return a1, a2, b0, b1, b2

# Normalise a biquad filter, according to TMC
def biquad_tmc(b0, b1, b2, a0, a1, a2):
    dcgain = (b0 + b1 + b2) / (a0 + a1 + a2)
    #dcgain = 1.0
    e29 = 2**29
    b0 = round(b0/(a0*dcgain) * e29)
    b1 = round(b1/(a0*dcgain) * e29)
    b2 = round(b2/(a0*dcgain) * e29)
    a1 = round(-a1/a0 * e29)
    a2 = round(-a2/a0 * e29)
    # return in the same order as the config registers
    return a1, a2, b0, b1, b2

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


class PIDHelper:
    def __init__(self, config, mcu_tmc, var, def_v, nvar, def_n):
        self.mcu_tmc = mcu_tmc
        self.fields = mcu_tmc.get_fields()
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
        self.fields = mcu_tmc.get_fields()
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
        self.fields = mcu_tmc.get_fields()
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
    def set_current(self, run_current):
        self.run_current = run_current
        self.flux_limit = self._calc_flux_limit(self.run_current)
        self._write_field("PID_TORQUE_FLUX_LIMITS", self.flux_limit)
        return self.flux_limit
    def set_flux_current(self, current):
        self.flux_current = current
        self.flux_limit = self._calc_flux_limit(self.flux_current)
        self._write_field("PID_FLUX_OFFSET", self.flux_limit)
        return self.flux_limit
    def _read_field(self, field):
        reg_name = self.fields.lookup_register(field)
        reg_value = self.mcu_tmc.get_register(reg_name)
        return self.fields.get_field(field, reg_value=reg_value,
                                     reg_name=reg_name)
    def _write_field(self, field, val):
        reg_name = self.fields.lookup_register(field)
        reg_value = self.mcu_tmc.get_register(reg_name)
        self.mcu_tmc.set_register(reg_name,
                                  self.fields.set_field(field, val,
                                                        reg_value=reg_value,
                                                        reg_name=reg_name))


######################################################################
# Helper to configure the microstep settings
######################################################################


def StepHelper(config, mcu_tmc):
    fields = mcu_tmc.get_fields()
    stepper_name = " ".join(config.get_name().split()[1:])
    if not config.has_section(stepper_name):
        raise config.error(
            "Could not find config section '[%s]' required by tmc4671 driver"
            % (stepper_name,))
    sconfig = config.getsection(stepper_name)
    steps = {1<<i: 1<<i for i in range(0, 16)}
    res = sconfig.getchoice('full_steps_per_rotation', steps, default=8)
    mres = sconfig.getchoice('microsteps', steps, default=256)
    if res * mres > 65536:
        raise config.error(
            "Product of res and mres must not be more than 65536 for [%s]"
            % (stepper_name,))
    step_width = 65536 // (res * mres)
    fields.set_field("STEP_WIDTH", step_width)


######################################################################
# Periodic error checking
######################################################################


class TMCErrorCheck:
    def __init__(self, config, mcu_tmc):
        self.printer = config.get_printer()
        name_parts = config.get_name().split()
        self.stepper_name = ' '.join(name_parts[1:])
        self.mcu_tmc = mcu_tmc
        self.fields = mcu_tmc.get_fields()
        self.check_timer = None
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
        # Setup for temperature query
        # Per the OpenFFBoard firmware source
        #[thermistor ffboard]
        #temperature1: 25
        #resistance1: 10000
        #beta: 4300
        self.adc_temp = None
        self.adc_temp_reg = config.getchoice("adc_temp_reg",
                                             ADC_GPIO_FIELDS,
                                             default=None)
        if self.adc_temp_reg is not None:
            pheaters = self.printer.load_object(config, 'heaters')
            pheaters.register_monitor(config)
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
        #for reg_name in DumpGroups["monitor"]:
        #    val = self.mcu_tmc.get_register(reg_name)
        #    self.monitor_data.update(self.fields.get_reg_fields(reg_name, val))
        #    logging.info("TMC 4671 '%s' %s: %s", self.stepper_name,
        #                 reg_name, self.fields.pretty_format(reg_name, val))
    def _query_temperature(self):
        try:
            if self.adc_temp_reg is not None:
                self.adc_temp = self.mcu_tmc.read_field(self.adc_temp_reg)
                # TODO: remove this, just temp logging
                self._convert_temp(self.adc_temp)
        except self.printer.command_error as e:
            # Ignore comms error for temperature
            self.adc_temp = None
            return
    def _do_periodic_check(self, eventtime):
        try:
            self._query_status()
            # self._query_temperature()
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))
            return self.printer.get_reactor().NEVER
        return eventtime + 1.
    def stop_checks(self):
        if self.check_timer is None:
            return
        self.printer.get_reactor().unregister_timer(self.check_timer)
        self.check_timer = None
    def start_checks(self):
        if self.check_timer is not None:
            self.stop_checks()
        reactor = self.printer.get_reactor()
        curtime = reactor.monotonic()
        self.check_timer = reactor.register_timer(self._do_periodic_check,
                                                  curtime + 1.)
        return True
    def _convert_temp(self, adc):
        v = adc - 0x7fff
        if v < 0:
            temp = 0.0
        else:
            #temp = 1500.0 * 43252.0 / float(v)
            #temp = 64878000.0 / float(v)
            temp = 129756000.0 / float(v)
            #temp = (1.0/298.15) + math.log(temp / 10000.0) / 4300.0
            temp = (0.003354016) + math.log(temp / 10000.0) / 4300.0
            temp = 1.0 / temp
            temp -= 273.15
        logging.info("TMC %s temp: %g", self.stepper_name, temp)
    def get_status(self, eventtime=None):
        res = {'drv_status': None, 'temperature': None}
        res.update(self.monitor_data)
        if self.check_timer is None:
            return res
        temp = None
        if self.adc_temp is not None:
            # Convert it to temp here
            temp = self._convert_temp(self.adc_temp)
        res['temperature'] = temp
        return res


######################################################################
# Helper class for "sensorless homing"
######################################################################


class TMCVirtualPinHelper:
    def __init__(self, config, mcu_tmc, current_helper):
        self.printer = config.get_printer()
        self.mcu_tmc = mcu_tmc
        self.fields = mcu_tmc.get_fields()
        self.current_helper = current_helper
        self.diag_pin = config.get('diag_pin', None)
        self.mcu_endstop = None
        self.en_pwm = False
        # Stalls show up as either IQ_ERRSUM or V_OUTPUT.
        # Include the reference switches so can connect endstops
        # to driver boards.
        self.status_mask_entries = config.getlist("homing_mask",
                                                  ["PID_IQ_OUTPUT_LIMIT",
                                                   "PID_ID_OUTPUT_LIMIT",
                                                   "PID_X_ERRSUM_LIMIT",
                                                   #"PID_IQ_ERRSUM_LIMIT",
                                                   #"PID_ID_ERRSUM_LIMIT",
                                                   #"PID_IQ_TARGET_LIMIT",
                                                   "PID_ID_TARGET_LIMIT",
                                                   #"PID_X_OUTPUT_LIMIT",
                                                   "PID_V_OUTPUT_LIMIT",
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
    def setup_pin(self, pin_type, pin_params):
        # Validate pin
        ppins = self.printer.lookup_object('pins')
        if pin_type != 'endstop' or pin_params['pin'] != 'virtual_endstop':
            raise ppins.error("tmc virtual endstop only useful as endstop")
        if pin_params['invert'] or pin_params['pullup']:
            raise ppins.error("Can not pullup/invert tmc virtual pin")
        if self.diag_pin is None:
            raise ppins.error("tmc virtual endstop requires diag pin config")
        # Setup for sensorless homing
        self.printer.register_event_handler("homing:homing_move_begin",
                                            self.handle_homing_move_begin)
        self.printer.register_event_handler("homing:homing_move_end",
                                            self.handle_homing_move_end)
        self.mcu_endstop = ppins.setup_pin('endstop', self.diag_pin)
        return self.mcu_endstop
    def handle_homing_move_begin(self, hmove):
        if self.mcu_endstop not in hmove.get_mcu_endstops():
            return
        #self.mcu_tmc.write_field("PID_VELOCITY_LIMIT", 3000)
        self.current_helper.set_current(self.current_helper.get_homing_current())
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        self.printer.lookup_object('toolhead').dwell(0.005)
        self.mcu_tmc.write_field("STATUS_MASK", self.status_mask)
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        status = self.mcu_tmc.get_register("STATUS_FLAGS")
        fmt = self.fields.pretty_format("STATUS_FLAGS", status)
        logging.info("TMC 4671 '%s' status at homing start %s", self.name, fmt)
    def handle_homing_move_end(self, hmove):
        status = self.mcu_tmc.get_register("STATUS_FLAGS")
        fmt = self.fields.pretty_format("STATUS_FLAGS", status)
        logging.info("TMC 4671 '%s' status at homing end %s", self.name, fmt)
        if self.mcu_endstop not in hmove.get_mcu_endstops():
            return
        #self.mcu_tmc.write_field("PID_VELOCITY_LIMIT", 0x300000)
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)
        self.current_helper.set_current(self.current_helper.get_run_current())
        self.mcu_tmc.write_field("STATUS_MASK", 0)
        self.mcu_tmc.set_register_once("STATUS_FLAGS", 0)


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
            for retry in range(5):
                v = self.tmc_spi.reg_write(reg, val, print_time)
                if v == val:
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

######################################################################
# Main driver class
######################################################################


class TMC4671:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.stepper_name = ' '.join(config.get_name().split()[1:])
        self.name = config.get_name().split()[-1]
        self.mutex = self.printer.get_reactor().mutex()
        self.init_done = False
        self.alignment_done = False
        self.fields = FieldHelper(Fields,
                                  signed_fields=SignedFields,
                                  float_fields=FloatFields,
                                  field_formatters=FieldFormatters,
                                  prefix="foc_")
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
        self.vm_range = round(32767/1.25)
        # Correct for the OpenFFBoard
        self.voltage_scale = config.getfloat('voltage_scale_ratio', 43.64,
                                       above=0.)
        self.mcu_tmc = MCU_TMC_SPI(config, Registers, self.fields,
                                   TMC_FREQUENCY, pin_option="cs_pin")
        self.read_translate = None
        self.read_registers = Registers.keys()
        self.printer.register_event_handler("klippy:connect",
                                            self._handle_connect)
        self.printer.register_event_handler("klippy:ready",
                                            self._handle_ready)
        #self.printer.register_event_handler("idle_timeout:ready",
        #                                    self._handle_ready)
        self.stepper = None
        self.stepper_enable = self.printer.load_object(config, "stepper_enable")
        self.printer.register_event_handler("klippy:mcu_identify",
                                            self._handle_mcu_identify)
        self.printer.register_event_handler("klippy:connect",
                                            self._handle_connect)
        # Register commands
        self.step_helper = StepHelper(config, self.mcu_tmc)
        self.current_helper = CurrentHelper(config, self.mcu_tmc)
        self.error_helper = TMCErrorCheck(config, self.mcu_tmc)
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
        set_config_field(config, "MOTOR_TYPE", 3)
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
        set_config_field(config, "PIDOUT_UQ_UD_LIMITS", 31500) # Voltage limit, 32768 = Vm
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

        self.biquad_filters = {}
        for target in BIQUAD_FILTER_TARGETS.keys():
            filter_type = config.getchoice(
                f"biquad_{target}_filter",
                BIQUAD_FILTER_TYPES,
                default="lpf",
            )
            freq = config.getint(
                f"biquad_{target}_frequency",
                minval=0,
                maxval=4.0 * TMC_FREQUENCY,
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

    def _read_field(self, field):
        reg_name = self.fields.lookup_register(field)
        reg_value = self.mcu_tmc.get_register(reg_name)
        return self.fields.get_field(field, reg_value=reg_value,
                                     reg_name=reg_name)

    def _write_field(self, field, val):
        reg_name = self.fields.lookup_register(field)
        reg_value = self.mcu_tmc.get_register(reg_name)
        self.mcu_tmc.set_register(reg_name,
                                  self.fields.set_field(field, val,
                                                        reg_value=reg_value,
                                                        reg_name=reg_name))

    def enable_biquad(self, enable_field, *biquad):
        reg, addr = self.mcu_tmc.name_to_reg[enable_field]
        for o,i in enumerate(biquad):
            self.mcu_tmc.tmc_spi.reg_write(reg+1, addr-6+o)
            self.mcu_tmc.tmc_spi.reg_write(reg, i)
        self.mcu_tmc.tmc_spi.reg_write(reg+1, addr)
        self.mcu_tmc.tmc_spi.reg_write(reg, 1)

    def disable_biquad(self, enable_field):
        reg, addr = self.mcu_tmc.name_to_reg[enable_field]
        self.mcu_tmc.tmc_spi.reg_write(reg+1, addr)
        self.mcu_tmc.tmc_spi.reg_write(reg, 0)

    def _do_enable(self, print_time):
        try:
            with self.mutex:
                # If we were manually moved, we don't want any motion now
                self._write_field("PID_POSITION_TARGET",
                                  self._read_field("PID_POSITION_ACTUAL"))
                self.error_helper.start_checks()
                self._write_field("MODE_MOTION", MotionMode.position_mode)
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))

    def _do_disable(self, print_time):
        try:
            with self.mutex:
                self.error_helper.stop_checks()
                # Switching off the enable line will turn off the drivers
                # but, belt and braces, stop the controller as well.
                self._write_field("MODE_MOTION", MotionMode.stopped_mode)
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
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        # Check for soft stepper enable/disable
        enable_line = self.stepper_enable.lookup_enable(self.stepper_name)
        # Send init
        try:
            self._init_registers()
        except self.printer.command_error as e:
            logging.info("TMC %s failed to init: %s", self.name, str(e))
        enable_line.register_state_callback(self._handle_stepper_enable)

    def _handle_ready(self):
        # klippy:ready handlers are limited in what they may do. Communicating with a MCU
        # will pause the reactor and is thus forbidden. That code has to run outside of the event handler.
        self.printer.reactor.register_callback((lambda ev: self._handle_ready_deferred))

    def _handle_ready_deferred(self, print_time=None):
        with self.mutex:
            if print_time is None:
                print_time = self.printer.lookup_object('toolhead').get_last_move_time()
            # Set these before setting enable to avoid yeeting the toolhead
            self._write_field("MODE_MOTION", MotionMode.stopped_mode)
            self._write_field("STATUS_MASK", 0)
            self._write_field("PID_FLUX_TARGET", 0)
            self._write_field("PID_TORQUE_TARGET", 0)
            self._write_field("PID_VELOCITY_TARGET", 0)
            self._write_field("ABN_DECODER_COUNT", 0)
            self._write_field("PID_POSITION_TARGET", 0)
            # Now enable 6100
            if self.fields6100 is not None:
                self.mcu_tmc6100.set_register("GCONF",
                                              self.fields6100.set_field("disable", 0),
                                              print_time)
            enable_line = self.stepper_enable.lookup_enable(self.stepper_name)
            enable_line.motor_enable(print_time)
            # Just test the PID, as it also sets up the encoder offsets
            P, I = self._tune_flux_pid(True, 1.0, print_time)
            self._write_field("ABN_DECODER_COUNT", 0)
            self._write_field("PID_POSITION_TARGET", 0)
            print_time = self.printer.lookup_object('toolhead').get_last_move_time()
            enable_line.motor_disable(print_time)
            self.alignment_done = True
            self._write_field("STATUS_MASK", 0)
            self._write_field("PID_FLUX_TARGET", 0)
            self._write_field("PID_TORQUE_TARGET", 0)
            self._write_field("PID_VELOCITY_TARGET", 0)
            self._write_field("ABN_DECODER_COUNT", 0)
            self._write_field("PID_POSITION_TARGET", 0)
            self._write_field("MODE_MOTION", MotionMode.stopped_mode)
            self.init_done = True

    def _calibrate_adc(self, print_time):
        self._write_field("PWM_CHOP", 0)
        self._write_field("CFG_ADC_I0", 0)
        self._write_field("CFG_ADC_I1", 0)
        i0_off, i1_off = self._sample_adc("ADC_I1_RAW_ADC_I0_RAW")
        # Following code would calibrate the scalers as well.
        # However, not doing that makes things simpler, and the
        # calibration result is always +- 1 from nominal.
        #self._write_field("CFG_ADC_I0", 2)
        #self._write_field("CFG_ADC_I1", 2)
        #i0_l, i1_l = self._sample_adc("ADC_I1_RAW_ADC_I0_RAW")
        #self._write_field("CFG_ADC_I0", 3)
        #self._write_field("CFG_ADC_I1", 3)
        #i0_h, i1_h = self._sample_adc("ADC_I1_RAW_ADC_I0_RAW")
        #self._write_field("CFG_ADC_I0", 0)
        #self._write_field("CFG_ADC_I1", 0)
        #self._write_field("ADC_I1_SCALE", (256*(i1_h-i1_l))//32768)
        #self._write_field("ADC_I0_SCALE", (256*(i0_h-i0_l))//32768)
        self._write_field("ADC_I1_SCALE", 256)
        self._write_field("ADC_I0_SCALE", 256)
        self._write_field("ADC_I1_OFFSET", i1_off)
        self._write_field("ADC_I0_OFFSET", i0_off)
        # Calibrate for VM measurement
        # Chip errata? This doesn't work.
        #self._write_field("CFG_ADC_VM", 5)
        #vml, vmh = self._sample_vm()
        #self.vm_offset = round(mean((vml, vmh)))
        #self._write_field("CFG_ADC_VM", 7)
        #vml, vmh = self._sample_vm()
        #self.vm_range = self.vm_offset - round(mean((vml, vmh)))
        #self._write_field("CFG_ADC_VM", 4)
        logging.info("TMC 4671 %s ADC offsets I0=%d I1=%d", self.name, i0_off, i1_off)
        #logging.info("TMC 4671 %s ADC VM offset=%d range=%s VM=%g", self.name,
        #             self.vm_offset, self.vm_range, self._read_vm())
        # Now calibrate for brake chopper
        vml, vmh = self._sample_vm()
        vmr = abs(vmh - vml)
        logging.info("TMC 4671 %s VM samples low=%d high=%d", self.name, vml, vmh)
        high = math.ceil(0.05*self.voltage_scale) + vmr//2 + vmh
        if high < 65536:
            self._write_field("ADC_VM_LIMIT_HIGH", high)
            self._write_field("ADC_VM_LIMIT_LOW", vmr//2 + vmh)
            logging.info("TMC 4671 %s brake thresholds low=%d(%g V) high=%d(%g V)", self.name,
                         vmr//2+vmh, self._convert_vm(vmr//2+vmh),
                         high, self._convert_vm(high))
        else:
            # What else can we do but turn the brake off?
            self._write_field("ADC_VM_LIMIT_HIGH", 0)
            self._write_field("ADC_VM_LIMIT_LOW", 0)
        self._write_field("PWM_CHOP", 7)

    def _sample_adc(self, reg_name):
        self.printer.lookup_object('toolhead').dwell(0.2)
        reg, addr = self.mcu_tmc.name_to_reg[reg_name]
        self.mcu_tmc.tmc_spi.reg_write(reg+1, addr)
        i1 = []
        i0 = []
        n = 100
        for i in range(n):
            v = self.fields.get_reg_fields(reg_name,
                                           self.mcu_tmc.tmc_spi.reg_read(reg))
            i1.append(v["ADC_I1_RAW"])
            i0.append(v["ADC_I0_RAW"])
            self.printer.lookup_object('toolhead').dwell(0.0005)
        return median_low(i0), median_low(i1)

    def _sample_vm(self):
        self.printer.lookup_object('toolhead').dwell(0.2)
        vm = []
        n = 100
        for i in range(n):
            vm.append(self._read_field("ADC_VM_RAW"))
            self.printer.lookup_object('toolhead').dwell(0.0005)
        return min(vm), max(vm)

    def _convert_vm(self, val):
        return ((val - self.vm_offset) / float(self.vm_range)) * self.voltage_scale

    def _read_vm(self):
        return self._convert_vm(self._read_field("ADC_VM_RAW"))

    def _tune_flux_pid(self, test_existing, derate, print_time):
        return self._tune_pid("FLUX", 2.5, derate, True, test_existing, print_time)

    def _tune_torque_pid(self, test_existing, derate, print_time):
        return self._tune_pid("TORQUE", 1.0, derate, True, test_existing, print_time)

    # Align motors and tune PID via a setpoint change experiment
    # See https://folk.ntnu.no/skoge/publications/2012/skogestad-improved-simc-pid/PIDbook-chapter5.pdf
    def _tune_pid(self, X, Kc, derate, offsets, test_existing, print_time):
        ch = self.current_helper
        dwell = self.printer.lookup_object('toolhead').dwell
        old_mode = self._read_field("MODE_MOTION")
        old_phi_e_selection = self._read_field("PHI_E_SELECTION")
        self._write_field("MODE_MOTION", MotionMode.stopped_mode)
        limit_cur = self._read_field("PID_TORQUE_FLUX_LIMITS")
        old_flux_offset = self._read_field("PID_FLUX_OFFSET")
        self._write_field("PHI_E_EXT", 0) # and, set this to be PHI_E = 0
        self._write_field("PHI_E_SELECTION", 1) # external mode, so it won't change.
        # Start at some low voltage and see if we can read a current
        test_U = round(self.vm_range/self.voltage_scale) # Should be about 1V
        self._write_field("UQ_EXT", 0)
        self._write_field("UD_EXT", test_U)
        self._write_field("PID_TORQUE_TARGET", 0)
        self._write_field("PID_VELOCITY_TARGET", 0)
        self._write_field("PID_POSITION_TARGET", 0)
        self._write_field("PID_POSITION_ACTUAL", 0)
        self._write_field("MODE_MOTION", MotionMode.uq_ud_ext_mode)
        # Turn on the chopper and wait a bit to measure the resistance
        self._write_field("PWM_CHOP", 7)
        dwell(0.1)
        c, MAX_I, iux, iv, iwy = self.current_helper.get_current()
        self._write_field("PWM_CHOP", 0)
        logging.info("TMC 4671 '%s' initial I %s", self.stepper_name, str(self.current_helper.get_current()))
        if max(abs(iux), abs(iwy)) < 1e-6:
            # something is horribly wrong
             raise self.printer.command_error("TMC 4671 is seeing no motor current. Check wiring.")
        # Ok, calculate a voltage that will give us about a third of the configured current limit
        test2_U = round((c / 2.0) * test_U / max(abs(iux), abs(iwy)))
        logging.info("TMC 4671 '%s' test U %g %g", self.stepper_name, test_U, test2_U)
        # Switch back on, and this time motor should self-align
        self._write_field("UD_EXT", test2_U)
        self._write_field("PWM_CHOP", 7)
        dwell(0.1)
        c, MAX_I, iux, iv, iwy = self.current_helper.get_current()
        logging.info("TMC 4671 '%s' alignment I %s", self.stepper_name, str(self.current_helper.get_current()))
        test2_U/(self.vm_range/self.voltage_scale)
        R = test2_U * self.voltage_scale / (self.vm_range * max(abs(iux), abs(iwy)))
        logging.info("TMC 4671 '%s' est. motor R=%g", self.stepper_name, R)
        for i in range(5):
            dwell(0.2)
            self._write_field("PWM_CHOP", 0)
            # Give it some time to settle
            dwell(0.1)
            self._write_field("PWM_CHOP", 7)
        # Give it some time to settle
        dwell(0.2)
        # Now we should be mechanically aligned
        if offsets:
            # While we're here, set the offsets
            self._write_field("HALL_PHI_E_OFFSET", -self._read_field("HALL_PHI_E")%65536),
            self._write_field("ABN_DECODER_COUNT", 0)
            self._write_field("ABN_DECODER_PHI_E_OFFSET", 0)
        self._write_field("MODE_MOTION", MotionMode.stopped_mode)
        # Give it some time to settle
        dwell(0.1)
        self._write_field("MODE_MOTION", MotionMode.torque_mode)
        test_cur = limit_cur #// 2
        old_cur = self._read_field("PID_%s_ACTUAL"%X)
        dwell(0.1)
        if not test_existing:
            Kc0 = Kc
            self._write_field("PID_%s_P"%X, self.pid_helpers["%s_P"%X].to_f(Kc0))
            self._write_field("PID_%s_I"%X, self.pid_helpers["%s_I"%X].to_f(0.0))
        else:
            Kc0 = from_q4_12(self._read_field("PID_%s_P"%X))
        # Do a setpoint change experiment
        self._write_field("PID_%s_TARGET"%X, 0)
        logging.info("test_cur = %d"%test_cur)
        n = 100
        c = self._dump_pid(n, X)
        self._write_field("PID_%s_TARGET"%X, test_cur)
        c += self._dump_pid(n, X)
        # Experiment over, switch off
        self._write_field("PID_%s_TARGET"%X, 0)
        # Put motion config back how it was
        self._write_field("PID_TORQUE_TARGET", 0)
        self._write_field("PID_VELOCITY_TARGET", 0)
        self._write_field("PID_POSITION_TARGET", 0)
        self._write_field("PID_POSITION_ACTUAL", 0)
        self._write_field("MODE_MOTION", old_mode)
        self._write_field("PID_FLUX_OFFSET", old_flux_offset)
        self._write_field("PHI_E_SELECTION", old_phi_e_selection)
        # Analysis and logging
        #for r in c:
        #    logging.info("%g,%s"%(float(r[0]-c[0][0])/1e9,','.join(map(str, r[1:]))))
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
        #tp -= float(c[n][0] + c[n+1][0])/2.0
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
        if not test_existing:
            self._write_field("PID_%s_P"%X, self.pid_helpers["%s_P"%X].to_f(Kc))
            self._write_field("PID_%s_I"%X, self.pid_helpers["%s_I"%X].to_f(Ki))
            # Store results for SAVE_CONFIG
            cfgname = "tmc4671 %s" % (self.name,)
            configfile = self.printer.lookup_object('configfile')
            configfile.set(cfgname, 'foc_PID_FLUX_P', "%.3f" % (Kc,))
            configfile.set(cfgname, 'foc_PID_FLUX_I', "%.3f" % (Ki,))
            configfile.set(cfgname, 'foc_PID_TORQUE_P', "%.3f" % (Kc,))
            configfile.set(cfgname, 'foc_PID_TORQUE_I', "%.3f" % (Ki,))
        return Kc, Ki

    def _dump_pid(self, n, X):
        f = "PID_%s_ACTUAL"%X
        c = [(0,0)]*(n)
        for i in range(n):
            cur = self._read_field(f)
            c[i]=(monotonic_ns(), cur,)
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
            self._write_field("PID_FLUX_TARGET", 0)
            self._write_field("PID_TORQUE_TARGET", 0)
            self._write_field("PID_VELOCITY_TARGET", 0)
            self._write_field("PID_POSITION_TARGET", 0)
            self._write_field("PWM_CHOP", 7)
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
        params = None

        logging.info(
            "Setting up biquad filter: register=%s, enabled=%s, filter=%s",
            register,
            enabled,
            biquad_filter,
        )

        freq_s = self.pwmfreq
        if register == "CONFIG_BIQUAD_X_ENABLE":
            freq_s = self.pwmfreq/(self._read_field("MODE_PID_SMPL")+1.0)

        if biquad_filter.type == "lpf":
            params = biquad_lpf(freq_s, biquad_filter.freq, biquad_filter.slope)
        elif biquad_filter.type == "notch":
            params = biquad_notch(freq_s, biquad_filter.freq, biquad_filter.slope)
        elif biquad_filter.type == "apf":
            params = biquad_apf(freq_s, biquad_filter.freq, biquad_filter.slope)

        if enabled and params is not None:
            self.enable_biquad(register, *biquad_tmc(*params))

        self._write_field(register, enabled)

    def _setup_filters(self) -> None:
        for target, biquad_filter in self.biquad_filters.items():
            register = BIQUAD_FILTER_TARGETS[target]
            self._setup_filter(register, biquad_filter)

    def get_status(self, eventtime=None):
        if not self.init_done:
            return {}
        current = self.current_helper.get_current()
        res = {'run_current': current[0],
               'current_ux': current[2],
               'current_v': current[3],
               'current_wy': current[4],
               }
        for reg_name in DumpGroups["monitor"]:
            val = self.mcu_tmc.get_register(reg_name)
            self.monitor_data.update(self.fields.get_reg_fields(reg_name, val))
        res.update(self.monitor_data)
        res.update(self.error_helper.get_status(eventtime))
        return res

    cmd_INIT_TMC_help = "Initialize TMC stepper driver registers"
    def cmd_INIT_TMC(self, gcmd):
        logging.info("INIT_TMC %s", self.name)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self._init_registers(print_time)

    cmd_TMC_TUNE_MOTION_PID_help = "Tune the current and torque PID coefficients"
    def cmd_TMC_TUNE_MOTION_PID(self, gcmd):
        l_v = gcmd.get_float('LAMBDA_V', 100)
        l_p = gcmd.get_float('LAMBDA_P', 400)
        I_h = gcmd.get_float('HOLDING_CURRENT', None)
        T_h = gcmd.get_float('HOLDING_TORQUE', None)
        Kt = gcmd.get_float('KT', None)
        if Kt is None:
            if (I_h is None or T_h is None):
                gcmd.respond_info("Must supply KT or both HOLDING_TORQUE and HOLDING_CURRENT.")
                return
            Kt = T_h / I_h
        Kadc = self.current_helper.current_scale * 1e-3
        NPP = self._read_field("N_POLE_PAIRS")
        rotation_distance, _ = self.stepper.get_rotation_distance()
        t_d = 1.

        k_v = Kadc / (Kt * math.pi)
        t_iv = 2.*l_v + t_d
        p_v = t_iv / (k_v * (l_v + t_d) ** 2)
        i_v = 1. / t_iv

        k_p = NPP / (256. * 50.)
        t_ip = 2.*l_p + t_d
        p_p = t_ip / (k_p * (l_p + t_d) ** 2)
        i_p = 1. / t_ip

        self._write_field("PID_VELOCITY_P", self.pid_helpers["VELOCITY_P"].to_f(p_v))
        self._write_field("PID_VELOCITY_I", self.pid_helpers["VELOCITY_I"].to_f(i_v))
        self._write_field("PID_POSITION_P", self.pid_helpers["POSITION_P"].to_f(p_p))
        self._write_field("PID_POSITION_I", self.pid_helpers["POSITION_I"].to_f(i_p))
        # Store results for SAVE_CONFIG
        cfgname = "tmc4671 %s" % (self.name,)
        configfile = self.printer.lookup_object('configfile')
        configfile.set(cfgname, 'foc_PID_VELOCITY_P', "%.3f" % (p_v,))
        configfile.set(cfgname, 'foc_PID_VELOCITY_I', "%.3f" % (i_v,))
        configfile.set(cfgname, 'foc_PID_POSITION_P', "%.3f" % (p_p,))
        configfile.set(cfgname, 'foc_PID_POSITION_I', "%.3f" % (i_p,))

        gcmd.respond_info(
            "PID %s parameters calculated.\n"
            "k_v=%.5f k_p=%.5f\n KT=%.5f\n"
            "p_v=%.5f i_v=%.5f p_p=%.5f i_p=%.5f\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with these parameters and restart the printer.\n"
            "Suggested torque and velocity filter frequency: %d\n"
            % (self.name, k_v, k_p, Kt, p_v, i_v, p_p, i_p, 3.0*self.pwmfreq / l_v))

    cmd_TMC_TUNE_PID_help = "Tune the current and torque PID coefficients"
    def cmd_TMC_TUNE_PID(self, gcmd):
        test_existing = gcmd.get_int('CHECK', 0)
        derate = gcmd.get_float('DERATE', 1.6)
        logging.info("TMC_TUNE_PID %s", self.name)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        with self.mutex:
            P, I = self._tune_flux_pid(test_existing, derate, print_time)
            self._write_field("PID_TORQUE_P", self.pid_helpers["TORQUE_P"].to_f(P))
            self._write_field("PID_TORQUE_I", self.pid_helpers["TORQUE_I"].to_f(I))
        gcmd.respond_info(
            "PID %s parameters: Kc=%.2f Ki=%.3f\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with these parameters and restart the printer." % (self.name, P, I))

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
            #self._write_field("PWM_CHOP", 7)
            old_mode = self._read_field("MODE_MOTION")
            self._write_field("PID_POSITION_ACTUAL", 0)
            self.printer.lookup_object('toolhead').dwell(0.2)
            # Clear all the status flags for later reference
            self.mcu_tmc.set_register_once(reg, 0, print_time)
            limit_cur = self._read_field("PID_TORQUE_FLUX_LIMITS")
            self._write_field("PID_FLUX_TARGET", 0)
            self._write_field("PID_TORQUE_TARGET", 0)
            self._write_field(target_reg, 0)
            self._write_field("MODE_MOTION", mode)
            n2 = 20
            if mode == MotionMode.stopped_mode:
                v = [velocity * i // (2*n2) for i in range(n2,2*n2)] + [velocity for i in range(n2*2)]
            else:
                v = [velocity for i in range(n2,2*n2)] + [velocity for i in range(n2*2)]
            n = 500
            c = self._dump_motion(n, f=lambda x : self._write_field(target_reg, x), v=v)
            self._write_field("MODE_MOTION", old_mode)
            self._write_field(target_reg, 0)
            #self._write_field("PWM_CHOP", 0)
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
                  self._read_field("PID_POSITION_ACTUAL"),
                  self._read_field("PID_VELOCITY_ACTUAL"),
                  self._read_field("PID_ERROR_PID_VELOCITY_ERROR"),
                  self._read_field("INTERIM_PIDIN_TARGET_TORQUE"),
                  self._read_field("PID_TORQUE_ACTUAL"),
                  self._read_field("PID_ERROR_PID_TORQUE_ERROR"),
                  self._read_field("PID_ERROR_PID_TORQUE_ERROR_SUM"),
                  self._read_field("INTERIM_PIDIN_TARGET_FLUX"),
                  self._read_field("PID_FLUX_ACTUAL"),
                  self._read_field("PID_ERROR_PID_FLUX_ERROR"),
                  self._read_field("PID_ERROR_PID_FLUX_ERROR_SUM"),
                  ":::",
                  self._read_field("ADC_I0_RAW"),
                  self._read_field("ADC_I1_RAW"),
                  self._read_field("ADC_IUX"),
                  self._read_field("INTERIM_PWM_UX"),
                  self._read_field("ADC_IV"),
                  self._read_field("INTERIM_PWM_UV"),
                  self._read_field("ADC_IWY"),
                  self._read_field("INTERIM_PWM_WY"),
                  ":::",
                  self._read_field("ABN_DECODER_PHI_M")%65536,
                  self._read_field("ABN_DECODER_PHI_E")%65536,
                  self._read_field("HALL_PHI_M")%65536,
                  self._read_field("HALL_PHI_E")%65536,
                  self._read_field("PHI_E")%65536,
                  (self._read_field("PHI_E")-self._read_field("HALL_PHI_E")) % 65536,
                  (self._read_field("PHI_E")-self._read_field("ABN_DECODER_PHI_E")) % 65536,
                  )
            self.printer.lookup_object('toolhead').dwell(15./n)
        return c

    def _debug_openloop_velocity_motion(self, velocity, print_time):
        with self.mutex:
            self._write_field("PWM_CHOP", 7)
            self._write_field("MODE_MOTION", MotionMode.uq_ud_ext_mode)
            limit_cur = self._read_field("PID_TORQUE_FLUX_LIMITS")
            self._write_field("UD_EXT", limit_cur)
            self._write_field("UQ_EXT", 0)
            old_phi_e_sel = self._read_field("PHI_E_SELECTION")
            self._write_field("PHI_E_SELECTION", 2)
            phi_e = self._read_field("PHI_E")
            # Clear all the status flags for later reference
            self.mcu_tmc.set_register_once(reg, 0, print_time)
            # might not stick, so write with a one-shot
            n = 500
            self._write_field("OPENLOOP_VELOCITY_TARGET", velocity)
            self._write_field("OPENLOOP_ACCELERATION", 1000)
            c = self._dump_motion(n)
            self._write_field("OPENLOOP_VELOCITY_TARGET", 0)
            self._write_field("OPENLOOP_ACCELERATION", 0)
            self.printer.lookup_object('toolhead').dwell(0.2)
            self._write_field("MODE_MOTION", MotionMode.stopped_mode)
            self._write_field("PHI_E_SELECTION", old_phi_e_sel)
            self._write_field("PWM_CHOP", 0)
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
        prev_cur, max_cur = ch.get_current()
        run_current = gcmd.get_float('CURRENT', None, minval=0., maxval=max_cur)
        if run_current is not None:
            with self.mutex:
                reg_val = ch.set_current(run_current)
                prev_cur, max_cur = ch.get_current()
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

        freq = gcmd.get_int(
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

def load_config_prefix(config):
    return TMC4671(config)
