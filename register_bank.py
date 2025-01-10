# Tuple is the address followed by a value to put in the next higher address
# to select that sub-register, or none to just go straight there.
# Not used for 6100, but there to use the same code.

######################################################################
# Register map for the 6100 companion chip
######################################################################
from enum import Enum
from typing import Iterator, Self
from dataclasses import dataclass


class EnumExt(Enum):
    @classmethod
    def get(cls, name, default=None) -> Self:
        if name in cls.__members__:
            return cls[name]
        return default

    @classmethod
    def member_names(cls):
        return cls._member_names_

    # for typehinting purposes
    @classmethod
    def members(cls) -> Iterator[Self]:
        return cls.__iter__()


@dataclass
class Register:
    reg_addr: int
    sub_addr: int
    signed: bool = False


class RegisterEnum(EnumExt):
    @property
    def value(self) -> Register:
        """The value of the Enum member."""
        return self._value_


@dataclass
class Field:
    register: RegisterEnum
    mask: int
    signed: bool = False


class FieldEnum(EnumExt):
    @property
    def value(self) -> Field:
        """The value of the Enum member."""
        return self._value_


class Registers6100(EnumExt):
    GCONF = Register(0x00, None)
    GSTAT = Register(0x01, None)
    IOIN = Register(0x04, None)
    SHORT_CONF = Register(0x09, None)
    DRV_CONF = Register(0x0A, None)


class Fields6100(FieldEnum):
    # GCONF
    DISABLE = Field(Registers6100.GCONF, 0x1 << 0)
    SINGLELINE = Field(Registers6100.GCONF, 0x1 << 1)
    FAULTDIRECT = Field(Registers6100.GCONF, 0x1 << 2)
    NORMAL = Field(Registers6100.GCONF, 0x1 << 6)

    # GSTAT
    RESET = Field(Registers6100.GSTAT, 0x1 << 0)
    DRV_OTPW = Field(Registers6100.GSTAT, 0x1 << 1)
    DRV_OT = Field(Registers6100.GSTAT, 0x1 << 2)
    UV_CP = Field(Registers6100.GSTAT, 0x1 << 3)
    SHORTDET_U = Field(Registers6100.GSTAT, 0x1 << 4)
    S2GU = Field(Registers6100.GSTAT, 0x1 << 5)
    S2VSU = Field(Registers6100.GSTAT, 0x1 << 6)
    SHORTDET_V = Field(Registers6100.GSTAT, 0x1 << 8)
    S2GV = Field(Registers6100.GSTAT, 0x1 << 9)
    S2VSV = Field(Registers6100.GSTAT, 0x1 << 10)
    SHORTDET_W = Field(Registers6100.GSTAT, 0x1 << 12)
    S2GW = Field(Registers6100.GSTAT, 0x1 << 13)
    S2VSW = Field(Registers6100.GSTAT, 0x1 << 14)

    # IOIN
    UL = Field(Registers6100.IOIN, 0x1 << 0)
    UH = Field(Registers6100.IOIN, 0x1 << 1)
    VL = Field(Registers6100.IOIN, 0x1 << 2)
    VH = Field(Registers6100.IOIN, 0x1 << 3)
    WL = Field(Registers6100.IOIN, 0x1 << 4)
    WH = Field(Registers6100.IOIN, 0x1 << 5)
    DRV_EN = Field(Registers6100.IOIN, 0x1 << 6)
    OTPW = Field(Registers6100.IOIN, 0x1 << 8)
    OT136C = Field(Registers6100.IOIN, 0x1 << 9)
    OT143C = Field(Registers6100.IOIN, 0x1 << 10)
    OT150C = Field(Registers6100.IOIN, 0x1 << 11)
    VERSION = Field(Registers6100.IOIN, 0xFF << 24)

    # DRV_CONF
    BBMCLKS = Field(Registers6100.DRV_CONF, 0x0F)
    OTSELECT = Field(Registers6100.DRV_CONF, 0x03 << 16)
    DRVSTRENGTH = Field(Registers6100.DRV_CONF, 0x03 << 19)

    # TODO: SHORT_CONF (defaults are reasonable)


DUMP_GROUPS_6100 = {
    "Default": [
        Registers6100.GCONF,
        Registers6100.GSTAT,
        Registers6100.IOIN,
        Registers6100.SHORT_CONF,
        Registers6100.DRV_CONF,
    ],
}


