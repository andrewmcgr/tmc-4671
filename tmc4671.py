# TMC4671 servo driver support
#
# Copyright (C) 2024       Andrew McGregor <andrewmcgr@gmail.com>
#
# Based heavily on Klipper TMC stepper drivers which are:
#
# Copyright (C) 2018-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math
from time import monotonic_ns
from enum import IntEnum
from statistics import median_low
from .helpers import (
    FieldHelper,
    StepHelper,
    CurrentHelper,
    PIDHelper,
    MCU_TMC_SPI,
    TMCVirtualPinHelper,
)
from .helpers import FIELD_PARSERS
from .register_bank import (
    Fields4671,
    Fields6100,
    Registers4671,
    Registers6100,
    RegisterEnum,
)
from .register_bank import DUMP_GROUPS_4671, DUMP_GROUPS_6100
from .errorcheck import TMCErrorCheck
from .utils import FormatUtils, BiquadUtils, PIDUtils

# The 4671 has a 25 MHz external clock
TMC_FREQUENCY = 25000000.0
# However there is a 100 MHz internal clock, hence 10 ns units in places

# Some magic numbers for the driver


class MotionMode(IntEnum):
    stopped_mode = 0
    torque_mode = 1
    velocity_mode = 2
    position_mode = 3
    uq_ud_ext_mode = 8


