import math
from .helpers import MCU_TMC_SPI
from .register_bank import Registers4671, Fields4671, FieldEnum
from .register_bank import DUMP_GROUPS_4671, ADC_GPIO_FIELDS
import logging

######################################################################
# Periodic error checking
######################################################################


class TMCErrorCheck:
    def __init__(self, config, mcu_tmc: MCU_TMC_SPI):
        self.printer = config.get_printer()
        name_parts = config.get_name().split()
        self.stepper_name = " ".join(name_parts[1:])
        self.mcu_tmc = mcu_tmc
        self.field_helper = mcu_tmc.get_field_helper()
        self.check_timer = None
        self.status_warn_mask = self._make_mask(
            [
                Fields4671.PID_IQ_TARGET_LIMIT,
                Fields4671.PID_ID_TARGET_LIMIT,
                Fields4671.PID_V_OUTPUT_LIMIT,
                Fields4671.REF_SW_R,
                Fields4671.REF_SW_L,
            ]
        )
        # Useful for debugging
        # self.status_warn_mask = 0xffffffff
        self.status_error_mask = self._make_mask(
            [
                # Fields4671.PWM_MIN,
                # Fields4671.PWM_MAX,
                Fields4671.ADC_I_CLIPPED,
                Fields4671.AENC_CLIPPED,
            ]
        )
        self.last_status = 0
        self.monitor_data = {
            n: None
            for reg_name in DUMP_GROUPS_4671["monitor"]
            for n in self.field_helper.get_reg_fields(reg_name, 0)
        }
        # Setup for temperature query
        self.adc_temp = None
        self.adc_temp_reg = config.getchoice(
            "adc_temp_reg", ADC_GPIO_FIELDS, default=None
        )
        if self.adc_temp_reg is not None:
            pheaters = self.printer.load_object(config, "heaters")
            pheaters.register_monitor(config)

    def _make_mask(self, entries: list[FieldEnum]):
        mask = 0
        for f in entries:
            mask = self.field_helper.set_field(
                f, 1, mask, Registers4671.STATUS_FLAGS
            )
        return mask

    def _query_status(self):
        try:
            status = self.mcu_tmc.get_register(Registers4671.STATUS_FLAGS)
            fmt = self.field_helper.pretty_format(
                Registers4671.STATUS_FLAGS, status
            )
            # logging.info("TMC 4671 '%s' raw %s", self.stepper_name, fmt)
            if (
                status & self.status_warn_mask
                != self.last_status & self.status_warn_mask
            ):
                fmt = self.field_helper.pretty_format(
                    Registers4671.STATUS_FLAGS, status
                )
                logging.info("TMC 4671 '%s' reports %s", self.stepper_name, fmt)
            self.mcu_tmc.set_register_once(Registers4671.STATUS_FLAGS, 0)
            status = self.mcu_tmc.get_register(Registers4671.STATUS_FLAGS)
            self.last_status = status
            if status & self.status_error_mask:
                fmt = self.field_helper.pretty_format(
                    Registers4671.STATUS_FLAGS, status
                )
                raise self.printer.command_error(
                    "TMC 4671 '%s' reports error: %s" % (self.stepper_name, fmt)
                )
            # for reg_name in DumpGroups["MONITOR"]:
            #    val = self.mcu_tmc.get_register(reg_name)
            #    self.monitor_data.update(self.field_helper.get_reg_fields(reg_name, val))
            #    logging.info("TMC 4671 '%s' %s: %s", self.stepper_name,
            #                 reg_name, self.field_helper.pretty_format(reg_name, val))
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))
            return self.printer.get_reactor().NEVER

    def _query_temperature(self):
        try:
            if self.adc_temp_reg is not None:
                self.adc_temp = self.mcu_tmc.read_field(self.adc_temp_reg)
                # TODO: remove this, just temp logging
                # self._convert_temp(self.adc_temp)
        except self.printer.command_error as e:
            # Ignore comms error for temperature
            self.adc_temp = None
            return

    def _do_periodic_check(self, eventtime):
        try:
            self._query_status()
            self._query_temperature()
        except self.printer.command_error as e:
            self.printer.invoke_shutdown(str(e))
            return self.printer.get_reactor().NEVER
        return eventtime + 1.0

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
        self.check_timer = reactor.register_timer(
            self._do_periodic_check, curtime + 1.0
        )
        return True

    # Per the OpenFFBoard firmware source
    # [thermistor ffboard]
    # temperature1: 25
    # resistance1: 10000
    # beta: 4300
    def _convert_temp(self, adc):
        v = adc - 0x7FFF
        if v < 0:
            temp = 0.0
        else:
            # temp = 1500.0 * 43252.0 / float(v)
            temp = 64878000.0 / float(v)
            # temp = (1.0/298.15) + math.log(temp / 10000.0) / 4300.0
            temp = (0.003354016) + math.log(temp / 10000.0) / 4300.0
            temp = 1.0 / temp
            temp -= 273.15
        # logging.info("TMC %s temp: %g", self.stepper_name, temp)

    def get_status(self, eventtime=None):
        res = {"drv_status": None, "temperature": None}
        # res.update(self.monitor_data)
        if self.check_timer is None:
            return res
        temp = None
        if self.adc_temp is not None:
            # Convert it to temp here
            temp = self._convert_temp(self.adc_temp)
        res["temperature"] = temp
        return res