######################################################################
# Register map for the 4671
######################################################################
class Registers4671(EnumExt):
    CHIPINFO_DATA = Register(0x00, None)  # R,Test
    CHIPINFO_ADDR = Register(0x01, None)  # RW,Test
    CHIPINFO_SI_TYPE = Register(0x00, 0)
    CHIPINFO_SI_VERSION = Register(0x00, 1)
    CHIPINFO_SI_DATE = Register(0x00, 2)
    CHIPINFO_SI_TIME = Register(0x00, 3)
    CHIPINFO_SI_VARIANT = Register(0x00, 4)
    CHIPINFO_SI_BUILD = Register(0x00, 5)
    ADC_RAW_DATA = Register(0x02, None)  # R,Monitor
    ADC_RAW_ADDR = Register(0x03, None)  # RW,Monitor
    ADC_I1_RAW_ADC_I0_RAW = Register(0x02, 0)
    ADC_AGPI_A_RAW_ADC_VM_RAW = Register(0x02, 1)
    ADC_AENC_UX_RAW_ADC_AGPI_B_RAW = Register(0x02, 2)
    ADC_AENC_WY_RAW_ADC_AENC_VN_RAW = Register(0x02, 3)
    DSADC_MCFG_B_MCFG_A = Register(0x04, None)  # RW,Init
    DSADC_MCLK_A = Register(0x05, None)  # RW,Init
    DSADC_MCLK_B = Register(0x06, None)  # RW,Init
    DSADC_MDEC_B_MDEC_A = Register(0x07, None)  # RW,Init
    ADC_I1_SCALE_OFFSET = Register(0x08, None)  # RW,Init
    ADC_I0_SCALE_OFFSET = Register(0x09, None)  # RW,Init
    ADC_I_SELECT = Register(0x0A, None)  # RW,Init
    ADC_I1_I0_EXT = Register(0x0B, None)  # RW,Test
    DS_ANALOG_INPUT_STAGE_CFG = Register(0x0C, None)  # RW,Test
    AENC_0_SCALE_OFFSET = Register(0x0D, None)  # RW,Init
    AENC_1_SCALE_OFFSET = Register(0x0E, None)  # RW,Init
    AENC_2_SCALE_OFFSET = Register(0x0F, None)  # RW,Init
    AENC_SELECT = Register(0x11, None)  # RW,Init
    ADC_IWY_IUX = Register(0x12, None)  # R,Monitor
    ADC_IV = Register(0x13, None)  # R,Monitor
    AENC_WY_UX = Register(0x15, None)  # R,Monitor
    AENC_VN = Register(0x16, None)  # R,Monitor
    PWM_POLARITIES = Register(0x17, None)  # RW,Init
    PWM_MAXCNT = Register(0x18, None)  # RW,Init
    PWM_BBM_H_BBM_L = Register(0x19, None)  # RW
    PWM_SV_CHOP = Register(0x1A, None)  # RW
    MOTOR_TYPE_N_POLE_PAIRS = Register(0x1B, None)  # RW
    PHI_E_EXT = Register(0x1C, None, True)  # RW,Test
    OPENLOOP_MODE = Register(0x1F, None)  # RW,Init
    OPENLOOP_ACCELERATION = Register(0x20, None)  # RW,Init
    OPENLOOP_VELOCITY_TARGET = Register(0x21, None, True)  # RW,Init
    OPENLOOP_VELOCITY_ACTUAL = Register(0x22, None, True)  # RW,Monitor
    OPENLOOP_PHI = Register(0x23, None, True)  # RW,Monitor/Test
    UQ_UD_EXT = Register(0x24, None)  # RW,Init/Test
    ABN_DECODER_MODE = Register(0x25, None)  # RW,Init
    ABN_DECODER_PPR = Register(0x26, None)  # RW,Init
    ABN_DECODER_COUNT = Register(0x27, None)  # RW,Monitor
    ABN_DECODER_COUNT_N = Register(0x28, None)  # RW,Monitor
    ABN_DECODER_PHI_E_PHI_M_OFFSET = Register(0x29, None)  # RW,Init
    ABN_DECODER_PHI_E_PHI_M = Register(0x2A, None)  # R,Monitor
    ABN_2_DECODER_MODE = Register(0x2C, None)  # RW,Init
    ABN_2_DECODER_PPR = Register(0x2D, None)  # RW,Init
    ABN_2_DECODER_COUNT = Register(0x2E, None)  # RW,Monitor
    ABN_2_DECODER_COUNT_N = Register(0x2F, None)  # RW,Monitor
    ABN_2_DECODER_PHI_M_OFFSET = Register(0x30, None)  # RW,Init
    ABN_2_DECODER_PHI_M = Register(0x31, None)  # R,Monitor
    HALL_MODE = Register(0x33, None)  # RW,Init
    HALL_POSITION_060_000 = Register(0x34, None)  # RW,Init
    HALL_POSITION_180_120 = Register(0x35, None)  # RW,Init
    HALL_POSITION_300_240 = Register(0x36, None)  # RW,Init
    HALL_PHI_E_PHI_M_OFFSET = Register(0x37, None)  # RW,Init
    HALL_DPHI_MAX = Register(0x38, None)  # RW,Init
    HALL_PHI_E_INTERPOLATED_PHI_E = Register(0x39, None)  # R,Monitor
    HALL_PHI_M = Register(0x3A, None, True)  # R,Monitor
    AENC_DECODER_MODE = Register(0x3B, None)  # RW,Init
    AENC_DECODER_N_THRESHOLD = Register(0x3C, None)  # RW,Init
    AENC_DECODER_PHI_A_RAW = Register(0x3D, None, True)  # R,Monitor
    AENC_DECODER_PHI_A_OFFSET = Register(0x3E, None, True)  # RW,Init
    AENC_DECODER_PHI_A = Register(0x3F, None, True)  # R,Monitor
    AENC_DECODER_PPR = Register(0x40, None, True)  # RW,Init
    AENC_DECODER_COUNT = Register(0x41, None, True)  # RW,Monitor
    AENC_DECODER_COUNT_N = Register(0x42, None, True)  # RW,Monitor/Init
    AENC_DECODER_PHI_E_PHI_M_OFFSET = Register(0x45, None)  # RW,Init
    AENC_DECODER_PHI_E_PHI_M = Register(0x46, None)  # R,Monitor
    CONFIG_DATA = Register(0x4D, None)  # RW,Init
    CONFIG_ADDR = Register(0x4E, None)  # RW,Init
    CONFIG_BIQUAD_X_A_1 = Register(0x4D, 1)
    CONFIG_BIQUAD_X_A_2 = Register(0x4D, 2)
    CONFIG_BIQUAD_X_B_0 = Register(0x4D, 4)
    CONFIG_BIQUAD_X_B_1 = Register(0x4D, 5)
    CONFIG_BIQUAD_X_B_2 = Register(0x4D, 6)
    CONFIG_BIQUAD_X_ENABLE = Register(0x4D, 7)
    CONFIG_BIQUAD_V_A_1 = Register(0x4D, 9)
    CONFIG_BIQUAD_V_A_2 = Register(0x4D, 10)
    CONFIG_BIQUAD_V_B_0 = Register(0x4D, 12)
    CONFIG_BIQUAD_V_B_1 = Register(0x4D, 13)
    CONFIG_BIQUAD_V_B_2 = Register(0x4D, 14)
    CONFIG_BIQUAD_V_ENABLE = Register(0x4D, 15)
    CONFIG_BIQUAD_T_A_1 = Register(0x4D, 17)
    CONFIG_BIQUAD_T_A_2 = Register(0x4D, 18)
    CONFIG_BIQUAD_T_B_0 = Register(0x4D, 20)
    CONFIG_BIQUAD_T_B_1 = Register(0x4D, 21)
    CONFIG_BIQUAD_T_B_2 = Register(0x4D, 22)
    CONFIG_BIQUAD_T_ENABLE = Register(0x4D, 23)
    CONFIG_BIQUAD_F_A_1 = Register(0x4D, 25)
    CONFIG_BIQUAD_F_A_2 = Register(0x4D, 26)
    CONFIG_BIQUAD_F_B_0 = Register(0x4D, 28)
    CONFIG_BIQUAD_F_B_1 = Register(0x4D, 29)
    CONFIG_BIQUAD_F_B_2 = Register(0x4D, 30)
    CONFIG_BIQUAD_F_ENABLE = Register(0x4D, 31)
    CONFIG_REF_SWITCH_CONFIG = Register(0x4D, 51)
    CONFIG_SINGLE_PIN_IF_STATUS_CFG = Register(0x4D, 60)
    CONFIG_SINGLE_PIN_IF_SCALE_OFFSET = Register(0x4D, 61)
    CONFIG_ADVANCED_PI_REPRESENT = Register(0x4D, 62)
    VELOCITY_SELECTION = Register(0x50, None)  # RW,Init
    POSITION_SELECTION = Register(0x51, None)  # RW,Init
    PHI_E_SELECTION = Register(0x52, None)  # RW,Init
    PHI_E = Register(0x53, None, True)  # R,Monitor
    PID_FLUX_P_FLUX_I = Register(0x54, None)  # RW,Init
    PID_TORQUE_P_TORQUE_I = Register(0x56, None)  # RW,Init
    PID_VELOCITY_P_VELOCITY_I = Register(0x58, None)  # RW,Init
    PID_POSITION_P_POSITION_I = Register(0x5A, None)  # RW,Init
    PIDOUT_UQ_UD_LIMITS = Register(0x5D, None, True)  # RW,Init
    PID_TORQUE_FLUX_LIMITS = Register(0x5E, None)  # RW,Init
    PID_VELOCITY_LIMIT = Register(0x60, None)  # RW,Init
    PID_POSITION_LIMIT_LOW = Register(0x61, None, True)  # RW,Init
    PID_POSITION_LIMIT_HIGH = Register(0x62, None, True)  # RW,Init
    MODE_RAMP_MODE_MOTION = Register(0x63, None)  # RW,Init
    PID_TORQUE_FLUX_TARGET = Register(0x64, None)  # RW,Control
    PID_TORQUE_FLUX_OFFSET = Register(0x65, None)  # RW,Control
    PID_VELOCITY_TARGET = Register(0x66, None, True)  # RW,Control
    PID_VELOCITY_OFFSET = Register(0x67, None, True)  # RW,Control
    PID_POSITION_TARGET = Register(0x68, None, True)  # RW,Control
    PID_TORQUE_FLUX_ACTUAL = Register(0x69, None)  # R,Monitor
    PID_VELOCITY_ACTUAL = Register(0x6A, None, True)  # R,Monitor
    PID_POSITION_ACTUAL = Register(0x6B, None, True)  # RW,Monitor/Init

    PID_ERROR_DATA = Register(0x6C, None)  # R,Test
    PID_ERROR_ADDR = Register(0x6D, None)  # RW,Test

    PID_ERROR_PID_TORQUE_ERROR = Register(0x6C, 0, True)
    PID_ERROR_PID_FLUX_ERROR = Register(0x6C, 1, True)
    PID_ERROR_PID_VELOCITY_ERROR = Register(0x6C, 2, True)
    PID_ERROR_PID_POSITION_ERROR = Register(0x6C, 3, True)
    PID_ERROR_PID_TORQUE_ERROR_SUM = Register(0x6C, 4, True)
    PID_ERROR_PID_FLUX_ERROR_SUM = Register(0x6C, 5, True)
    PID_ERROR_PID_VELOCITY_ERROR_SUM = Register(0x6C, 6, True)
    PID_ERROR_PID_POSITION_ERROR_SUM = Register(0x6C, 7, True)

    INTERIM_DATA = Register(0x6E, None)  # RW,Monitor
    INTERIM_ADDR = Register(0x6F, None)  # RW,Monitor

    INTERIM_PIDIN_TARGET_TORQUE = Register(0x6E, 0, True)
    INTERIM_PIDIN_TARGET_FLUX = Register(0x6E, 1, True)
    INTERIM_PIDIN_TARGET_VELOCITY = Register(0x6E, 2, True)
    INTERIM_PIDIN_TARGET_POSITION = Register(0x6E, 3, True)
    INTERIM_PIDOUT_TARGET_TORQUE = Register(0x6E, 4, True)
    INTERIM_PIDOUT_TARGET_FLUX = Register(0x6E, 5, True)
    INTERIM_PIDOUT_TARGET_VELOCITY = Register(0x6E, 6, True)
    INTERIM_PIDOUT_TARGET_POSITION = Register(0x6E, 7, True)
    INTERIM_FOC_IWY_IUX = Register(0x6E, 8, True)
    INTERIM_FOC_IV = Register(0x6E, 9, True)
    INTERIM_FOC_IB_IA = Register(0x6E, 10, True)
    INTERIM_FOC_IQ_ID = Register(0x6E, 11, True)
    INTERIM_FOC_UQ_UD = Register(0x6E, 12, True)
    INTERIM_FOC_UQ_UD_LIMITED = Register(0x6E, 13, True)
    INTERIM_FOC_UB_UA = Register(0x6E, 14, True)
    INTERIM_FOC_UWY_UUX = Register(0x6E, 15, True)
    INTERIM_FOC_UV = Register(0x6E, 16, True)
    INTERIM_PWM_WY_UX = Register(0x6E, 17, True)
    INTERIM_PWM_UV = Register(0x6E, 18, True)
    INTERIM_ADC_I1_I0 = Register(0x6E, 19, True)
    INTERIM_PID_TORQUE_TARGET_FLUX_TARGET_TORQUE_ACTUAL_FLUX_ACTUAL_DIV256 = (
        Register(0x6E, 20, True)
    )
    INTERIM_PID_TORQUE_TARGET_TORQUE_ACTUAL = Register(0x6E, 21, True)
    INTERIM_PID_FLUX_TARGET_FLUX_ACTUAL = Register(0x6E, 22, True)
    INTERIM_PID_VELOCITY_TARGET_VELOCITY_ACTUAL_DIV256 = Register(
        0x6E, 23, True
    )
    INTERIM_PID_VELOCITY_TARGET_VELOCITY_ACTUAL = Register(0x6E, 24, True)
    INTERIM_PID_POSITION_TARGET_POSITION_ACTUAL_DIV256 = Register(
        0x6E, 25, True
    )
    INTERIM_PID_POSITION_TARGET_POSITION_ACTUAL = Register(0x6E, 26, True)
    INTERIM_FF_VELOCITY = Register(0x6E, 27, True)
    INTERIM_FF_TORQUE = Register(0x6E, 28, True)
    INTERIM_ACTUAL_VELOCITY_PPTM = Register(0x6E, 29, True)
    INTERIM_REF_SWITCH_STATUS = Register(0x6E, 30, True)
    INTERIM_HOME_POSITION = Register(0x6E, 31, True)
    INTERIM_LEFT_POSITION = Register(0x6E, 32, True)
    INTERIM_RIGHT_POSITION = Register(0x6E, 33, True)
    INTERIM_SINGLE_PIN_IF_PWM_DUTY_CYCLE_TORQUE_TARGET = Register(
        0x6E, 42, True
    )
    INTERIM_SINGLE_PIN_IF_VELOCITY_TARGET = Register(0x6E, 43, True)
    INTERIM_SINGLE_PIN_IF_POSITION_TARGET = Register(0x6E, 44, True)
    ADC_VM_LIMITS = Register(0x75, None)  # RW,Init
    TMC4671_INPUTS_RAW = Register(0x76, None)  # R,Test/Monitor
    TMC4671_OUTPUTS_RAW = Register(0x77, None)  # R,Test/Monitor
    STEP_WIDTH = Register(0x78, None, True)  # RW,Init
    UART_BPS = Register(0x79, None)  # RW,Init
    GPIO_DSADCI_CONFIG = Register(0x7B, None)  # RW,Init
    STATUS_FLAGS = Register(0x7C, None)  # RW,Monitor
    STATUS_MASK = Register(0x7D, None)  # RW,Monitor


