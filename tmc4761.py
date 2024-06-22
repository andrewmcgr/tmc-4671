# TMC4671 configuration
from . import bus, tmc

# If this is a number, it's just the address
# If a tuple, it's the address followed by a value to put in the next higher address to select that sub-register.

Registers = {
    "CHIPINFO_DATA": (0x00, None) # R,Test
    "CHIPINFO_ADDR": (0x01, None) # RW,Test

    "CHIPINFO_SI_TYPE": (0x00, 0),
    "CHIPINFO_SI_VERSION": (0x00, 1),
    "CHIPINFO_SI_DATE": (0x00, 2),
    "CHIPINFO_SI_TIME": (0x00, 3),
    "CHIPINFO_SI_VARIANT": (0x00, 4),
    "CHIPINFO_SI_BUILD": (0x00, 5),

    "ADC_RAW_DATA": (0x02, None) # R,Monitor
    "ADC_RAW_ADDR": (0x03, None) # RW,Monitor

    "ADC_I1_RAW_ADC_I0_RAW": (0x02, 0),
    "ADC_AGPI_A_RAW_ADC_VM_RAW": (0x02, 1),
    "ADC_AENC_UX_RAW_ADC_AGPI_B_RAW": (0x02, 2),
    "ADC_AENC_WY_RAW_ADC_AENC_VN_RAW": (0x02, 3),

    "dsADC_MCFG_B_MCFG_A": (0x04, None) # RW,Init
    "dsADC_MCLK_A": (0x05, None) # RW,Init
    "dsADC_MCLK_B": (0x06, None) # RW,Init
    "dsADC_MDEC_B_MDEC_A": (0x07, None) # RW,Init
    "ADC_I1_SCALE_OFFSET": (0x08, None) # RW,Init
    "ADC_I0_SCALE_OFFSET": (0x09, None) # RW,Init
    "ADC_I_SELECT": (0x0A, None) # RW,Init
    "ADC_I1_I0_EXT": (0x0B, None) # RW,Test
    "DS_ANALOG_INPUT_STAGE_CFG": (0x0C, None) # RW,Test
    "AENC_0_SCALE_OFFSET": (0x0D, None) # RW,Init
    "AENC_1_SCALE_OFFSET": (0x0E, None) # RW,Init
    "AENC_2_SCALE_OFFSET": (0x0F, None) # RW,Init
    "AENC_SELECT": (0x11, None) # RW,Init
    "ADC_IWY_IUX": (0x12, None) # R,Monitor
    "ADC_IV": (0x13, None) # R,Monitor
    "AENC_WY_UX": (0x15, None) # R,Monitor
    "AENC_VN": (0x16, None) # R,Monitor
    "PWM_POLARITIES": (0x17, None) # RW,Init
    "PWM_MAXCNT": (0x18, None) # RW,Init
    "PWM_BBM_H_BBM_L": (0x19, None) # RW,Init
    "PWM_SV_CHOP": (0x1A, None) # RW,Init
    "MOTOR_TYPE_N_POLE_PAIRS": (0x1B, None) # RW,Init
    "PHI_E_EXT": (0x1C, None) # RW,Test
    "OPENLOOP_MODE": (0x1F, None) # RW,Init
    "OPENLOOP_ACCELERATION": (0x20, None) # RW,Init
    "OPENLOOP_VELOCITY_TARGET": (0x21, None) # RW,Init
    "OPENLOOP_VELOCITY_ACTUAL": (0x22, None) # RW,Monitor
    "OPENLOOP_PHI": (0x23, None) # RW,Monitor/Test
    "UQ_UD_EXT": (0x24, None) # RW,Init/Test
    "ABN_DECODER_MODE": (0x25, None) # RW,Init
    "ABN_DECODER_PPR": (0x26, None) # RW,Init
    "ABN_DECODER_COUNT": (0x27, None) # RW,Init/Test/Monitor
    "ABN_DECODER_COUNT_N": (0x28, None) # RW,Init/Test/Monitor
    "ABN_DECODER_PHI_E_PHI_M_OFFSET": (0x29, None) # RW,Init
    "ABN_DECODER_PHI_E_PHI_M": (0x2A, None) # R,Monitor
    "ABN_2_DECODER_MODE": (0x2C, None) # RW,Init
    "ABN_2_DECODER_PPR": (0x2D, None) # RW,Init
    "ABN_2_DECODER_COUNT": (0x2E, None) # RW,Init/Test/Monitor
    "ABN_2_DECODER_COUNT_N": (0x2F, None) # RW,Init/Test/Monitor
    "ABN_2_DECODER_PHI_M_OFFSET": (0x30, None) # RW,Init
    "ABN_2_DECODER_PHI_M": (0x31, None) # R,Monitor
    "HALL_MODE": (0x33, None) # RW,Init
    "HALL_POSITION_060_000": (0x34, None) # RW,Init
    "HALL_POSITION_180_120": (0x35, None) # RW,Init
    "HALL_POSITION_300_240": (0x36, None) # RW,Init
    "HALL_PHI_E_PHI_M_OFFSET": (0x37, None) # RW,Init
    "HALL_DPHI_MAX": (0x38, None) # RW,Init
    "HALL_PHI_E_INTERPOLATED_PHI_E": (0x39, None) # R,Monitor
    "HALL_PHI_M": (0x3A, None) # R,Monitor
    "AENC_DECODER_MODE": (0x3B, None) # RW,Init
    "AENC_DECODER_N_THRESHOLD": (0x3C, None) # RW,Init
    "AENC_DECODER_PHI_A_RAW": (0x3D, None) # R,Monitor
    "AENC_DECODER_PHI_A_OFFSET": (0x3E, None) # RW,Init
    "AENC_DECODER_PHI_A": (0x3F, None) # R,Monitor
    "AENC_DECODER_PPR": (0x40, None) # RW,Init
    "AENC_DECODER_COUNT": (0x41, None) # RW,Monitor
    "AENC_DECODER_COUNT_N": (0x42, None) # RW,Monitor/Init
    "AENC_DECODER_PHI_E_PHI_M_OFFSET": (0x45, None) # RW,Init
    "AENC_DECODER_PHI_E_PHI_M": (0x46, None) # R,Monitor
    "CONFIG_DATA": (0x4D, None) # RW,Init
    "CONFIG_ADDR": (0x4E, None) # RW,Init

    "CONFIG_biquad_x_a_1": (0x4D, 1),
    "CONFIG_biquad_x_a_2": (0x4D, 2),
    "CONFIG_biquad_x_b_0": (0x4D, 4),
    "CONFIG_biquad_x_b_1": (0x4D, 5),
    "CONFIG_biquad_x_b_2": (0x4D, 6),
    "CONFIG_biquad_x_enable": (0x4D, 7),
    "CONFIG_biquad_v_a_1": (0x4D, 9),
    "CONFIG_biquad_v_a_2": (0x4D, 10),
    "CONFIG_biquad_v_b_0": (0x4D, 12),
    "CONFIG_biquad_v_b_1": (0x4D, 13),
    "CONFIG_biquad_v_b_2": (0x4D, 14),
    "CONFIG_biquad_v_enable": (0x4D, 15),
    "CONFIG_biquad_t_a_1": (0x4D, 17),
    "CONFIG_biquad_t_a_2": (0x4D, 18),
    "CONFIG_biquad_t_b_0": (0x4D, 20),
    "CONFIG_biquad_t_b_1": (0x4D, 21),
    "CONFIG_biquad_t_b_2": (0x4D, 22),
    "CONFIG_biquad_t_enable": (0x4D, 23),
    "CONFIG_biquad_f_a_1": (0x4D, 25),
    "CONFIG_biquad_f_a_2": (0x4D, 26),
    "CONFIG_biquad_f_b_0": (0x4D, 28),
    "CONFIG_biquad_f_b_1": (0x4D, 29),
    "CONFIG_biquad_f_b_2": (0x4D, 30),
    "CONFIG_biquad_f_enable": (0x4D, 31),
    "CONFIG_ref_switch_config": (0x4D, 51),
    "CONFIG_SINGLE_PIN_IF_STATUS_CFG": (0x4D, 60),
    "CONFIG_SINGLE_PIN_IF_SCALE_OFFSET": (0x4D, 61),
    "CONFIG_ADVANCED_PI_REPRESENT": (0x4D, 62),

    "VELOCITY_SELECTION": (0x50, None) # RW,Init
    "POSITION_SELECTION": (0x51, None) # RW,Init
    "PHI_E_SELECTION": (0x52, None) # RW,Init
    "PHI_E": (0x53, None) # R,Monitor
    "PID_FLUX_P_FLUX_I": (0x54, None) # RW,Init
    "PID_TORQUE_P_TORQUE_I": (0x56, None) # RW,Init
    "PID_VELOCITY_P_VELOCITY_I": (0x58, None) # RW,Init
    "PID_POSITION_P_POSITION_I": (0x5A, None) # RW,Init
    "PIDOUT_UQ_UD_LIMITS": (0x5D, None) # RW,Init
    "PID_TORQUE_FLUX_LIMITS": (0x5E, None) # RW,Init
    "PID_VELOCITY_LIMIT": (0x60, None) # RW,Init
    "PID_POSITION_LIMIT_LOW": (0x61, None) # RW,Init
    "PID_POSITION_LIMIT_HIGH": (0x62, None) # RW,Init
    "MODE_RAMP_MODE_MOTION": (0x63, None) # RW,Init
    "PID_TORQUE_FLUX_TARGET": (0x64, None) # RW,Control
    "PID_TORQUE_FLUX_OFFSET": (0x65, None) # RW,Control
    "PID_VELOCITY_TARGET": (0x66, None) # RW,Control
    "PID_VELOCITY_OFFSET": (0x67, None) # RW,Control
    "PID_POSITION_TARGET": (0x68, None) # RW,Control
    "PID_TORQUE_FLUX_ACTUAL": (0x69, None) # R,Monitor
    "PID_VELOCITY_ACTUAL": (0x6A, None) # R,Monitor
    "PID_POSITION_ACTUAL": (0x6B, None) # RW,Monitor/Init
    "PID_ERROR_DATA": (0x6C, None) # R,Test
    "PID_ERROR_ADDR": (0x6D, None) # RW,Test

    "PID_ERROR_PID_TORQUE_ERROR": (0x6C, 0),
    "PID_ERROR_PID_FLUX_ERROR": (0x6C, 1),
    "PID_ERROR_PID_VELOCITY_ERROR": (0x6C, 2),
    "PID_ERROR_PID_POSITION_ERROR": (0x6C, 3),
    "PID_ERROR_PID_TORQUE_ERROR_SUM": (0x6C, 4),
    "PID_ERROR_PID_FLUX_ERROR_SUM": (0x6C, 5),
    "PID_ERROR_PID_VELOCITY_ERROR_SUM": (0x6C, 6),
    "PID_ERROR_PID_POSITION_ERROR_SUM": (0x6C, 7),

    "INTERIM_DATA": (0x6E, None) # RW,Monitor
    "INTERIM_ADDR": (0x6F, None) # RW,Monitor

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

    "ADC_VM_LIMITS": (0x75, None) # RW,Init
    "TMC4671_INPUTS_RAW": (0x76, None) # R,Test/Monitor
    "TMC4671_OUTPUTS_RAW": (0x77, None) # R,Test/Monitor
    "STEP_WIDTH": (0x78, None) # RW,Init
    "UART_BPS": (0x79, None) # RW,Init
    "GPIO_dsADCI_CONFIG": (0x7B, None) # RW,Init
    "STATUS_FLAGS": (0x7C, None) # RW,Monitor
    "STATUS_MASK": (0x7D, None) # RW,Monitor
}

