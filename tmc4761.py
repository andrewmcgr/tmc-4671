# TMC4671 configuration
from . import bus, tmc

Registers = {
    "CHIPINFO_DATA": 0x00, # R,Test
    "CHIPINFO_ADDR": 0x01, # RW,Test
    "ADC_RAW_DATA": 0x02, # R,Monitor
    "ADC_RAW_ADDR": 0x03, # RW,Monitor
    "dsADC_MCFG_B_MCFG_A": 0x04, # RW,Init
    "dsADC_MCLK_A": 0x05, # RW,Init
    "dsADC_MCLK_B": 0x06, # RW,Init
    "dsADC_MDEC_B_MDEC_A": 0x07, # RW,Init
    "ADC_I1_SCALE_OFFSET": 0x08, # RW,Init
    "ADC_I0_SCALE_OFFSET": 0x09, # RW,Init
    "ADC_I_SELECT": 0x0A, # RW,Init
    "ADC_I1_I0_EXT": 0x0B, # RW,Test
    "DS_ANALOG_INPUT_STAGE_CFG": 0x0C, # RW,Test
    "AENC_0_SCALE_OFFSET": 0x0D, # RW,Init
    "AENC_1_SCALE_OFFSET": 0x0E, # RW,Init
    "AENC_2_SCALE_OFFSET": 0x0F, # RW,Init
    "AENC_SELECT": 0x11, # RW,Init
    "ADC_IWY_IUX": 0x12, # R,Monitor
    "ADC_IV": 0x13, # R,Monitor
    "AENC_WY_UX": 0x15, # R,Monitor
    "AENC_VN": 0x16, # R,Monitor
    "PWM_POLARITIES": 0x17, # RW,Init
    "PWM_MAXCNT": 0x18, # RW,Init
    "PWM_BBM_H_BBM_L": 0x19, # RW,Init
    "PWM_SV_CHOP": 0x1A, # RW,Init
    "MOTOR_TYPE_N_POLE_PAIRS": 0x1B, # RW,Init
    "PHI_E_EXT": 0x1C, # RW,Test
    "OPENLOOP_MODE": 0x1F, # RW,Init
    "OPENLOOP_ACCELERATION": 0x20, # RW,Init
    "OPENLOOP_VELOCITY_TARGET": 0x21, # RW,Init
    "OPENLOOP_VELOCITY_ACTUAL": 0x22, # RW,Monitor
    "OPENLOOP_PHI": 0x23, # RW,Monitor/Test
    "UQ_UD_EXT": 0x24, # RW,Init/Test
    "ABN_DECODER_MODE": 0x25, # RW,Init
    "ABN_DECODER_PPR": 0x26, # RW,Init
    "ABN_DECODER_COUNT": 0x27, # RW,Init/Test/Monitor
    "ABN_DECODER_COUNT_N": 0x28, # RW,Init/Test/Monitor
    "ABN_DECODER_PHI_E_PHI_M_OFFSET": 0x29, # RW,Init
    "ABN_DECODER_PHI_E_PHI_M": 0x2A, # R,Monitor
    "ABN_2_DECODER_MODE": 0x2C, # RW,Init
    "ABN_2_DECODER_PPR": 0x2D, # RW,Init
    "ABN_2_DECODER_COUNT": 0x2E, # RW,Init/Test/Monitor
    "ABN_2_DECODER_COUNT_N": 0x2F, # RW,Init/Test/Monitor
    "ABN_2_DECODER_PHI_M_OFFSET": 0x30, # RW,Init
    "ABN_2_DECODER_PHI_M": 0x31, # R,Monitor
    "HALL_MODE": 0x33, # RW,Init
    "HALL_POSITION_060_000": 0x34, # RW,Init
    "HALL_POSITION_180_120": 0x35, # RW,Init
    "HALL_POSITION_300_240": 0x36, # RW,Init
    "HALL_PHI_E_PHI_M_OFFSET": 0x37, # RW,Init
    "HALL_DPHI_MAX": 0x38, # RW,Init
    "HALL_PHI_E_INTERPOLATED_PHI_E": 0x39, # R,Monitor
    "HALL_PHI_M": 0x3A, # R,Monitor
    "AENC_DECODER_MODE": 0x3B, # RW,Init
    "AENC_DECODER_N_THRESHOLD": 0x3C, # RW,Init
    "AENC_DECODER_PHI_A_RAW": 0x3D, # R,Monitor
    "AENC_DECODER_PHI_A_OFFSET": 0x3E, # RW,Init
    "AENC_DECODER_PHI_A": 0x3F, # R,Monitor
    "AENC_DECODER_PPR": 0x40, # RW,Init
    "AENC_DECODER_COUNT": 0x41, # RW,Monitor
    "AENC_DECODER_COUNT_N": 0x42, # RW,Monitor/Init
    "AENC_DECODER_PHI_E_PHI_M_OFFSET": 0x45, # RW,Init
    "AENC_DECODER_PHI_E_PHI_M": 0x46, # R,Monitor
    "CONFIG_DATA": 0x4D, # RW,Init
    "CONFIG_ADDR": 0x4E, # RW,Init
    "VELOCITY_SELECTION": 0x50, # RW,Init
    "POSITION_SELECTION": 0x51, # RW,Init
    "PHI_E_SELECTION": 0x52, # RW,Init
    "PHI_E": 0x53, # R,Monitor
    "PID_FLUX_P_FLUX_I": 0x54, # RW,Init
    "PID_TORQUE_P_TORQUE_I": 0x56, # RW,Init
    "PID_VELOCITY_P_VELOCITY_I": 0x58, # RW,Init
    "PID_POSITION_P_POSITION_I": 0x5A, # RW,Init
    "PIDOUT_UQ_UD_LIMITS": 0x5D, # RW,Init
    "PID_TORQUE_FLUX_LIMITS": 0x5E, # RW,Init
    "PID_VELOCITY_LIMIT": 0x60, # RW,Init
    "PID_POSITION_LIMIT_LOW": 0x61, # RW,Init
    "PID_POSITION_LIMIT_HIGH": 0x62, # RW,Init
    "MODE_RAMP_MODE_MOTION": 0x63, # RW,Init
    "PID_TORQUE_FLUX_TARGET": 0x64, # RW,Control
    "PID_TORQUE_FLUX_OFFSET": 0x65, # RW,Control
    "PID_VELOCITY_TARGET": 0x66, # RW,Control
    "PID_VELOCITY_OFFSET": 0x67, # RW,Control
    "PID_POSITION_TARGET": 0x68, # RW,Control
    "PID_TORQUE_FLUX_ACTUAL": 0x69, # R,Monitor
    "PID_VELOCITY_ACTUAL": 0x6A, # R,Monitor
    "PID_POSITION_ACTUAL": 0x6B, # RW,Monitor/Init
    "PID_ERROR_DATA": 0x6C, # R,Test
    "PID_ERROR_ADDR": 0x6D, # RW,Test
    "INTERIM_DATA": 0x6E, # RW,Monitor
    "INTERIM_ADDR": 0x6F, # RW,Monitor
    "ADC_VM_LIMITS": 0x75, # RW,Init
    "TMC4671_INPUTS_RAW": 0x76, # R,Test/Monitor
    "TMC4671_OUTPUTS_RAW": 0x77, # R,Test/Monitor
    "STEP_WIDTH": 0x78, # RW,Init
    "UART_BPS": 0x79, # RW,Init
    "GPIO_dsADCI_CONFIG": 0x7B, # RW,Init
    "STATUS_FLAGS": 0x7C, # RW,Monitor
    "STATUS_MASK": 0x7D, # RW,Monitor
}