# These are read-only
ReadOnlyRegisters = {
    Registers4671.CHIPINFO_DATA,
    Registers4671.ADC_RAW_DATA,
    Registers4671.ADC_IWY_IUX,
    Registers4671.ADC_IV,
    Registers4671.AENC_WY_UX,
    Registers4671.AENC_VN,
    Registers4671.ABN_DECODER_PHI_E_PHI_M,
    Registers4671.ABN_2_DECODER_PHI_M,
    Registers4671.HALL_PHI_E_INTERPOLATED_PHI_E,
    Registers4671.HALL_PHI_M,
    Registers4671.AENC_DECODER_PHI_A_RAW,
    Registers4671.AENC_DECODER_PHI_A,
    Registers4671.AENC_DECODER_PHI_E_PHI_M,
    Registers4671.PHI_E,
    Registers4671.PID_TORQUE_FLUX_ACTUAL,
    Registers4671.PID_VELOCITY_ACTUAL,
    Registers4671.PID_ERROR_DATA,
    Registers4671.TMC4671_INPUTS_RAW,
    Registers4671.TMC4671_OUTPUTS_RAW,
}


class Fields4671(FieldEnum):
    # ADC_I1_RAW_ADC_I0_RAW
    ADC_I0_RAW = Field(Registers4671.ADC_I1_RAW_ADC_I0_RAW, 0xFFFF << 0)
    ADC_I1_RAW = Field(Registers4671.ADC_I1_RAW_ADC_I0_RAW, 0xFFFF << 16)

    # ADC_AGPI_A_RAW_ADC_VM_RAW
    ADC_AGPI_A_RAW = Field(Registers4671.ADC_AGPI_A_RAW_ADC_VM_RAW, 0xFFFF << 0)
    ADC_VM_RAW = Field(Registers4671.ADC_AGPI_A_RAW_ADC_VM_RAW, 0xFFFF << 16)

    # ADC_AENC_UX_RAW_ADC_AGPI_B_RAW
    ADC_AENC_UX_RAW = Field(
        Registers4671.ADC_AENC_UX_RAW_ADC_AGPI_B_RAW, 0xFFFF << 0
    )
    ADC_AGPI_B_RAW = Field(
        Registers4671.ADC_AENC_UX_RAW_ADC_AGPI_B_RAW, 0xFFFF << 16
    )

    # ADC_AENC_WY_RAW_ADC_AENC_VN_RAW
    ADC_AENC_WY_RAW = Field(
        Registers4671.ADC_AENC_WY_RAW_ADC_AENC_VN_RAW, 0xFFFF << 0
    )
    ADC_AENC_VN_RAW = Field(
        Registers4671.ADC_AENC_WY_RAW_ADC_AENC_VN_RAW, 0xFFFF << 16
    )

    # DSADC_MCFG_B_MCFG_A
    CFG_DSMODULATOR_A = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x3 << 0)
    MCLK_POLARITY_A = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x1 << 2)
    MDAT_POLARITY_A = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x1 << 3)
    SEL_NCLK_MCLK_I_A = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x1 << 4)
    CFG_DSMODULATOR_B = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x3 << 16)
    MCLK_POLARITY_B = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x1 << 18)
    MDAT_POLARITY_B = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x1 << 19)
    SEL_NCLK_MCLK_I_B = Field(Registers4671.DSADC_MCFG_B_MCFG_A, 0x1 << 20)

    # DSADC_MDEC_B_MDEC_A
    DSADC_MDEC_A = Field(Registers4671.DSADC_MDEC_B_MDEC_A, 0xFFFF << 0)
    DSADC_MDEC_B = Field(Registers4671.DSADC_MDEC_B_MDEC_A, 0xFFFF << 16)

    # ADC_I1_SCALE_OFFSET
    ADC_I1_OFFSET = Field(Registers4671.ADC_I1_SCALE_OFFSET, 0xFFFF << 0)
    ADC_I1_SCALE = Field(Registers4671.ADC_I1_SCALE_OFFSET, 0xFFFF << 16, True)

    # ADC_I0_SCALE_OFFSET
    ADC_I0_OFFSET = Field(Registers4671.ADC_I0_SCALE_OFFSET, 0xFFFF << 0)
    ADC_I0_SCALE = Field(Registers4671.ADC_I0_SCALE_OFFSET, 0xFFFF << 16, True)

    # ADC_I_SELECT
    ADC_I0_SELECT = Field(Registers4671.ADC_I_SELECT, 0xFF << 0)
    ADC_I1_SELECT = Field(Registers4671.ADC_I_SELECT, 0xFF << 8)
    ADC_I_UX_SELECT = Field(Registers4671.ADC_I_SELECT, 0x3 << 24)
    ADC_I_V_SELECT = Field(Registers4671.ADC_I_SELECT, 0x3 << 26)
    ADC_I_WY_SELECT = Field(Registers4671.ADC_I_SELECT, 0x3 << 28)

    # ADC_I1_I0_EXT
    ADC_I0_EXT = Field(Registers4671.ADC_I1_I0_EXT, 0xFFFF << 0)
    ADC_I1_EXT = Field(Registers4671.ADC_I1_I0_EXT, 0xFFFF << 16)

    # DS_ANALOG_INPUT_STAGE_CFG
    CFG_ADC_I0 = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 0)
    CFG_ADC_I1 = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 4)
    CFG_ADC_VM = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 8)
    CFG_ADC_AGPI_A = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 12)
    CFG_ADC_AGPI_B = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 16)
    CFG_ADC_AENC_UX = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 20)
    CFG_ADC_AENC_VN = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 24)
    CFG_ADC_AENC_WY = Field(Registers4671.DS_ANALOG_INPUT_STAGE_CFG, 0xF << 28)

    # AENC_0_SCALE_OFFSET
    AENC_0_OFFSET = Field(Registers4671.AENC_0_SCALE_OFFSET, 0xFFFF << 0)
    AENC_0_SCALE = Field(Registers4671.AENC_0_SCALE_OFFSET, 0xFFFF << 16, True)

    # AENC_1_SCALE_OFFSET
    AENC_1_OFFSET = Field(Registers4671.AENC_1_SCALE_OFFSET, 0xFFFF << 0)
    AENC_1_SCALE = Field(Registers4671.AENC_1_SCALE_OFFSET, 0xFFFF << 16, True)

    # AENC_2_SCALE_OFFSET
    AENC_2_OFFSET = Field(Registers4671.AENC_2_SCALE_OFFSET, 0xFFFF << 0)
    AENC_2_SCALE = Field(Registers4671.AENC_2_SCALE_OFFSET, 0xFFFF << 16, True)

    # AENC_SELECT
    AENC_0_SELECT = Field(Registers4671.AENC_SELECT, 0xFF << 0)
    AENC_1_SELECT = Field(Registers4671.AENC_SELECT, 0xFF << 8)
    AENC_2_SELECT = Field(Registers4671.AENC_SELECT, 0xFF << 16)

    # ADC_IWY_IUX
    ADC_IUX = Field(Registers4671.ADC_IWY_IUX, 0xFFFF << 0, True)
    ADC_IWY = Field(Registers4671.ADC_IWY_IUX, 0xFFFF << 16, True)

    # ADC_IV
    ADC_IV = Field(Registers4671.ADC_IV, 0xFFFF << 0, True)

    # AENC_WY_UX
    AENC_UX = Field(Registers4671.AENC_WY_UX, 0xFFFF << 0, True)
    AENC_WY = Field(Registers4671.AENC_WY_UX, 0xFFFF << 16, True)

    # AENC_VN
    AENC_VN = Field(Registers4671.AENC_VN, 0xFFFF << 0, True)

    # PWM_POLARITIES
    PWM_POLARITIES_0 = Field(Registers4671.PWM_POLARITIES, 0x1 << 0)
    PWM_POLARITIES_1 = Field(Registers4671.PWM_POLARITIES, 0x1 << 1)

    # PWM_BBM_H_BBM_L
    PWM_BBM_L = Field(Registers4671.PWM_BBM_H_BBM_L, 0xFF << 0)
    PWM_BBM_H = Field(Registers4671.PWM_BBM_H_BBM_L, 0xFF << 8)

    # PWM_SV_CHOP
    PWM_CHOP = Field(Registers4671.PWM_SV_CHOP, 0xFF << 0)
    PWM_SV = Field(Registers4671.PWM_SV_CHOP, 0x1 << 8)

    # MOTOR_TYPE_N_POLE_PAIRS
    N_POLE_PAIRS = Field(Registers4671.MOTOR_TYPE_N_POLE_PAIRS, 0xFFFF << 0)
    MOTOR_TYPE = Field(Registers4671.MOTOR_TYPE_N_POLE_PAIRS, 0xFF << 16)

    # OPENLOOP_MODE
    OPENLOOP_PHI_DIRECTION = Field(Registers4671.OPENLOOP_MODE, 0x1 << 12)

    # UQ_UD_EXT
    UD_EXT = Field(Registers4671.UQ_UD_EXT, 0xFFFF << 0, True)
    UQ_EXT = Field(Registers4671.UQ_UD_EXT, 0xFFFF << 16, True)

    # ABN_DECODER_MODE
    ABN_APOL = Field(Registers4671.ABN_DECODER_MODE, 0x1 << 0)
    ABN_BPOL = Field(Registers4671.ABN_DECODER_MODE, 0x1 << 1)
    ABN_NPOL = Field(Registers4671.ABN_DECODER_MODE, 0x1 << 2)
    ABN_USE_ABN_AS_N = Field(Registers4671.ABN_DECODER_MODE, 0x1 << 3)
    ABN_CLN = Field(Registers4671.ABN_DECODER_MODE, 0x1 << 8)
    ABN_DIRECTION = Field(Registers4671.ABN_DECODER_MODE, 0x1 << 12)

    # ABN_DECODER_PHI_E_PHI_M_OFFSET
    ABN_DECODER_PHI_M_OFFSET = Field(
        Registers4671.ABN_DECODER_PHI_E_PHI_M_OFFSET, 0xFFFF << 0, True
    )
    ABN_DECODER_PHI_E_OFFSET = Field(
        Registers4671.ABN_DECODER_PHI_E_PHI_M_OFFSET, 0xFFFF << 16, True
    )

    # ABN_DECODER_PHI_E_PHI_M
    ABN_DECODER_PHI_M = Field(
        Registers4671.ABN_DECODER_PHI_E_PHI_M, 0xFFFF << 0, True
    )
    ABN_DECODER_PHI_E = Field(
        Registers4671.ABN_DECODER_PHI_E_PHI_M, 0xFFFF << 16, True
    )

    # ABN_2_DECODER_MODE
    ABN_2_APOL = Field(Registers4671.ABN_2_DECODER_MODE, 0x1 << 0)
    ABN_2_BPOL = Field(Registers4671.ABN_2_DECODER_MODE, 0x1 << 1)
    ABN_2_NPOL = Field(Registers4671.ABN_2_DECODER_MODE, 0x1 << 2)
    ABN_2_USE_ABN_AS_N = Field(Registers4671.ABN_2_DECODER_MODE, 0x1 << 3)
    ABN_2_CLN = Field(Registers4671.ABN_2_DECODER_MODE, 0x1 << 8)
    ABN_2_DIRECTION = Field(Registers4671.ABN_2_DECODER_MODE, 0x1 << 12)

    # # ABN_2_DECODER_PHI_E_PHI_M_OFFSET
    # ABN_2_DECODER_PHI_M_OFFSET = Field(
    #     Registers4671.ABN_2_DECODER_PHI_E_PHI_M_OFFSET, 0xFFFF << 0, True
    # )
    # ABN_2_DECODER_PHI_E_OFFSET = Field(
    #     Registers4671.ABN_2_DECODER_PHI_E_PHI_M_OFFSET, 0xFFFF << 16, True
    # )

    # ABN_2_DECODER_PHI_E_PHI_M
    # ABN_2_DECODER_PHI_M = Field(
    #     Registers4671.ABN_2_DECODER_PHI_E_PHI_M, 0xFFFF << 0
    # )
    # ABN_2_DECODER_PHI_E = Field(
    #     Registers4671.ABN_2_DECODER_PHI_E_PHI_M, 0xFFFF << 16
    # )

    # HALL_MODE
    HALL_POLARITY = Field(Registers4671.HALL_MODE, 0x1 << 0)
    HALL_SYNC = Field(Registers4671.HALL_MODE, 0x1 << 4)
    HALL_INTERP = Field(Registers4671.HALL_MODE, 0x1 << 8)
    HALL_DIR = Field(Registers4671.HALL_MODE, 0x1 << 12)
    HALL_BLANK = Field(Registers4671.HALL_MODE, 0xFFF << 16)

    # HALL_POSITION_060_000
    HALL_POSITION_000 = Field(
        Registers4671.HALL_POSITION_060_000, 0xFFFF << 0, True
    )
    HALL_POSITION_060 = Field(
        Registers4671.HALL_POSITION_060_000, 0xFFFF << 16, True
    )

    # HALL_POSITION_180_120
    HALL_POSITION_120 = Field(
        Registers4671.HALL_POSITION_180_120, 0xFFFF << 0, True
    )
    HALL_POSITION_180 = Field(
        Registers4671.HALL_POSITION_180_120, 0xFFFF << 16, True
    )

    # HALL_POSITION_300_240
    HALL_POSITION_240 = Field(
        Registers4671.HALL_POSITION_300_240, 0xFFFF << 0, True
    )
    HALL_POSITION_300 = Field(
        Registers4671.HALL_POSITION_300_240, 0xFFFF << 16, True
    )

    # HALL_PHI_E_PHI_M_OFFSET
    HALL_PHI_M_OFFSET = Field(
        Registers4671.HALL_PHI_E_PHI_M_OFFSET, 0xFFFF << 0, True
    )
    HALL_PHI_E_OFFSET = Field(
        Registers4671.HALL_PHI_E_PHI_M_OFFSET, 0xFFFF << 16, True
    )

    # HALL_PHI_E_INTERPOLATED_PHI_E
    HALL_PHI_E = Field(
        Registers4671.HALL_PHI_E_INTERPOLATED_PHI_E, 0xFFFF << 0, True
    )
    HALL_PHI_E_INTERPOLATED = Field(
        Registers4671.HALL_PHI_E_INTERPOLATED_PHI_E, 0xFFFF << 16, True
    )

    # AENC_DECODER_MODE
    AENC_DEG = Field(Registers4671.AENC_DECODER_MODE, 0x1 << 0)
    AENC_DIR = Field(Registers4671.AENC_DECODER_MODE, 0x1 << 12)

    # AENC_DECODER_PPR
    AENC_PPR = Field(Registers4671.AENC_DECODER_PPR, 0xFFFF << 0)

    # AENC_DECODER_PHI_E_PHI_M_OFFSET
    AENC_DECODER_PHI_M_OFFSET = Field(
        Registers4671.AENC_DECODER_PHI_E_PHI_M_OFFSET, 0xFFFF << 0, True
    )
    AENC_DECODER_PHI_E_OFFSET = Field(
        Registers4671.AENC_DECODER_PHI_E_PHI_M_OFFSET, 0xFFFF << 16, True
    )

    # AENC_DECODER_PHI_E_PHI_M
    AENC_DECODER_PHI_M = Field(
        Registers4671.AENC_DECODER_PHI_E_PHI_M, 0xFFFF << 0, True
    )
    AENC_DECODER_PHI_E = Field(
        Registers4671.AENC_DECODER_PHI_E_PHI_M, 0xFFFF << 16, True
    )

    # CONFIG_DATA
    CURRENT_I_n = Field(Registers4671.CONFIG_ADVANCED_PI_REPRESENT, 1 << 0)
    CURRENT_P_n = Field(Registers4671.CONFIG_ADVANCED_PI_REPRESENT, 1 << 1)
    VELOCITY_I_n = Field(Registers4671.CONFIG_ADVANCED_PI_REPRESENT, 1 << 2)
    VELOCITY_P_n = Field(Registers4671.CONFIG_ADVANCED_PI_REPRESENT, 1 << 3)
    POSITION_I_n = Field(Registers4671.CONFIG_ADVANCED_PI_REPRESENT, 1 << 4)
    POSITION_P_n = Field(Registers4671.CONFIG_ADVANCED_PI_REPRESENT, 1 << 5)

    # VELOCITY_SELECTION
    VELOCITY_SELECTION = Field(Registers4671.VELOCITY_SELECTION, 0xFF << 0)
    VELOCITY_METER_SELECTION = Field(
        Registers4671.VELOCITY_SELECTION, 0xFF << 8
    )

    # PID_FLUX_P_FLUX_I
    PID_FLUX_I = Field(Registers4671.PID_FLUX_P_FLUX_I, 0xFFFF << 0, True)
    PID_FLUX_P = Field(Registers4671.PID_FLUX_P_FLUX_I, 0xFFFF << 16, True)

    # PID_TORQUE_P_TORQUE_I
    PID_TORQUE_I = Field(Registers4671.PID_TORQUE_P_TORQUE_I, 0xFFFF << 0, True)
    PID_TORQUE_P = Field(
        Registers4671.PID_TORQUE_P_TORQUE_I, 0xFFFF << 16, True
    )

    # PID_VELOCITY_P_VELOCITY_I
    PID_VELOCITY_I = Field(
        Registers4671.PID_VELOCITY_P_VELOCITY_I, 0xFFFF << 0, True
    )
    PID_VELOCITY_P = Field(
        Registers4671.PID_VELOCITY_P_VELOCITY_I, 0xFFFF << 16, True
    )

    # PID_POSITION_P_POSITION_I
    PID_POSITION_I = Field(
        Registers4671.PID_POSITION_P_POSITION_I, 0xFFFF << 0, True
    )
    PID_POSITION_P = Field(
        Registers4671.PID_POSITION_P_POSITION_I, 0xFFFF << 16, True
    )

    # MODE_RAMP_MODE_MOTION
    MODE_MOTION = Field(Registers4671.MODE_RAMP_MODE_MOTION, 0xFF << 0)
    MODE_PID_SMPL = Field(Registers4671.MODE_RAMP_MODE_MOTION, 0x7F << 24)
    MODE_PID_TYPE = Field(Registers4671.MODE_RAMP_MODE_MOTION, 1 << 31)

    # PID_TORQUE_FLUX_TARGET
    PID_FLUX_TARGET = Field(
        Registers4671.PID_TORQUE_FLUX_TARGET, 0xFFFF << 0, True
    )
    PID_TORQUE_TARGET = Field(
        Registers4671.PID_TORQUE_FLUX_TARGET, 0xFFFF << 16, True
    )

    # PID_TORQUE_FLUX_OFFSET
    PID_FLUX_OFFSET = Field(
        Registers4671.PID_TORQUE_FLUX_OFFSET, 0xFFFF << 0, True
    )
    PID_TORQUE_OFFSET = Field(
        Registers4671.PID_TORQUE_FLUX_OFFSET, 0xFFFF << 16, True
    )

    # PID_TORQUE_FLUX_ACTUAL
    PID_FLUX_ACTUAL = Field(
        Registers4671.PID_TORQUE_FLUX_ACTUAL, 0xFFFF << 0, True
    )
    PID_TORQUE_ACTUAL = Field(
        Registers4671.PID_TORQUE_FLUX_ACTUAL, 0xFFFF << 16, True
    )

    # INTERIM_PWM_WY_UX
    INTERIM_PWM_UX = Field(Registers4671.INTERIM_PWM_WY_UX, 0xFFFF << 0)
    INTERIM_PWM_WY = Field(Registers4671.INTERIM_PWM_WY_UX, 0xFFFF << 16)

    # ADC_VM_LIMITS
    ADC_VM_LIMIT_LOW = Field(Registers4671.ADC_VM_LIMITS, 0xFFFF << 0)
    ADC_VM_LIMIT_HIGH = Field(Registers4671.ADC_VM_LIMITS, 0xFFFF << 16)

    # STATUS_FLAGS
    PID_X_TARGET_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 0)
    PID_X_ERRSUM_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 2)
    PID_X_OUTPUT_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 3)
    PID_V_TARGET_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 4)
    PID_V_ERRSUM_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 6)
    PID_V_OUTPUT_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 7)
    PID_ID_TARGET_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 8)
    PID_ID_ERRSUM_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 10)
    PID_ID_OUTPUT_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 11)
    PID_IQ_TARGET_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 12)
    PID_IQ_ERRSUM_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 14)
    PID_IQ_OUTPUT_LIMIT = Field(Registers4671.STATUS_FLAGS, 1 << 15)
    IPARK_CIRLIM_LIMIT_U_D = Field(Registers4671.STATUS_FLAGS, 1 << 16)
    IPARK_CIRLIM_LIMIT_U_Q = Field(Registers4671.STATUS_FLAGS, 1 << 17)
    IPARK_CIRLIM_LIMIT_U_R = Field(Registers4671.STATUS_FLAGS, 1 << 18)
    REF_SW_R = Field(Registers4671.STATUS_FLAGS, 1 << 20)
    REF_SW_H = Field(Registers4671.STATUS_FLAGS, 1 << 21)
    REF_SW_L = Field(Registers4671.STATUS_FLAGS, 1 << 22)
    PWM_MIN = Field(Registers4671.STATUS_FLAGS, 1 << 24)
    PWM_MAX = Field(Registers4671.STATUS_FLAGS, 1 << 25)
    ADC_I_CLIPPED = Field(Registers4671.STATUS_FLAGS, 1 << 26)
    AENC_CLIPPED = Field(Registers4671.STATUS_FLAGS, 1 << 27)
    ENC_N = Field(Registers4671.STATUS_FLAGS, 1 << 28)
    ENC_2_N = Field(Registers4671.STATUS_FLAGS, 1 << 29)
    AENC_N = Field(Registers4671.STATUS_FLAGS, 1 << 30)


