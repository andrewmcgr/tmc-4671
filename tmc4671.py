# TMC4671 configuration
import logging, collections
import math
from time import monotonic_ns
from enum import IntEnum
from . import bus, tmc

TMC_FREQUENCY=25000000.

# Some magic numbers for the driver

class MotionMode(IntEnum):
    stopped_mode = 0
    torque_mode = 1
    velocity_mode = 2
    position_mode = 3

# Tuple is the address followed by a value to put in the next higher address to select that sub-register, or none to just go straight there.

# Register map for the 6100 companion chip
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

# Register map for the 4671 itself
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
    "ADC_I0": 0xf,
    "ADC_I1": 0xf << 4,
    "ADC_VM": 0xf << 8,
    "ADC_AGPI_A": 0xf << 12,
    "ADC_AGPI_B": 0xf << 16,
    "ADC_AENC_UX": 0xf << 20,
    "ADC_AENC_VN": 0xf << 24,
    "ADC_AENC_WY": 0xf << 28,
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

# TODO: CONFIG_DATA
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

# TODO: if necessary, INTERIM_DATA

Fields["ADC_VM_LIMITS"] = {
    "ADC_VM_LIMIT_LOW": 0xffff,
    "ADC_VM_LIMIT_HIGH": 0xffff << 16
}

# TODO: if necessary, TMC467_*_RAW
# TODO: if necessary, GPIO_dsADCI_CONFIG

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

# TODO: interim data fields
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
                "AENC_DECODER_PHI_E", "PHI_E", "PID_FLUX_I", "PID_FLUX_P",
                "PID_TORQUE_I", "PID_TORQUE_P", "PID_VELOCITY_I",
                "PID_VELOCITY_P", "PID_POSITION_I", "PID_POSITION_P",
                "PIDOUT_UQ_UD_LIMITS", "PID_POSITION_LIMIT_LOW",
                "PID_POSITION_LIMIT_HIGH", "PID_FLUX_TARGET",
                "PID_TORQUE_TARGET", "PID_FLUX_OFFSET", "PID_TORQUE_OFFSET",
                "PID_VELOCITY_TARGET", "PID_VELOCITY_OFFSET",
                "PID_POSITION_TARGET", "PID_FLUX_ACTUAL", "PID_TORQUE_ACTUAL",
                "PID_VELOCITY_ACTUAL", "PID_POSITION_ACTUAL",
                "PID_TORQUE_ERROR", "PID_FLUX_ERROR", "PID_VELOCITY_ERROR",
                "PID_POSITION_ERROR", "PID_TORQUE_ERROR_SUM",
                "PID_FLUX_ERROR_SUM", "PID_VELOCITY_ERROR_SUM",
                "PID_POSITION_ERROR_SUM", "STEP_WIDTH"}

def format_phi(val):
    phi = (val * 360.0 / 65536.0)
    if phi < 0.0:
        phi += 360
    return "%.3f" % (phi)

def format_q4_12(val):
    return "%.4f" % (val * 2**-12)

def to_q4_12(val):
    return round(val * 2**12) & 0xffff

def format_q0_15(val):
    return "%.7f" % (val * 2**-15)

def format_q8_8(val):
    return "%.3f" % (val * 2**-8)

def to_q8_8(val):
    return round(val * 2**8) & 0xffff

def format_q3_29(val):
    return "%.9f" % (val * 2**-29)

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
}