# These are read-only
ReadRegisters = [
    "CHIPINFO_DATA", "ADC_RAW_DATA", "ADC_IWY_IUX", "ADC_IV", "AENC_WY_UX",
    "AENC_VN", "ABN_DECODER_PHI_E_PHI_M", "ABN_2_DECODER_PHI_M",
    "HALL_PHI_E_INTERPOLATED_PHI_E", "HALL_PHI_M", "AENC_DECODER_PHI_A_RAW",
    "AENC_DECODER_PHI_A", "AENC_DECODER_PHI_E_PHI_M", "PHI_E",
    "PID_TORQUE_FLUX_ACTUAL", "PID_VELOCITY_ACTUAL", "PID_ERROR_DATA",
    "TMC4671_INPUTS_RAW", "TMC4671_OUTPUTS_RAW",
    ]

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

Fields["dsADC_MCFG_B_MCFG_A"] = {
    "cfg_dsmodulator_a": 3,
    "mclk_polarity_a": 1 << 2,
    "mdat_polarity_a": 1 << 3,
    "sel_nclk_mclk_i_a": 1 << 4,
    "cfg_dsmodulator_b": 3 <<16,
    "mclk_polarity_b": 1 << 18,
    "mdat_polarity_b": 1 << 19,
    "sel_nclk_mclk_i_b": 1 << 20
}