ADC_GPIO_FIELDS = {
    "AGPI_A": Fields4671.ADC_AGPI_A_RAW,
    "AGPI_B": Fields4671.ADC_AGPI_B_RAW,
    None: None,
}


DUMP_GROUPS_4671 = {
    "default": [
        Registers4671.CHIPINFO_SI_TYPE,
        Registers4671.CHIPINFO_SI_VERSION,
        Registers4671.STATUS_FLAGS,
        Registers4671.PHI_E,
    ],
    "hall": [
        Registers4671.HALL_MODE,
        Registers4671.HALL_POSITION_060_000,
        Registers4671.HALL_POSITION_180_120,
        Registers4671.HALL_POSITION_300_240,
        Registers4671.HALL_PHI_E_INTERPOLATED_PHI_E,
        Registers4671.HALL_PHI_E_PHI_M_OFFSET,
        Registers4671.HALL_PHI_M,
    ],
    "abn": [
        Registers4671.ABN_DECODER_COUNT,
        Registers4671.ABN_DECODER_MODE,
        Registers4671.ABN_DECODER_PPR,
        Registers4671.ABN_DECODER_PHI_E_PHI_M_OFFSET,
        Registers4671.ABN_DECODER_PHI_E_PHI_M,
    ],
    "adc": [
        Registers4671.ADC_I1_RAW_ADC_I0_RAW,
        Registers4671.ADC_IWY_IUX,
        Registers4671.ADC_IV,
        Registers4671.ADC_I0_SCALE_OFFSET,
        Registers4671.ADC_I1_SCALE_OFFSET,
    ],
    "aenc": [
        Registers4671.AENC_DECODER_MODE,
        Registers4671.AENC_DECODER_PPR,
        Registers4671.ADC_I1_RAW_ADC_I0_RAW,
        Registers4671.ADC_AGPI_A_RAW_ADC_VM_RAW,
        Registers4671.ADC_AENC_UX_RAW_ADC_AGPI_B_RAW,
        Registers4671.ADC_AENC_WY_RAW_ADC_AENC_VN_RAW,
        Registers4671.AENC_DECODER_PHI_A_RAW,
    ],
    "pwm": [
        Registers4671.PWM_POLARITIES,
        Registers4671.PWM_MAXCNT,
        Registers4671.PWM_BBM_H_BBM_L,
        Registers4671.PWM_SV_CHOP,
        Registers4671.MOTOR_TYPE_N_POLE_PAIRS,
    ],
    "pidconf": [
        Registers4671.PID_FLUX_P_FLUX_I,
        Registers4671.PID_TORQUE_P_TORQUE_I,
        Registers4671.PID_VELOCITY_P_VELOCITY_I,
        Registers4671.PID_POSITION_P_POSITION_I,
    ],
    "monitor": [
        Registers4671.ADC_IWY_IUX,
        Registers4671.ADC_IV,
        Registers4671.PID_TORQUE_FLUX_ACTUAL,
        Registers4671.INTERIM_PIDIN_TARGET_TORQUE,
        Registers4671.PID_VELOCITY_ACTUAL,
        Registers4671.INTERIM_PIDIN_TARGET_VELOCITY,
        Registers4671.PID_POSITION_ACTUAL,
        Registers4671.PID_ERROR_PID_POSITION_ERROR,
        Registers4671.PID_ERROR_PID_VELOCITY_ERROR,
    ],
    "pid": [
        Registers4671.PID_FLUX_P_FLUX_I,
        Registers4671.PID_TORQUE_P_TORQUE_I,
        Registers4671.PID_VELOCITY_P_VELOCITY_I,
        Registers4671.PID_POSITION_P_POSITION_I,
        Registers4671.PID_TORQUE_FLUX_TARGET,
        Registers4671.PID_TORQUE_FLUX_OFFSET,
        Registers4671.PID_VELOCITY_TARGET,
        Registers4671.PID_POSITION_TARGET,
        Registers4671.PID_TORQUE_FLUX_ACTUAL,
        Registers4671.INTERIM_PIDIN_TARGET_FLUX,
        Registers4671.PID_ERROR_PID_FLUX_ERROR,
        Registers4671.PID_ERROR_PID_FLUX_ERROR_SUM,
        Registers4671.INTERIM_PIDIN_TARGET_TORQUE,
        Registers4671.PID_ERROR_PID_TORQUE_ERROR,
        Registers4671.PID_ERROR_PID_TORQUE_ERROR_SUM,
        Registers4671.PID_VELOCITY_ACTUAL,
        Registers4671.INTERIM_PIDIN_TARGET_VELOCITY,
        Registers4671.PID_ERROR_PID_VELOCITY_ERROR,
        Registers4671.PID_ERROR_PID_VELOCITY_ERROR_SUM,
        Registers4671.PID_POSITION_ACTUAL,
        Registers4671.INTERIM_PIDIN_TARGET_POSITION,
        Registers4671.PID_ERROR_PID_POSITION_ERROR,
        Registers4671.PID_ERROR_PID_POSITION_ERROR_SUM,
    ],
    "step": [
        Registers4671.STEP_WIDTH,
        Registers4671.PHI_E,
        Registers4671.MODE_RAMP_MODE_MOTION,
        Registers4671.STATUS_FLAGS,
        Registers4671.PID_POSITION_TARGET,
    ],
    "filters": [
        Registers4671.CONFIG_BIQUAD_X_A_1,
        Registers4671.CONFIG_BIQUAD_X_A_2,
        Registers4671.CONFIG_BIQUAD_X_B_0,
        Registers4671.CONFIG_BIQUAD_X_B_1,
        Registers4671.CONFIG_BIQUAD_X_B_2,
        Registers4671.CONFIG_BIQUAD_X_ENABLE,
        Registers4671.CONFIG_BIQUAD_V_A_1,
        Registers4671.CONFIG_BIQUAD_V_A_2,
        Registers4671.CONFIG_BIQUAD_V_B_0,
        Registers4671.CONFIG_BIQUAD_V_B_1,
        Registers4671.CONFIG_BIQUAD_V_B_2,
        Registers4671.CONFIG_BIQUAD_V_ENABLE,
        Registers4671.CONFIG_BIQUAD_T_A_1,
        Registers4671.CONFIG_BIQUAD_T_A_2,
        Registers4671.CONFIG_BIQUAD_T_B_0,
        Registers4671.CONFIG_BIQUAD_T_B_1,
        Registers4671.CONFIG_BIQUAD_T_B_2,
        Registers4671.CONFIG_BIQUAD_T_ENABLE,
        Registers4671.CONFIG_BIQUAD_F_A_1,
        Registers4671.CONFIG_BIQUAD_F_A_2,
        Registers4671.CONFIG_BIQUAD_F_B_0,
        Registers4671.CONFIG_BIQUAD_F_B_1,
        Registers4671.CONFIG_BIQUAD_F_B_2,
        Registers4671.CONFIG_BIQUAD_F_ENABLE,
    ],
}