DumpGroups = {
    "Default": ["CHIPINFO_SI_TYPE", "CHIPINFO_SI_VERSION",
                "STATUS_FLAGS", "PHI_E"],
    "HALL": ["HALL_MODE", "HALL_POSITION_060_000", "HALL_POSITION_180_120",
             "HALL_POSITION_300_240", "HALL_PHI_E_INTERPOLATED_PHI_E",
             "HALL_PHI_E_PHI_M_OFFSET", "HALL_PHI_M",],
    "AENC": ["AENC_DECODER_MODE",
             "AENC_DECODER_PPR", "ADC_I1_RAW_ADC_I0_RAW",
             "ADC_AGPI_A_RAW_ADC_VM_RAW", "ADC_AENC_UX_RAW_ADC_AGPI_B_RAW",
             "ADC_AENC_WY_RAW_ADC_AENC_VN_RAW", "AENC_DECODER_PHI_A_RAW"],
    "PWM": ["PWM_POLARITIES", "PWM_MAXCNT", "PWM_BBM_H_BBM_L", "PWM_SV_CHOP",
            "MOTOR_TYPE_N_POLE_PAIRS"],
    "STEP": ["STEP_WIDTH", "PHI_E", "MODE_RAMP_MODE_MOTION", "STATUS_FLAGS",
             "PID_POSITION_TARGET"],
    "FILTERS": [ "CONFIG_BIQUAD_X_A_1", "CONFIG_BIQUAD_X_A_2",
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

# Z-transform and normalise a biquad filter, according to TMC
def biquad_tmc(T, b0, b1, b2, a0, a1, a2):
    den = (T**2 - 2*a1 + 4*a2)
    b2z = (b0*T**2 + 2*b1*T + 4*b2) / den
    b1z = (2*b0*T**2 - 8*b2) / den
    b0z = (b0*T**2 - 2*b1*T + 4*b2) / den
    a2z = (T**2 + 2*a1*T + 4*a2) / den
    a1z = (2*T**2 - 8*a2) / den
    e29 = 2**29
    b0 = round(b0z * e29)
    b1 = round(b1z * e29)
    b2 = round(b2z * e29)
    a1 = round(-a1z * e29)
    a2 = round(-a2z * e29)
    # return in the same order as the config registers
    return a1, a2, b0, b1, b2

# S-IMC PI controller design
def simc(k, theta, tau1, tauc):
    Kc = (1.0/k) * (tau1/(tauc + theta))
    taui = min(tau1, 4*(tauc + theta))
    return Kc, taui

# Return the position of the first bit set in a mask
def ffs(mask):
    return (mask & -mask).bit_length() - 1

class FieldHelper:
    def __init__(self, all_fields, signed_fields=[], field_formatters={},
                 registers=None, prefix="driver_"):
        self.all_fields = all_fields
        self.signed_fields = {sf: 1 for sf in signed_fields}
        self.field_formatters = field_formatters
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
        if reg_name == field_name:
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
    def set_config_field(self, config, field_name, default):
        # Allow a field to be set from the config file
        config_name = self.prefix + field_name
        reg_name = self.lookup_register(field_name)
        if reg_name == field_name:
            mask = 0xffffffff
        else:
            mask = self.all_fields[reg_name][field_name]
        maxval = mask >> ffs(mask)
        if maxval == 1:
            val = config.getboolean(config_name, default)
        elif field_name in self.signed_fields:
            val = config.getint(config_name, default,
                                minval=-(maxval//2 + 1), maxval=maxval//2)
        else:
            val = config.getint(config_name, default, minval=0, maxval=maxval)
        return self.set_field(field_name, val, reg_name=reg_name)
    def pretty_format(self, reg_name, reg_value):
        # Provide a string description of a register
        reg_fields = self.all_fields.get(reg_name, {reg_name: 0xffffffff})
        reg_fields = sorted([(mask, name) for name, mask in reg_fields.items()])
        fields = []
        for mask, field_name in reg_fields:
            field_value = self.get_field(field_name, reg_value, reg_name)
            sval = self.field_formatters.get(field_name, str)(field_value)
            if sval and sval != "0":
                fields.append(" %s=%s" % (field_name, sval))
        return "%-11s %08x%s" % (reg_name + ":", reg_value, "".join(fields))
    def get_reg_fields(self, reg_name, reg_value):
        # Provide fields found in a register
        reg_fields = self.all_fields.get(reg_name, {})
        return {field_name: self.get_field(field_name, reg_value, reg_name)
                for field_name, mask in reg_fields.items()}

# TODO: actually make this do something
MAX_CURRENT = 10.000

class CurrentHelper:
    def __init__(self, config, mcu_tmc):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.mcu_tmc = mcu_tmc
        self.fields = mcu_tmc.get_fields()
        self.run_current = config.getfloat('run_current',
                                      above=0., maxval=MAX_CURRENT)
        self.current_scale = config.getfloat('current_scale_ma_lsb', 1.272e-3,
                                       above=0., maxval=10e-3)
        self.flux_limit = self._calc_flux_limit(self.run_current)
        self.fields.set_field("PID_TORQUE_FLUX_LIMITS", self.flux_limit)
    def _calc_flux_limit(self, current):
        flux_limit = int(current // self.current_scale)
        if flux_limit > 0xffff:
            return 0xffff
        return flux_limit
    def convert_adc_current(self, adc):
        return adc * self.current_scale
    def get_current(self):
        c = self.convert_adc_current(self.fields.get_field("PID_TORQUE_FLUX_LIMITS"))
        return c, MAX_CURRENT
    def set_current(self, run_current):
        self.run_current = run_current
        self.flux_limit = self._calc_flux_limit(self.run_current)
        self.fields.set_field("PID_TORQUE_FLUX_LIMITS", self.flux_limit)
        return self.flux_limit

# Helper to configure the microstep settings
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
            "Product of res and mres must be less than 65536 for [%s]"
            % (stepper_name,))
    step_width = 65536 // (res * mres)
    fields.set_field("STEP_WIDTH", step_width)

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
        self.spi.spi_send(cmd)
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
            "Unable to write tmc spi '%s' register %s" % (self.name, reg_name))
    def get_tmc_frequency(self):
        return self.tmc_frequency

class TMC4671:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.fields = FieldHelper(Fields,
                                  signed_fields=SignedFields,
                                  field_formatters=FieldFormatters,
                                  prefix="foc_")
        # TODO: make 6100 optional for boards without one.
        self.fields6100 = FieldHelper(Fields6100, prefix="drv_")
        self.mcu_tmc = MCU_TMC_SPI(config, Registers, self.fields,
                                   TMC_FREQUENCY, pin_option="cs_pin")
        self.mcu_tmc6100 = MCU_TMC_SPI(config, Registers6100, self.fields6100,
                                       12e6, pin_option="drv_cs_pin")
        self.read_translate = None
        self.read_registers = Registers.keys()
        self.printer.register_event_handler("klippy:connect",
                                            self._handle_connect)
        # Register commands
        self.step_helper = StepHelper(config, self.mcu_tmc)
        self.current_helper = CurrentHelper(config, self.mcu_tmc)
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command("SET_TMC_FIELD", "STEPPER", self.name,
                                   self.cmd_SET_TMC_FIELD,
                                   desc=self.cmd_SET_TMC_FIELD_help)
        gcode.register_mux_command("DUMP_TMC", "STEPPER", self.name,
                                   self.cmd_DUMP_TMC,
                                   desc=self.cmd_DUMP_TMC_help)
        gcode.register_mux_command("DUMP_TMC6100", "STEPPER", self.name,
                                   self.cmd_DUMP_TMC6100,
                                   desc=self.cmd_DUMP_TMC6100_help)
        gcode.register_mux_command("TMC_TUNE_PID", "STEPPER", self.name,
                                   self.cmd_TMC_TUNE_PID,
                                   desc=self.cmd_TMC_TUNE_PID_help)
        gcode.register_mux_command("INIT_TMC", "STEPPER", self.name,
                                   self.cmd_INIT_TMC,
                                   desc=self.cmd_INIT_TMC_help)
        gcode.register_mux_command("SET_TMC_CURRENT", "STEPPER", self.name,
                                   self.cmd_SET_TMC_CURRENT,
                                   desc=self.cmd_SET_TMC_CURRENT_help)
        # Allow other registers to be set from the config
        set_config_field = self.fields.set_config_field
        set_config6100_field = self.fields6100.set_config_field
        # defaults as per 4671+6100 BOB datasheet
        set_config6100_field(config, "singleline", 0)
        set_config6100_field(config, "normal", 1)
        set_config6100_field(config, "DRVSTRENGTH", 0)
        set_config6100_field(config, "BBMCLKS", 10)
        # This should not really be set to anything else
        # therefore not providing convenience interface
        set_config_field(config, "PWM_MAXCNT", 0xF9F) # 25 kHz
        # These are used later by filter definitions
        self.pwmfreq = 4.0 * TMC_FREQUENCY / (self.fields.get_field("PWM_MAXCNT") + 1)
        self.pwmT = 1.0 / self.pwmfreq
        set_config_field(config, "PWM_BBM_L", 10)
        set_config_field(config, "PWM_BBM_H", 10)
        set_config_field(config, "PWM_CHOP", 7)
        set_config_field(config, "PWM_SV", 1)
        set_config_field(config, "MOTOR_TYPE", 3)
        set_config_field(config, "N_POLE_PAIRS", 4)
        set_config_field(config, "AENC_DEG", 1)    # 120 degree analog hall
        set_config_field(config, "AENC_PPR", 1)    # 120 degree analog hall
        set_config_field(config, "HALL_INTERP", 0)
        set_config_field(config, "HALL_BLANK", 8)
        set_config_field(config, "PHI_E_SELECTION", 5) # digital hall PHI_E
        set_config_field(config, "POSITION_SELECTION", 12) # digital hall PHI_M
        set_config_field(config, "VELOCITY_SELECTION", 12) # digital hall PHI_M
        set_config_field(config, "VELOCITY_METER_SELECTION", 1) # PWM frequency velocity meter
        set_config_field(config, "CURRENT_I_n", 0) # q8.8
        set_config_field(config, "CURRENT_P_n", 0) # q8.8
        set_config_field(config, "VELOCITY_I_n", 1) # q4.12
        set_config_field(config, "VELOCITY_P_n", 1) # q4.12
        set_config_field(config, "POSITION_I_n", 1) # q4.12
        set_config_field(config, "POSITION_P_n", 1) # q4.12
        set_config_field(config, "MODE_PID_SMPL", 1) # Advanced PID samples position at fPWM
        set_config_field(config, "MODE_PID_TYPE", 1) # Advanced PID mode
        set_config_field(config, "PIDOUT_UQ_UD_LIMITS", 30000) # Voltage limit, 32768 = Vm

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

    # Intended to be called, e.g. like this:
    # self.enable_biquad("CONFIG_BIQUAD_X_ENABLE", *biquad_tmc(self.pwmT, *biquad_lpf(self.pwmfreq, 5e3, 0.7)))
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

    def _handle_connect(self):
        # Check if using step on both edges optimization
        #pulse_duration, step_both_edge = self.stepper.get_pulse_duration()
        #if step_both_edge:
        #    self.fields.set_field("dedge", 1)
        # Send init
        try:
            self._init_registers()
        except self.printer.command_error as e:
            logging.info("TMC %s failed to init: %s", self.name, str(e))

    def _calibrate_adc(self, print_time):
        self.fields.set_field("ADC_I_UX_SELECT", 0)
        self.fields.set_field("ADC_I_V_SELECT", 1)
        self.fields.set_field("ADC_I_WY_SELECT", 2)
        self.fields.set_field("ADC_I0_SELECT", 0)
        self.mcu_tmc.set_register("ADC_I_SELECT",
                                  self.fields.set_field("ADC_I1_SELECT", 1),
                                  print_time)
        self.fields.set_field("ADC_I1_SCALE", 256),
        self.fields.set_field("ADC_I0_SCALE", 256),
        reg, addr = self.mcu_tmc.name_to_reg["ADC_I1_RAW_ADC_I0_RAW"]
        self.mcu_tmc.tmc_spi.reg_write(reg+1, addr)
        i1sum = 0
        i0sum = 0
        n = 50
        for i in range(n):
            v = self.fields.get_reg_fields("ADC_I1_RAW_ADC_I0_RAW",
                                           self.mcu_tmc.tmc_spi.reg_read(reg))
            i1sum += v["ADC_I1_RAW"]
            i0sum += v["ADC_I0_RAW"]
            self.printer.lookup_object('toolhead').dwell(0.005)
        i1_off = i1sum // n
        i0_off = i0sum // n
        self.mcu_tmc.set_register("ADC_I1_SCALE_OFFSET",
                                  self.fields.set_field("ADC_I1_OFFSET", i1_off),
                                  print_time)
        self.mcu_tmc.set_register("ADC_I0_SCALE_OFFSET",
                                  self.fields.set_field("ADC_I0_OFFSET", i0_off),
                                  print_time)
        logging.info("TMC 4671 %s ADC offsets I0=%d I1=%d", self.name, i0_off, i1_off)

    def _tune_flux_pid(self, print_time):
        ch = self.current_helper
        self._write_field("CONFIG_BIQUAD_X_ENABLE", 0)
        old_phi_e_selection = self._read_field("PHI_E_SELECTION")
        self._write_field("PHI_E_SELECTION", 1) # external mode, so it won't change.
        self._write_field("MODE_MOTION", MotionMode.torque_mode)
        limit_cur = self._read_field("PID_TORQUE_FLUX_LIMITS")
        test_cur = limit_cur // 2
        not_done = True
        old_cur = self._read_field("PID_FLUX_ACTUAL")
        self._write_field("PWM_CHOP", 7)
        self._write_field("PID_FLUX_P", to_q4_12(0.75))
        self._write_field("PID_FLUX_I", to_q4_12(0.0))
        self._write_field("PID_FLUX_TARGET", 0)
        logging.info("test_cur = %d"%test_cur)
        n = 25
        c = [(0,0)]*(n*2)
        for i in range(n):
            cur = self._read_field("PID_FLUX_ACTUAL")
            c[i]=(monotonic_ns(), cur,)
        self._write_field("PID_FLUX_TARGET", test_cur)
        for i in range(n,2*n):
            cur = self._read_field("PID_FLUX_ACTUAL")
            c[i]=(monotonic_ns(), cur,)
        # Experiment over, switch off
        self._write_field("PID_FLUX_TARGET", 0)
        self._write_field("MODE_MOTION", MotionMode.stopped_mode)
        self._write_field("PWM_CHOP", 0)
        self._write_field("PHI_E_SELECTION", old_phi_e_selection) # restore it
        # Analysis and logging
        #for i in range(2*n):
        #    logging.info(",".join(map(str, c[i])))
        # At this point we can determine system model
        yinf = sum(a[1] for a in c[3*n//2:2*n])/float(2*n - 3*n//2) - sum(a[1] for a in c[0:n])/float(n)
        k = 1.0/(0.75*abs((1.0*test_cur-yinf)/yinf))
        theta = 1.0/25e3
        # TODO: calculate this from motor constants
        tau1 = 700e-6
        logging.info("TMC 4671 %s Flux system model k=%g, theta=%g, tau1=%g"%(self.name, k, theta, tau1,))
        Kc, taui = simc(k, theta, tau1, theta)
        logging.info("TMC 4671 %s Flux PID coefficients Kc=%g, Ti=%g"%(self.name, Kc, taui))
        self._write_field("PID_FLUX_P", to_q8_8(Kc))
        self._write_field("PID_FLUX_I", to_q8_8(Kc/taui))

    def _init_registers(self, print_time=None):
        if print_time is None:
            print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        ping = self.mcu_tmc.get_register("CHIPINFO_SI_TYPE")
        if ping != 0x34363731:
            raise self.printer.command_error(
                "TMC 4671 not identified, identification register returned %x" % (ping,))
        # Disable 6100
        self.mcu_tmc6100.set_register("GCONF",
                                      self.fields6100.set_field("disable", 1),
                                      print_time)
        # Set torque and current in 4671 to zero
        self.mcu_tmc.set_register("PID_TORQUE_FLUX_TARGET",
                                  self.fields.set_field("PID_TORQUE_TARGET", 0),
                                  print_time)
        self.mcu_tmc.set_register("PID_TORQUE_FLUX_TARGET",
                                  self.fields.set_field("PID_FLUX_TARGET", 0),
                                  print_time)
        # Send registers, 6100 first then 4671
        for reg_name in list(self.fields6100.registers.keys()):
            val = self.fields6100.registers[reg_name] # Val may change during loop
            self.mcu_tmc6100.set_register(reg_name, val, print_time)
        for reg_name in list(self.fields.registers.keys()):
            val = self.fields.registers[reg_name] # Val may change during loop
            self.mcu_tmc.set_register(reg_name, val, print_time)
        self._calibrate_adc(print_time)
        self._tune_flux_pid(print_time)
        # setup filters
        self.enable_biquad("CONFIG_BIQUAD_X_ENABLE",
                           *biquad_tmc(self.pwmT,
                                       *biquad_lpf(self.pwmfreq, 5e3, 2**-0.5)))
        # Now enable 6100
        self.mcu_tmc6100.set_register("GCONF",
                                      self.fields6100.set_field("disable", 0),
                                      print_time)

    cmd_INIT_TMC_help = "Initialize TMC stepper driver registers"
    def cmd_INIT_TMC(self, gcmd):
        logging.info("INIT_TMC %s", self.name)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self._init_registers(print_time)

    cmd_TMC_TUNE_PID_help = "Initialize TMC stepper driver registers"
    def cmd_TMC_TUNE_PID(self, gcmd):
        logging.info("TMC_TUNE_PID %s", self.name)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self._tune_flux_pid(print_time)

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
            group = gcmd.get('GROUP', 'Default')
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
            group = gcmd.get('GROUP', 'Default')
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
        velocity = gcmd.get_float('VELOCITY', None, minval=0.)
        if (value is None) == (velocity is None):
            raise gcmd.error("Specify either VALUE or VELOCITY")
        if velocity is not None:
            if self.mcu_tmc.get_tmc_frequency() is None:
                raise gcmd.error(
                    "VELOCITY parameter not supported by this driver")
            value = TMCtstepHelper(self.mcu_tmc, velocity,
                                   pstepper=self.stepper)
        reg_val = self.fields.set_field(field_name, value)
        print_time = self.printer.lookup_object('toolhead').get_last_move_time()
        self.mcu_tmc.set_register(reg_name, reg_val, print_time)

    cmd_SET_TMC_CURRENT_help = "Set the current of a TMC driver"
    def cmd_SET_TMC_CURRENT(self, gcmd):
        ch = self.current_helper
        prev_cur, max_cur = ch.get_current()
        run_current = gcmd.get_float('CURRENT', None, minval=0., maxval=max_cur)
        if run_current is not None:
            reg_val = ch.set_current(run_current)
            prev_cur, max_cur = ch.get_current()
            print_time = self.printer.lookup_object('toolhead').get_last_move_time()
            self.mcu_tmc.set_register("PID_TORQUE_FLUX_LIMITS", reg_val, print_time)
        gcmd.respond_info("Run Current: %0.2fA" % (prev_cur,))


def load_config_prefix(config):
    return TMC4671(config)