Fields["dsADC_MDEC_B_MDEC_A"] = {
    "dsADC_MDEC_A": 0xffff,
    "dsADC_MDEC_B": 0xffff << 16
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
    "ADC_I_UX_SELECT": 0xff << 8,
    "ADC_I_V_SELECT": 0xff << 16,
    "ADC_I_WY_SELECT": 0xff << 24,
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
    "apol": 1,
    "bpol": 1 << 1,
    "npol": 1 << 2,
    "use_abn_as_n": 1 <<3,
    "cln": 1 << 8,
    "direction": 1 << 12,
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
    "apol": 1,
    "bpol": 1 << 1,
    "npol": 1 << 2,
    "use_abn_as_n": 1 <<3,
    "cln": 1 << 8,
    "direction": 1 << 12,
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
    "polarity": 1,
    "sync": 1 << 4,
    "interp": 1 << 8,
    "dir": 1 << 12,
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
    "deg": 1,
    "dir": 1 << 12,
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
    "pid_x_target_limit": 1 << 0,
    "pid_x_errsum_limit": 1 << 2,
    "pid_x_output_limit": 1 << 3,
    "pid_v_target_limit": 1 << 4,
    "pid_v_errsum_limit": 1 << 6,
    "pid_v_output_limit": 1 << 7,
    "pid_id_target_limit": 1 << 8,
    "pid_id_errsum_limit": 1 << 10,
    "pid_id_output_limit": 1 << 11,
    "pid_iq_target_limit": 1 << 12,
    "pid_iq_errsum_limit": 1 << 14,
    "pid_iq_output_limit": 1 << 15,
    "ipark_cirlim_limit_u_d": 1 << 16,
    "ipark_cirlim_limit_u_q": 1 << 17,
    "ipark_cirlim_limit_u_r": 1 << 18,
    "ref_sw_r": 1 << 20,
    "ref_sw_h": 1 << 21,
    "ref_sw_l": 1 << 22,
    "pwm_min": 1 << 24,
    "pwm_max": 1 << 25,
    "adc_i_clipped": 1 << 26,
    "aenc_clipped": 1 << 27,
    "enc_n": 1 << 28,
    "enc_2_n": 1 << 29,
    "aenc_n": 1 << 30,
}