class TMC4671:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.stepper_name = " ".join(config.get_name().split()[1:])
        self.name = config.get_name().split()[-1]
        self.init_done = False
        self.mutex = self.printer.get_reactor().mutex()
        self.alignment_done = False

        # 6100 is optional for boards without one.
        gcode = self.printer.lookup_object("gcode")
        if config.get("drv_cs_pin", None) is not None:
            self.field_helper_6100 = FieldHelper(Fields6100, prefix="drv_")
            self.mcu_tmc6100 = MCU_TMC_SPI(
                config,
                self.field_helper_6100,
                12e6,
                pin_option="drv_cs_pin",
            )
            gcode.register_mux_command(
                "DUMP_TMC6100",
                "STEPPER",
                self.name,
                self.cmd_DUMP_TMC6100,
                desc=self.cmd_DUMP_TMC6100_help,
            )
        else:
            self.field_helper_6100 = None
            self.mcu_tmc6100 = None

        self.field_helper = FieldHelper(
            Fields4671,
            prefix="foc_",
        )
        # These will be calibrated later, but this is roughly correct
        self.vm_offset = 32768
        self.vm_range = round(32767 / 2.5)
        # Correct for the OpenFFBoard
        self.voltage_scale = config.getfloat(
            "voltage_scale_ratio", 43.64, above=0.0
        )
        self.mcu_tmc = MCU_TMC_SPI(
            config, self.field_helper, TMC_FREQUENCY, pin_option="cs_pin"
        )

        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )
        self.printer.register_event_handler("klippy:ready", self._handle_ready)

        self.stepper = None

        self.stepper_enable = self.printer.load_object(config, "stepper_enable")
        self.printer.register_event_handler(
            "klippy:mcu_identify", self._handle_mcu_identify
        )
        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )
        # Register commands
        self.step_helper = StepHelper(config, self.mcu_tmc)
        self.current_helper = CurrentHelper(config, self.mcu_tmc)
        self.error_helper = TMCErrorCheck(config, self.mcu_tmc)
        TMCVirtualPinHelper(config, self.mcu_tmc, self.current_helper)
        gcode.register_mux_command(
            "SET_TMC_FIELD",
            "STEPPER",
            self.name,
            self.cmd_SET_TMC_FIELD,
            desc=self.cmd_SET_TMC_FIELD_help,
        )
        gcode.register_mux_command(
            "DUMP_TMC",
            "STEPPER",
            self.name,
            self.cmd_DUMP_TMC,
            desc=self.cmd_DUMP_TMC_help,
        )
        gcode.register_mux_command(
            "TMC_DEBUG_MOVE",
            "STEPPER",
            self.name,
            self.cmd_TMC_DEBUG_MOVE,
            desc=self.cmd_TMC_DEBUG_MOVE_help,
        )
        gcode.register_mux_command(
            "TMC_TUNE_PID",
            "STEPPER",
            self.name,
            self.cmd_TMC_TUNE_PID,
            desc=self.cmd_TMC_TUNE_PID_help,
        )
        gcode.register_mux_command(
            "INIT_TMC",
            "STEPPER",
            self.name,
            self.cmd_INIT_TMC,
            desc=self.cmd_INIT_TMC_help,
        )
        gcode.register_mux_command(
            "SET_TMC_CURRENT",
            "STEPPER",
            self.name,
            self.cmd_SET_TMC_CURRENT,
            desc=self.cmd_SET_TMC_CURRENT_help,
        )
        # Allow other registers to be set from the config
        if self.field_helper_6100 is not None:
            # defaults as per 4671+6100 BOB datasheet
            self.field_helper_6100.set_config_field(
                config, Fields6100.SINGLELINE, 0
            )
            self.field_helper_6100.set_config_field(
                config, Fields6100.NORMAL, 1
            )
            self.field_helper_6100.set_config_field(
                config, Fields6100.DRVSTRENGTH, 0
            )
            self.field_helper_6100.set_config_field(
                config, Fields6100.BBMCLKS, 10
            )

        set_config_field = self.field_helper.set_config_field

        # This should not really be set to anything else
        # therefore not providing convenience interface
        # maxcnt = 3999 # 25 kHz
        # maxcnt = 1999 # 50 kHz
        # maxcnt = 1599 # 62.5 kHz
        maxcnt = 999  # 100 kHz
        # maxcnt = 699 # ~143 kHz
        set_config_field(config, "PWM_MAXCNT", maxcnt)

        # These are used later by filter definitions
        self.pwmfreq = 4.0 * TMC_FREQUENCY / (maxcnt + 1.0)
        self.pwmT = (maxcnt + 1.0) * 10e-9
        self.mdec = round(self.pwmT / (3.0 * 40e-9) - 2)
        set_config_field(config, Fields4671.DSADC_MDEC_A, self.mdec)
        set_config_field(config, Fields4671.DSADC_MDEC_B, self.mdec)
        set_config_field(config, Fields4671.PWM_BBM_L, 10)
        set_config_field(config, Fields4671.PWM_BBM_H, 10)
        set_config_field(config, Fields4671.PWM_CHOP, 7)
        set_config_field(config, Fields4671.PWM_SV, 1)
        set_config_field(config, Fields4671.MOTOR_TYPE, 3)
        set_config_field(config, Fields4671.N_POLE_PAIRS, 4)
        set_config_field(config, Fields4671.ADC_I_UX_SELECT, 0)
        set_config_field(config, Fields4671.ADC_I_V_SELECT, 2)
        set_config_field(config, Fields4671.ADC_I_WY_SELECT, 1)
        set_config_field(config, Fields4671.ADC_I0_SELECT, 0)
        set_config_field(config, Fields4671.ADC_I1_SELECT, 1)
        # set_config_field(config, Fields4671.CFG_ADC_I0, 0)
        # set_config_field(config, Fields4671.CFG_ADC_I1, 0)
        # set_config_field(config, Fields4671.CFG_ADC_VM, 4)
        set_config_field(
            config, Fields4671.AENC_DEG, 1
        )  # 120 degree analog hall
        set_config_field(
            config, Fields4671.AENC_PPR, 1
        )  # 120 degree analog hall
        set_config_field(config, Fields4671.ABN_APOL, 0)
        set_config_field(config, Fields4671.ABN_BPOL, 0)
        set_config_field(config, Fields4671.ABN_NPOL, 0)
        set_config_field(config, Fields4671.ABN_USE_ABN_AS_N, 0)
        set_config_field(config, Fields4671.ABN_CLN, 0)
        set_config_field(config, Fields4671.ABN_DIRECTION, 0)
        set_config_field(config, Registers4671.ABN_DECODER_PPR, 1600)
        set_config_field(config, Fields4671.HALL_INTERP, 0)
        set_config_field(config, Fields4671.HALL_SYNC, 1)
        set_config_field(config, Fields4671.HALL_POLARITY, 0)
        set_config_field(config, Fields4671.HALL_DIR, 0)
        set_config_field(config, Registers4671.HALL_DPHI_MAX, 0xAAAA)
        set_config_field(config, Fields4671.HALL_PHI_E_OFFSET, 0)
        set_config_field(config, Fields4671.HALL_BLANK, 2)

        # 3: ABN, 5: Hall
        set_config_field(config, Registers4671.PHI_E_SELECTION, 3)
        # 0: phi_e, 3: ABN_e 5: Hall_e 9: ABN_m 12: Hall_m
        set_config_field(config, Registers4671.POSITION_SELECTION, 9)
        set_config_field(config, Fields4671.VELOCITY_SELECTION, 3)

        # set_config_field(config, Fields4671.VELOCITY_METER_SELECTION, 0) # Default velocity meter
        set_config_field(
            config, Fields4671.VELOCITY_METER_SELECTION, 1
        )  # PWM frequency velocity meter

        set_config_field(config, Fields4671.MODE_PID_SMPL, 0)
        # Advanced PID samples position at fPWM
        set_config_field(
            config, Fields4671.MODE_PID_TYPE, 1
        )  # Advanced PID mode
        set_config_field(
            config, Registers4671.PIDOUT_UQ_UD_LIMITS, 31500
        )  # Voltage limit, 32768 = Vm
        # TODO: get this from the size of the printer
        set_config_field(
            config, Registers4671.PID_POSITION_LIMIT_LOW, -0x10000000
        )
        set_config_field(
            config, Registers4671.PID_POSITION_LIMIT_HIGH, 0x10000000
        )
        # TODO: Units, what should this be anyway?
        set_config_field(config, Registers4671.PID_VELOCITY_LIMIT, 0x100000)
        pid_defaults = [
            (Fields4671.PID_FLUX_P, 9.4, Fields4671.CURRENT_P_n, 0),
            (Fields4671.PID_FLUX_I, 0.087, Fields4671.CURRENT_I_n, 1),
            (Fields4671.PID_TORQUE_P, 9.4, Fields4671.CURRENT_P_n, 0),
            (Fields4671.PID_TORQUE_I, 0.087, Fields4671.CURRENT_I_n, 1),
            (Fields4671.PID_VELOCITY_P, 4.5, Fields4671.VELOCITY_P_n, 0),
            (Fields4671.PID_VELOCITY_I, 0.0, Fields4671.VELOCITY_I_n, 1),
            (Fields4671.PID_POSITION_P, 2.5, Fields4671.POSITION_P_n, 0),
            (Fields4671.PID_POSITION_I, 0.0, Fields4671.POSITION_I_n, 1),
        ]
        self.pid_helpers = {
            field: PIDHelper(config, self.mcu_tmc, field, val, n_field, n_val)
            for field, val, n_field, n_val in pid_defaults
        }
        self.monitor_data = {
            n: None
            for reg in DUMP_GROUPS_4671["monitor"]
            for n in self.field_helper.get_reg_fields(reg, 0)
        }

    def _read_field(self, field):
        return self.mcu_tmc.read_field(field)

    def _write_field(self, field, val):
        return self.mcu_tmc.write_field(field, val)

    def enable_biquad(self, enable_field, *biquad):
        reg = self.field_helper.lookup_register_info(enable_field).value
        reg_addr, sub_addr = reg.reg_addr, reg.sub_addr
        for o, i in enumerate(biquad):
            self.mcu_tmc.tmc_spi.reg_write(reg_addr + 1, sub_addr - 6 + o)
            self.mcu_tmc.tmc_spi.reg_write(reg_addr, i)
        self.mcu_tmc.tmc_spi.reg_write(reg_addr + 1, sub_addr)
        self.mcu_tmc.tmc_spi.reg_write(reg_addr, 1)

    def disable_biquad(self, enable_field):
        reg = self.field_helper.lookup_register_info(enable_field).value
        reg_addr, sub_addr = reg.reg_addr, reg.sub_addr

        self.mcu_tmc.tmc_spi.reg_write(reg_addr + 1, sub_addr)
        self.mcu_tmc.tmc_spi.reg_write(reg_addr, 0)

    def _do_enable(self, print_time):
        try:
            with self.mutex:
                self._write_field(
                    Registers4671.PID_POSITION_TARGET,
                    self._read_field(Registers4671.PID_POSITION_ACTUAL),
                )
                self.error_helper.start_checks()
                self._write_field(
                    Fields4671.MODE_MOTION, MotionMode.position_mode
                )
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))

    def _do_disable(self, print_time):
        try:
            with self.mutex:
                self.error_helper.stop_checks()
                # Switching off the enable line will turn off the drivers
                # but, belt and braces, stop the controller as well.
                self._write_field(
                    Fields4671.MODE_MOTION, MotionMode.stopped_mode
                )
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))

    def _handle_mcu_identify(self):
        # Lookup stepper object
        force_move = self.printer.lookup_object("force_move")
        self.stepper = force_move.lookup_stepper(self.stepper_name)
        # Note default pulse duration and step_both_edge unavailable
        self.stepper.setup_default_pulse_duration(0.000000100, False)

    def _handle_stepper_enable(self, print_time, is_enable):
        if is_enable:

            def cb(ev):
                self._do_enable(print_time)
        else:

            def cb(ev):
                self._do_disable(print_time)

        self.printer.get_reactor().register_callback(cb)

    def _handle_connect(self):
        print_time = self.printer.lookup_object("toolhead").get_last_move_time()
        # Check for soft stepper enable/disable
        enable_line = self.stepper_enable.lookup_enable(self.stepper_name)
        # Send init
        try:
            self._init_registers()
        except self.printer.command_error as e:
            logging.info("TMC %s failed to init: %s", self.name, str(e))
            raise e
        enable_line.register_state_callback(self._handle_stepper_enable)

    def _handle_ready(self, print_time=None):
        # XXX why are we re-writing all the fields after enable?
        with self.mutex:
            if print_time is None:
                print_time = self.printer.lookup_object(
                    "toolhead"
                ).get_last_move_time()
            # Set these before setting enable to avoid yeeting the toolhead
            self._write_field(Fields4671.MODE_MOTION, MotionMode.stopped_mode)
            self._write_field(Registers4671.STATUS_MASK, 0)
            self._write_field(Fields4671.PID_FLUX_TARGET, 0)
            self._write_field(Fields4671.PID_TORQUE_TARGET, 0)
            self._write_field(Registers4671.PID_VELOCITY_TARGET, 0)
            self._write_field(Registers4671.ABN_DECODER_COUNT, 0)
            self._write_field(Registers4671.PID_POSITION_TARGET, 0)
            # Now enable 6100
            if self.field_helper_6100 is not None:
                self.mcu_tmc6100.set_register(
                    Registers6100.GCONF,
                    self.field_helper_6100.set_field(Fields6100.DISABLE, 0),
                    print_time,
                )
            enable_line = self.stepper_enable.lookup_enable(self.stepper_name)
            enable_line.motor_enable(print_time)
            # Just test the PID, as it also sets up the encoder offsets
            P, I = self._tune_flux_pid(True, 1.0, print_time)
            self._write_field(Registers4671.ABN_DECODER_COUNT, 0)
            self._write_field(Registers4671.PID_POSITION_TARGET, 0)
            print_time = self.printer.lookup_object(
                "toolhead"
            ).get_last_move_time()
            enable_line.motor_disable(print_time)
            self.alignment_done = True
            self._write_field(Registers4671.STATUS_MASK, 0)
            self._write_field(Fields4671.PID_FLUX_TARGET, 0)
            self._write_field(Fields4671.PID_TORQUE_TARGET, 0)
            self._write_field(Registers4671.PID_VELOCITY_TARGET, 0)
            self._write_field(Registers4671.ABN_DECODER_COUNT, 0)
            self._write_field(Registers4671.PID_POSITION_TARGET, 0)
            self._write_field(Fields4671.MODE_MOTION, MotionMode.stopped_mode)
            self.init_done = True

    def _calibrate_adc(self, print_time):
        self._write_field(Fields4671.PWM_CHOP, 0)
        self._write_field(Fields4671.CFG_ADC_I0, 0)
        self._write_field(Fields4671.CFG_ADC_I1, 0)
        i0_off, i1_off = self._sample_adc(Registers4671.ADC_I1_RAW_ADC_I0_RAW)

        # Following code would calibrate the scalers as well.
        # However, not doing that makes things simpler, and the
        # calibration result is always +- 1 from nominal.
        # self._write_field(Fields4671.CFG_ADC_I0, 2)
        # self._write_field(Fields4671.CFG_ADC_I1, 2)
        # i0_l, i1_l = self._sample_adc(Registers4671.ADC_I1_RAW_ADC_I0_RAW)
        # self._write_field(Fields4671.CFG_ADC_I0, 3)
        # self._write_field(Fields4671.CFG_ADC_I1, 3)
        # i0_h, i1_h = self._sample_adc(Registers4671.ADC_I1_RAW_ADC_I0_RAW)
        # self._write_field(Fields4671.CFG_ADC_I0, 0)
        # self._write_field(Fields4671.CFG_ADC_I1, 0)
        # self._write_field(Fields4671.ADC_I1_SCALE, (256*(i1_h-i1_l))//32768)
        # self._write_field(Fields4671.ADC_I0_SCALE, (256*(i0_h-i0_l))//32768)

        self._write_field(Fields4671.ADC_I1_SCALE, 256)
        self._write_field(Fields4671.ADC_I0_SCALE, 256)
        self._write_field(Fields4671.ADC_I1_OFFSET, i1_off)
        self._write_field(Fields4671.ADC_I0_OFFSET, i0_off)
        # Calibrate for VM measurement
        # Chip errata? This doesn't work.
        # self._write_field(Fields4671.CFG_ADC_VM, 5)
        # vml, vmh = self._sample_vm()
        # self.vm_offset = round(mean((vml, vmh)))
        # self._write_field(Fields4671.CFG_ADC_VM, 7)
        # vml, vmh = self._sample_vm()
        # self.vm_range = self.vm_offset - round(mean((vml, vmh)))
        # self._write_field(Fields4671.CFG_ADC_VM, 4)

        # logging.info("TMC 4671 %s ADC VM offset=%d range=%s VM=%g", self.name,
        #             self.vm_offset, self.vm_range, self._read_vm())
        # Now calibrate for brake chopper
        vml, vmh = self._sample_vm()
        logging.info("TMC 4671 %s ADC VM %s", self.name, str(vml, vmh))
        vmr = abs(vmh - vml)
        logging.info(
            "TMC 4671 %s VM samples low=%d high=%d", self.name, vml, vmh
        )
        high = math.ceil(0.15 * self.voltage_scale) + vmr + vmh
        if high < 65536:
            self._write_field(Fields4671.ADC_VM_LIMIT_HIGH, high)
            self._write_field(Fields4671.ADC_VM_LIMIT_LOW, vmr + vmh)
            logging.info(
                "TMC 4671 %s brake thresholds low=%d(%g V) high=%d(%g V)",
                self.name,
                vmr + vmh,
                self._convert_vm(vmr + vmh),
                high,
                self._convert_vm(high),
            )
        else:
            # What else can we do but turn the brake off?
            self._write_field(Fields4671.ADC_VM_LIMIT_HIGH, 0)
            self._write_field(Fields4671.ADC_VM_LIMIT_LOW, 0)
        self._write_field(Fields4671.PWM_CHOP, 7)

    def _sample_adc(self, reg: RegisterEnum):
        self.printer.lookup_object("toolhead").dwell(0.2)
        reg_addr, sub_addr = reg.value.reg_addr, reg.value.sub_addr
        self.mcu_tmc.tmc_spi.reg_write(reg_addr + 1, sub_addr)
        i1 = []
        i0 = []
        n = 100
        for i in range(n):
            v = self.field_helper.get_reg_fields(
                reg, self.mcu_tmc.raw_reg_read(reg)
            )
            i1.append(v[Fields4671.ADC_I1_RAW.name])
            i0.append(v[Fields4671.ADC_I0_RAW.name])

            self.printer.lookup_object("toolhead").dwell(0.0005)

        return median_low(i0), median_low(i1)

    def _convert_vm(self, val):
        return (
            (val - self.vm_offset) / float(self.vm_range)
        ) * self.voltage_scale

    def _read_vm(self):
        return self._convert_vm(self._read_field(Fields4671.ADC_VM_RAW))

    def _sample_vm(self):
        self.printer.lookup_object("toolhead").dwell(0.2)
        vm = []
        n = 100
        for i in range(n):
            vm.append(self._read_field(Fields4671.ADC_VM_RAW))
            self.printer.lookup_object("toolhead").dwell(0.0005)
        return min(vm), max(vm)

    def _tune_flux_pid(self, test_existing, derate, print_time):
        return self._tune_pid(
            "FLUX", 2.5, derate, True, test_existing, print_time
        )

    def _tune_torque_pid(self, test_existing, derate, print_time):
        return self._tune_pid(
            "TORQUE", 1.0, derate, True, test_existing, print_time
        )

    # Align motors and tune PID via a setpoint change experiment
    # See https://folk.ntnu.no/skoge/publications/2012/skogestad-improved-simc-pid/PIDbook-chapter5.pdf
    def _tune_pid(self, X, Kc, derate, offsets, test_existing, print_time):
        ch = self.current_helper
        dwell = self.printer.lookup_object("toolhead").dwell

        target_field_name = f"PID_{X}_TARGET"
        target_field = self.field_helper.lookup_field_info(target_field_name)
        actual_field_name = f"PID_{X}_ACTUAL"
        actual_field = self.field_helper.lookup_field_info(actual_field_name)
        p_field_name = f"PID_{X}_P"
        p_field = self.field_helper.lookup_field_info(p_field_name)
        i_field_name = f"PID_{X}_I"
        i_field = self.field_helper.lookup_field_info(i_field_name)

        old_mode = self._read_field(Fields4671.MODE_MOTION)
        old_phi_e_selection = self._read_field(Registers4671.PHI_E_SELECTION)
        self._write_field(Fields4671.MODE_MOTION, MotionMode.stopped_mode)

        limit_cur = self._read_field(Registers4671.PID_TORQUE_FLUX_LIMITS)

        old_flux_offset = self._read_field(Fields4671.PID_FLUX_OFFSET)
        self._write_field(
            Registers4671.PHI_E_EXT, 0
        )  # and, set this to be PHI_E = 0
        self._write_field(
            Registers4671.PHI_E_SELECTION, 1
        )  # external mode, so it won't change.

        # Start at some low voltage and see if we can read a current
        test_U = round(self.vm_range / self.voltage_scale)  # Should be about 1V
        self._write_field(Fields4671.UQ_EXT, 0)
        self._write_field(Fields4671.UD_EXT, test_U)

        self._write_field(Fields4671.PID_TORQUE_TARGET, 0)
        self._write_field(Registers4671.PID_VELOCITY_TARGET, 0)
        self._write_field(Registers4671.PID_POSITION_TARGET, 0)
        self._write_field(Registers4671.PID_POSITION_ACTUAL, 0)
        self._write_field(Fields4671.MODE_MOTION, MotionMode.uq_ud_ext_mode)
        # Turn on the chopper and wait a bit to measure the resistance
        self._write_field(Fields4671.PWM_CHOP, 7)
        dwell(0.1)
        c, MAX_I, iux, iv, iwy = self.current_helper.get_current()
        self._write_field(Fields4671.PWM_CHOP, 0)
        logging.info(
            "TMC 4671 '%s' initial I %s",
            self.stepper_name,
            str(self.current_helper.get_current()),
        )
        if max(abs(iux), abs(iwy)) < 1e-6:
            # something is horribly wrong
            raise self.printer.command_error(
                "TMC 4671 is seeing no motor current. Check wiring."
            )
        # Ok, calculate a voltage that will give us about a third of the configured current limit
        test2_U = round((c / 2.0) * test_U / max(abs(iux), abs(iwy)))
        logging.info(
            "TMC 4671 '%s' test U %g %g", self.stepper_name, test_U, test2_U
        )
        # Switch back on, and this time motor should self-align
        self._write_field(Fields4671.UD_EXT, test2_U)
        self._write_field(Fields4671.PWM_CHOP, 7)
        dwell(0.1)
        c, MAX_I, iux, iv, iwy = self.current_helper.get_current()
        logging.info(
            "TMC 4671 '%s' alignment I %s",
            self.stepper_name,
            str(self.current_helper.get_current()),
        )
        test2_U / (self.vm_range / self.voltage_scale)
        R = (
            test2_U
            * self.voltage_scale
            / (self.vm_range * max(abs(iux), abs(iwy)))
        )
        logging.info("TMC 4671 '%s' est. motor R=%g", self.stepper_name, R)
        for i in range(5):
            dwell(0.2)
            self._write_field(Fields4671.PWM_CHOP, 0)
            # Give it some time to settle
            dwell(0.1)
            self._write_field(Fields4671.PWM_CHOP, 7)
        # Give it some time to settle
        dwell(0.2)
        # Now we should be mechanically aligned
        if offsets:
            # While we're here, set the offsets
            (
                self._write_field(
                    Fields4671.HALL_PHI_E_OFFSET,
                    -self._read_field(Fields4671.HALL_PHI_E) % 65536,
                ),
            )
            self._write_field(Registers4671.ABN_DECODER_COUNT, 0)
            self._write_field(Fields4671.ABN_DECODER_PHI_E_OFFSET, 0)
        self._write_field(Fields4671.MODE_MOTION, MotionMode.stopped_mode)
        # Give it some time to settle
        dwell(0.1)
        self._write_field(Fields4671.MODE_MOTION, MotionMode.torque_mode)
        test_cur = limit_cur  # // 2
        # old_cur = self._read_field(actual_field)
        dwell(0.1)
        if not test_existing:
            Kc0 = Kc
            self.pid_helpers[p_field].write_coefficient(Kc)
            self.pid_helpers[i_field].write_coefficient(0.0)
        else:
            Kc0 = FormatUtils.from_q4_12(self._read_field(p_field))
        # Do a setpoint change experiment
        self._write_field(target_field, 0)
        logging.info(f"test_cur = {test_cur}")
        n = 100
        c = self._dump_pid(n, X)
        self._write_field(target_field, test_cur)
        c += self._dump_pid(n, X)
        # Experiment over, switch off
        self._write_field(target_field, 0)
        # Put motion config back how it was
        self._write_field(Fields4671.PID_TORQUE_TARGET, 0)
        self._write_field(Registers4671.PID_VELOCITY_TARGET, 0)
        self._write_field(Registers4671.PID_POSITION_TARGET, 0)
        self._write_field(Registers4671.PID_POSITION_ACTUAL, 0)
        self._write_field(Fields4671.MODE_MOTION, old_mode)
        self._write_field(Fields4671.PID_FLUX_OFFSET, old_flux_offset)
        self._write_field(Registers4671.PHI_E_SELECTION, old_phi_e_selection)
        # Analysis and logging
        # for r in c:
        #    logging.info("%g,%s"%(float(r[0]-c[0][0])/1e9,','.join(map(str, r[1:]))))
        # At this point we can determine system model
        y0 = sum(float(a[1]) for a in c[0:n]) / float(n)
        yinf = (
            sum(float(a[1]) for a in c[3 * n // 2 : 2 * n])
            / float(2 * n - 3 * n // 2)
            - y0
        )
        if yinf < 0.0:
            # Wups, turned out negative...
            yinf *= -1.0
            c = [(t, -y) for t, y in c]
        yp = -100000  # Not a possible value
        tp = 0
        for tpt, ypt in c[n + 1 : -1]:
            if ypt < yp:
                break
            yp, tp = ypt, tpt
        yp -= y0
        # It is better to overestimate tp than under.
        # tp -= float(c[n][0] + c[n+1][0])/2.0
        tp -= c[n][0]
        tp *= 1e-9  # it was in nanoseconds, we want seconds
        D = (yp - yinf) / yinf
        B = abs((test_cur - yinf) / yinf)
        A = 1.152 * D**2 - 1.607 * D + 1
        r = 2 * A / B
        logging.info("yinf = %g, yp = %g, tp = %g" % (yinf, yp, tp))
        k = 1.0 / (Kc0 * B)
        theta = tp * (0.309 + 0.209 * math.exp(-0.61 * r))
        tau1 = r * theta
        logging.info(
            "TMC 4671 %s %s PID system model k=%g, theta=%g, tau1=%g"
            % (
                self.name,
                X,
                k,
                theta,
                tau1,
            )
        )
        Kc, taui = PIDUtils.simc(k, theta, tau1, 2.0 * derate / self.pwmfreq)
        # Account for sampling frequency etc
        Kc *= 2.0
        Ki = 2.0 * Kc / (taui * self.pwmfreq)
        logging.info(
            "TMC 4671 %s %s PID coefficients Kc=%g, Ti=%g (Ki=%g)"
            % (self.name, X, Kc, taui, Ki)
        )
        if not test_existing:
            self.pid_helpers[p_field].write_coefficient(Kc)
            self.pid_helpers[i_field].write_coefficient(Ki)
            # Store results for SAVE_CONFIG
            cfgname = "tmc4671 %s" % (self.name,)
            configfile = self.printer.lookup_object("configfile")
            configfile.set(cfgname, "foc_PID_FLUX_P", "%.3f" % (Kc,))
            configfile.set(cfgname, "foc_PID_FLUX_I", "%.3f" % (Ki,))
            configfile.set(cfgname, "foc_PID_TORQUE_P", "%.3f" % (Kc,))
            configfile.set(cfgname, "foc_PID_TORQUE_I", "%.3f" % (Ki,))
        return Kc, Ki

    def _dump_pid(self, num, X):
        field_name = f"PID_{X}_ACTUAL"
        c = [(0, 0)] * (num)
        for i in range(num):
            cur = self._read_field(field_name)
            c[i] = (
                monotonic_ns(),
                cur,
            )
        return c

    def ping(self):
        ping = self.mcu_tmc.get_register(Registers4671.CHIPINFO_SI_TYPE)
        if ping != 0x34363731:
            raise self.printer.command_error(
                "TMC 4671 not identified, identification register returned %x"
                % (ping,)
            )

    def _init_registers(self, print_time=None):
        with self.mutex:
            if print_time is None:
                print_time = self.printer.lookup_object(
                    "toolhead"
                ).get_last_move_time()
            ping = self.mcu_tmc.get_register(Registers4671.CHIPINFO_SI_TYPE)
            if ping != 0x34363731:
                raise self.printer.command_error(
                    "TMC 4671 not identified, identification register returned %x"
                    % (ping,)
                )
            # Disable 6100
            if self.field_helper_6100 is not None:
                self.mcu_tmc6100.set_register(
                    Registers6100.GCONF,
                    self.field_helper_6100.set_field(Fields6100.DISABLE, 1),
                    print_time,
                )
            self.mcu_tmc.set_register_once(Registers4671.STATUS_FLAGS, 0)
            # Set torque and current in 4671 to zero
            self._write_field(Fields4671.PID_FLUX_TARGET, 0)
            self._write_field(Fields4671.PID_TORQUE_TARGET, 0)
            self._write_field(Registers4671.PID_VELOCITY_TARGET, 0)
            self._write_field(Registers4671.PID_POSITION_TARGET, 0)
            self._write_field(Fields4671.PWM_CHOP, 7)
            # Send registers, 6100 first if configured then 4671
            if self.field_helper_6100 is not None:
                self.mcu_tmc6100.write_register_cache(print_time)

            self.mcu_tmc.write_register_cache(print_time)

            self._calibrate_adc(print_time)
            # setup filters
            self.enable_biquad(
                Registers4671.CONFIG_BIQUAD_F_ENABLE,
                *BiquadUtils.biquad_tmc(
                    *BiquadUtils.biquad_lpf(self.pwmfreq, 1600, 1.0 / 2.0**0.5)
                ),
            )
            self.enable_biquad(
                Registers4671.CONFIG_BIQUAD_T_ENABLE,
                *BiquadUtils.biquad_tmc(
                    *BiquadUtils.biquad_lpf(self.pwmfreq, 1600, 1.0 / 2.0**0.5)
                ),
            )
            self.enable_biquad(
                Registers4671.CONFIG_BIQUAD_X_ENABLE,
                *BiquadUtils.biquad_tmc(
                    *BiquadUtils.biquad_lpf(
                        self.pwmfreq
                        / (self._read_field(Fields4671.MODE_PID_SMPL) + 1.0),
                        3200,
                        1.0 / 2**0.5,
                    )
                ),
            )
            self.enable_biquad(
                Registers4671.CONFIG_BIQUAD_V_ENABLE,
                *BiquadUtils.biquad_tmc(
                    *BiquadUtils.biquad_lpf(self.pwmfreq, 8000, 1.0 / 2**0.5)
                ),
            )
            # *BiquadUtils.biquad_tmc(*BiquadUtils.biquad_lpf_tmc(self.pwmfreq, 4500, 2.0)))
            # *BiquadUtils.biquad_tmc(*BiquadUtils.biquad_apf(self.pwmfreq, 296, 2**-0.5)))
            self._write_field(Registers4671.CONFIG_BIQUAD_F_ENABLE, 1)
            self._write_field(Registers4671.CONFIG_BIQUAD_T_ENABLE, 1)
            self._write_field(Registers4671.CONFIG_BIQUAD_V_ENABLE, 0)
            self._write_field(Registers4671.CONFIG_BIQUAD_X_ENABLE, 0)

    def get_status(self, eventtime=None):
        if not self.init_done:
            return {}
        current = self.current_helper.get_current()
        res = {
            "run_current": current[0],
            "current_ux": current[2],
            "current_v": current[3],
            "current_wy": current[4],
        }
        for reg in DUMP_GROUPS_4671["monitor"]:
            val = self.mcu_tmc.get_register(reg)
            self.monitor_data.update(self.field_helper.get_reg_fields(reg, val))
        res.update(self.monitor_data)
        res.update(self.error_helper.get_status(eventtime))
        return res

    cmd_INIT_TMC_help = "Initialize TMC stepper driver registers"

    def cmd_INIT_TMC(self, gcmd):
        logging.info("INIT_TMC %s", self.name)
        print_time = self.printer.lookup_object("toolhead").get_last_move_time()
        self._init_registers(print_time)

    cmd_TMC_TUNE_PID_help = "Tune the current and torque PID coefficients"

    def cmd_TMC_TUNE_PID(self, gcmd):
        test_existing = gcmd.get_int("CHECK", 0)
        derate = gcmd.get_float("DERATE", 1.6)
        logging.info(f"TMC_TUNE_PID {self.name}")
        print_time = self.printer.lookup_object("toolhead").get_last_move_time()
        P, I = self._tune_flux_pid(test_existing, derate, print_time)
        with self.mutex:
            self.pid_helpers[Fields4671.PID_TORQUE_P].write_coefficient(P)
            self.pid_helpers[Fields4671.PID_TORQUE_I].write_coefficient(I)
        gcmd.respond_info(
            f"PID {self.name} parameters: Kc={P:.2f} Ki={I:.3f}\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with these parameters and restart the printer."
        )

    cmd_TMC_DEBUG_MOVE_help = (
        "Test TMC motion mode (motor must be free to move)"
    )

    def cmd_TMC_DEBUG_MOVE(self, gcmd):
        logging.info(f"TMC_DEBUG_MOVE {self.name}")
        velocity = gcmd.get_int("VELOCITY", None)
        torque = gcmd.get_int("TORQUE", None)
        pos = gcmd.get_int("POSITION", None)
        open_loop_velocity = gcmd.get_int("OPENVEL", None)
        print_time = self.printer.lookup_object("toolhead").get_last_move_time()
        if velocity is not None:
            self._debug_pid_motion(
                velocity,
                MotionMode.velocity_mode,
                Registers4671.PID_VELOCITY_TARGET,
                print_time,
            )
        elif torque is not None:
            self._debug_pid_motion(
                torque, MotionMode.torque_mode, "PID_TORQUE_TARGET", print_time
            )
        elif pos is not None:
            self._debug_pid_motion(
                pos, MotionMode.position_mode, "PID_POSITION_TARGET", print_time
            )
        elif open_loop_velocity is not None:
            self._debug_openloop_velocity_motion(open_loop_velocity, print_time)

    def _debug_pid_motion(self, velocity, mode, target_reg, print_time):
        with self.mutex:
            # self._write_field(Fields4671.PWM_CHOP, 7)
            old_mode = self._read_field(Fields4671.MODE_MOTION)
            self._write_field(Registers4671.PID_POSITION_ACTUAL, 0)
            self.printer.lookup_object("toolhead").dwell(0.2)
            # Clear all the status flags for later reference
            self.mcu_tmc.set_register_once(
                Registers4671.STATUS_FLAGS, 0, print_time
            )
            # limit_cur = self._read_field(Registers4671.PID_TORQUE_FLUX_LIMITS)
            self._write_field(Fields4671.PID_FLUX_TARGET, 0)
            self._write_field(Fields4671.PID_TORQUE_TARGET, 0)
            self._write_field(target_reg, 0)
            self._write_field(Fields4671.MODE_MOTION, mode)
            n2 = 20
            if mode == MotionMode.stopped_mode:
                v = [velocity * i // (2 * n2) for i in range(n2, 2 * n2)] + [
                    velocity for i in range(n2 * 2)
                ]
            else:
                v = [velocity for i in range(n2, 2 * n2)] + [
                    velocity for i in range(n2 * 2)
                ]
            n = 500
            c = self._dump_motion(
                n, f=lambda x: self._write_field(target_reg, x), v=v
            )
            self._write_field(Fields4671.MODE_MOTION, old_mode)
            self._write_field(target_reg, 0)
            # self._write_field(Fields4671.PWM_CHOP, 0)
        for i in range(n):
            logging.info(",".join(map(str, c[i])))

    def _dump_motion(self, n, f=None, v=None):
        n2 = n
        if v is not None:
            n2 = len(v) + 1
        iv = 0
        c = [(0, 0)] * (n)
        for i in range(n):
            if f is not None and i % n2 == 0:
                f(v[i // n2])
            c[i] = (
                monotonic_ns() / 1e9,
                self._read_field(Registers4671.PID_POSITION_ACTUAL),
                self._read_field(Registers4671.PID_VELOCITY_ACTUAL),
                self._read_field(Registers4671.PID_ERROR_PID_VELOCITY_ERROR),
                self._read_field(Registers4671.INTERIM_PIDIN_TARGET_TORQUE),
                self._read_field(Fields4671.PID_TORQUE_ACTUAL),
                self._read_field(Registers4671.PID_ERROR_PID_TORQUE_ERROR),
                self._read_field(Registers4671.PID_ERROR_PID_TORQUE_ERROR_SUM),
                self._read_field(Registers4671.INTERIM_PIDIN_TARGET_FLUX),
                self._read_field(Fields4671.PID_FLUX_ACTUAL),
                self._read_field(Registers4671.PID_ERROR_PID_FLUX_ERROR),
                self._read_field(Registers4671.PID_ERROR_PID_FLUX_ERROR_SUM),
                ":::",
                self._read_field(Fields4671.ADC_I0_RAW),
                self._read_field(Fields4671.ADC_I1_RAW),
                self._read_field(Fields4671.ADC_IUX),
                self._read_field(Fields4671.INTERIM_PWM_UX),
                self._read_field(Registers4671.ADC_IV),
                self._read_field(Registers4671.INTERIM_PWM_UV),
                self._read_field(Fields4671.ADC_IWY),
                self._read_field(Fields4671.INTERIM_PWM_WY),
                ":::",
                self._read_field(Fields4671.ABN_DECODER_PHI_M) % 65536,
                self._read_field(Fields4671.ABN_DECODER_PHI_E) % 65536,
                self._read_field(Registers4671.HALL_PHI_M) % 65536,
                self._read_field(Fields4671.HALL_PHI_E) % 65536,
                self._read_field(Registers4671.PHI_E) % 65536,
                (
                    self._read_field(Registers4671.PHI_E)
                    - self._read_field(Fields4671.HALL_PHI_E)
                )
                % 65536,
                (
                    self._read_field(Registers4671.PHI_E)
                    - self._read_field(Fields4671.ABN_DECODER_PHI_E)
                )
                % 65536,
            )
            self.printer.lookup_object("toolhead").dwell(15.0 / n)
        return c

    def _debug_openloop_velocity_motion(self, velocity, print_time):
        with self.mutex:
            self._write_field(Fields4671.PWM_CHOP, 7)
            self._write_field(Fields4671.MODE_MOTION, MotionMode.uq_ud_ext_mode)
            limit_cur = self._read_field(Registers4671.PID_TORQUE_FLUX_LIMITS)
            self._write_field(Fields4671.UD_EXT, limit_cur)
            self._write_field(Fields4671.UQ_EXT, 0)
            old_phi_e_sel = self._read_field(Registers4671.PHI_E_SELECTION)
            self._write_field(Registers4671.PHI_E_SELECTION, 2)
            phi_e = self._read_field(Registers4671.PHI_E)
            # Clear all the status flags for later reference
            self.mcu_tmc.set_register_once(
                Registers4671.STATUS_FLAGS, 0, print_time
            )
            # might not stick, so write with a one-shot
            n = 500
            self._write_field(Registers4671.OPENLOOP_VELOCITY_TARGET, velocity)
            self._write_field(Registers4671.OPENLOOP_ACCELERATION, 1000)
            c = self._dump_motion(n)
            self._write_field(Registers4671.OPENLOOP_VELOCITY_TARGET, 0)
            self._write_field(Registers4671.OPENLOOP_ACCELERATION, 0)
            self.printer.lookup_object("toolhead").dwell(0.2)
            self._write_field(Fields4671.MODE_MOTION, MotionMode.stopped_mode)
            self._write_field(Registers4671.PHI_E_SELECTION, old_phi_e_sel)
            self._write_field(Fields4671.PWM_CHOP, 0)
        for i in range(n):
            logging.info(",".join(map(str, c[i])))

    cmd_DUMP_TMC6100_help = "Read and display TMC6100 stepper driver registers"

    def cmd_DUMP_TMC6100(self, gcmd):
        logging.info("DUMP_TMC6100 %s", self.name)
        self.dump_tmc(
            gcmd, self.field_helper_6100, self.mcu_tmc6100, DUMP_GROUPS_6100
        )

    def dump_tmc(
        self,
        gcmd,
        field_helper: FieldHelper,
        mcu_tmc: MCU_TMC_SPI,
        dump_groups: dict[str, RegisterEnum],
    ):
        field_name = gcmd.get("FIELD", None)
        register_name = gcmd.get("REGISTER", None)
        name = field_name or register_name
        if name is not None:
            reg = field_helper.lookup_register_info(name.upper())
            if reg is None:
                raise gcmd.error(f"Unknown field/register name '{name}'")

            # readable register
            reg_val = mcu_tmc.get_register(reg)
            if reg.name != name:  # if we're dumping a field
                response = field_helper.pretty_format_field(name, reg, reg_val)
            else:
                response = field_helper.pretty_format(name, reg_val)
            gcmd.respond_info(response)
        else:
            group = gcmd.get("GROUP", "default").lower()
            if group not in dump_groups:
                raise gcmd.error(f"Unknown group name '{group}'")
            gcmd.respond_info("========== Queried registers ==========")
            for reg in dump_groups[group]:
                reg_val = mcu_tmc.get_register(reg)
                gcmd.respond_info(field_helper.pretty_format(reg, reg_val))

    cmd_DUMP_TMC_help = "Read and display TMC stepper driver registers"

    def cmd_DUMP_TMC(self, gcmd):
        logging.info("DUMP_TMC %s", self.name)
        self.dump_tmc(gcmd, self.field_helper, self.mcu_tmc, DUMP_GROUPS_4671)

    cmd_SET_TMC_FIELD_help = "Set a register field of a TMC driver"

    def cmd_SET_TMC_FIELD(self, gcmd):
        skip_parser = gcmd.get("SKIP_PARSER", False)

        field_name = gcmd.get("FIELD").upper()
        reg = self.field_helper.lookup_register_info(field_name)
        if reg is None:
            raise gcmd.error(f"Unknown field name '{field_name}'")

        value = gcmd.get_int("VALUE", None)
        if value is None:
            raise gcmd.error("Specify VALUE!")
        field = self.field_helper.lookup_field_info(field_name)

        if not skip_parser and field in FIELD_PARSERS:
            parser = FIELD_PARSERS[field]
            value = parser(value)
        with self.mutex:
            reg_val = self.field_helper.set_field(field_name, value)
            print_time = self.printer.lookup_object(
                "toolhead"
            ).get_last_move_time()
            self.mcu_tmc.set_register(reg, reg_val, print_time)

    cmd_SET_TMC_CURRENT_help = "Set the current of a TMC driver"

    def cmd_SET_TMC_CURRENT(self, gcmd):
        ch = self.current_helper
        prev_cur, max_cur = ch.get_current()
        run_current = gcmd.get_float(
            "CURRENT", None, minval=0.0, maxval=max_cur
        )
        if run_current is not None:
            ch.set_current(run_current)
            prev_cur, max_cur = ch.get_current()
        gcmd.respond_info("Run Current: %0.2fA" % (prev_cur,))


def load_config_prefix(config):
    return TMC4671(config)
