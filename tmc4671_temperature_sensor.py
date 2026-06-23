# TMC4671 AGPI temperature sensor integration for Kalico/Klipper
#
# Copyright (C) 2024       Andrew McGregor <andrewmcgr@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# Usage: add a [tmc4671_temperature_sensor <stepper>] section to your config.
# The matching [tmc4671 <stepper>] section must have adc_temp_reg set.

KELVIN_TO_CELSIUS = -273.15


class TMC4671TemperatureSensor:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.min_temp = config.getfloat(
            "min_temp", KELVIN_TO_CELSIUS, minval=KELVIN_TO_CELSIUS
        )
        self.max_temp = config.getfloat(
            "max_temp", 99999999.9, above=self.min_temp
        )
        self.last_temp = 0.0
        self.measured_min = 99999999.0
        self.measured_max = 0.0
        pheaters = self.printer.load_object(config, "heaters")
        pheaters.register_sensor(config, self)
        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )

    def _handle_connect(self):
        obj_name = "tmc4671_agpi %s" % (self.name,)
        sensor = self.printer.lookup_object(obj_name, None)
        if sensor is None:
            raise self.printer.config_error(
                "tmc4671_temperature_sensor '%s': no matching [tmc4671 %s] "
                "section with adc_temp_reg configured" % (self.name, self.name)
            )
        sensor.setup_minmax(self.min_temp, self.max_temp)
        sensor.setup_callback(self._temperature_callback)

    def _temperature_callback(self, read_time, temp):
        self.last_temp = temp
        if temp:
            self.measured_min = min(self.measured_min, temp)
            self.measured_max = max(self.measured_max, temp)

    def get_temp(self, eventtime):
        return self.last_temp, 0.0

    def stats(self, eventtime):
        return False, "%s: temp=%.1f" % (self.name, self.last_temp)

    def get_status(self, eventtime):
        return {
            "temperature": round(self.last_temp, 2),
            "measured_min_temp": round(self.measured_min, 2),
            "measured_max_temp": round(self.measured_max, 2),
        }


def load_config_prefix(config):
    return TMC4671TemperatureSensor(config)