# 4671 does not support chaining, so that's removed
class MCU_TMC_SPI_simple:
    def __init__(self, config):
		self.printer = config.get_printer()
        self.mutex = self.printer.get_reactor().mutex()
		self.spi = bus.MCU_SPI_from_config(config, 3, default_speed=4000000)
    def reg_read(self, reg):
		self.spi.spi_send([reg, 0x00, 0x00, 0x00, 0x00])
        if self.printer.get_start_args().get('debugoutput') is not None:
            return 0
        params = self.spi.spi_transfer(cmd)
        pr = bytearray(params['response'])
        return (pr[1] << 24) | (pr[2] << 16) | (pr[3] << 8) | pr[4]
    def reg_write(self, reg, val, print_time=None):
        minclock = 0
        if print_time is not None:
            minclock = self.spi.get_mcu().print_time_to_clock(print_time)
        data = [(reg | 0x80) & 0xff, (val >> 24) & 0xff, (val >> 16) & 0xff,
                (val >> 8) & 0xff, val & 0xff]
        if self.printer.get_start_args().get('debugoutput') is not None:
            self.spi.spi_send(data, minclock)
            return val
        write_cmd = self._build_cmd(data, chain_pos)
        dummy_read = self._build_cmd([0x00, 0x00, 0x00, 0x00, 0x00], chain_pos)
        params = self.spi.spi_transfer_with_preface(data,
                                                   [0x00, 0x00, 0x00, 0x00, 0x00],
                                                   minclock=minclock)
        pr = bytearray(params['response'])
        return (pr[1] << 24) | (pr[2] << 16) | (pr[3] << 8) | pr[4]

# Helper code for working with TMC devices via SPI
# 4671 does have overlay registers, so support those
class MCU_TMC_SPI:
    def __init__(self, config, name_to_reg, fields, tmc_frequency):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.tmc_spi = MCU_TMC_SPI_simple(config)
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
				self.tmc_spi.reg_write(reg+1, addr)
			read = self.tmc_spi.reg_read(reg)
        return read
    def set_register(self, reg_name, val, print_time=None):
        reg, addr = self.name_to_reg[reg_name]
        with self.mutex:
			if addr is not None:
				for retry in range(5):
					v = self.tmc_spi.reg_write(reg+1, addr, print_time)
					if v == val:
						break
			if v == val:
				for retry in range(5):
					v = self.tmc_spi.reg_write(reg, val, self.chain_pos, print_time)
					if v == val:
						return
        raise self.printer.command_error(
            "Unable to write tmc spi '%s' register %s" % (self.name, reg_name))
    def get_tmc_frequency(self):
        return self.tmc_frequency

