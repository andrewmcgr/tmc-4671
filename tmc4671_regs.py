import math

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
    "VELOCITY_SELECTION_METER_SELECTION": (0x50, None), # RW,Init
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
    "ADC_VM_RAW": 0xffff, "ADC_AGPI_A_RAW": 0xffff << 16
}
Fields["ADC_AENC_UX_RAW_ADC_AGPI_B_RAW"] = {
    "ADC_AGPI_B_RAW": 0xffff, "ADC_AENC_UX_RAW": 0xffff << 16
}
Fields["ADC_AENC_WY_RAW_ADC_AENC_VN_RAW"] = {
    "ADC_AENC_VN_RAW": 0xffff, "ADC_AENC_WY_RAW": 0xffff << 16
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

Fields["VELOCITY_SELECTION_METER_SELECTION"] = {
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

def format_phi(val: float) -> str:
    """Format a raw phi value as a string in degrees."""
    phi = (val * 360.0 / 65536.0)
    if phi < 0.0:
        phi += 360
    return "%.3f" % (phi)

def format_q4_12(val: int) -> str:
    """Format a Q4.12 fixed-point value as a string."""
    return "%.4f" % (val * 2**-12)

def to_q4_12(val: float) -> int:
    """Convert a float to a Q4.12 fixed-point integer."""
    return round(val * 2**12) & 0xffff

def from_q4_12(val: int) -> float:
    """Convert a Q4.12 fixed-point integer to a float."""
    return val * 2**-12

def format_q0_15(val: int) -> str:
    """Format a Q0.15 fixed-point value as a string."""
    return "%.7f" % (val * 2**-15)

def from_q8_8(val: int) -> float:
    """Convert a Q8.8 fixed-point integer to a float."""
    return val * 2**-8

def format_q8_8(val: int) -> str:
    """Format a Q8.8 fixed-point value as a string."""
    return "%.3f" % (from_q8_8(val))

def to_q8_8(val):
    return round(val * 2**8) & 0xffff

def format_q3_29(val):
    return "%.9f" % (int.from_bytes(val.to_bytes(length=4,
                                                 byteorder='big',
                                                 signed=False),
                                    byteorder='big',
                                    signed=True) * 2**-29)

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