ReadRegisters = [
    "CHIPINFO_DATA", "ADC_RAW_DATA", "ADC_IWY_IUX", "ADC_IV", "AENC_WY_UX",
    "AENC_VN", "ABN_DECODER_PHI_E_PHI_M", "ABN_2_DECODER_PHI_M",
    "HALL_PHI_E_INTERPOLATED_PHI_E", "HALL_PHI_M", "AENC_DECODER_PHI_A_RAW",
    "AENC_DECODER_PHI_A", "AENC_DECODER_PHI_E_PHI_M", "PHI_E",
    "PID_TORQUE_FLUX_ACTUAL", "PID_VELOCITY_ACTUAL", "PID_ERROR_DATA",
    "TMC4671_INPUTS_RAW", "TMC4671_OUTPUTS_RAW",
    ]

# CHIPINFO_ADDR
SI_TYPE = 0
SI_VERSION = 1
SI_DATE = 2
SI_TIME = 3
SI_VARIANT = 4
SI_BUILD = 5

# ADC_RAW_ADDR
ADC_I1_RAW_ADC_I0_RAW = 0
ADC_AGPI_A_RAW_ADC_VM_RAW = 1
ADC_AENC_UX_RAW_ADC_AGPI_B_RAW = 2
ADC_AENC_WY_RAW_ADC_AENC_VN_RAW = 3

