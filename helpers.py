import logging
from collections import OrderedDict
from .register_bank import Fields4671, Registers4671, FieldEnum, RegisterEnum
from .utils import FormatUtils, BitUtils
from .. import bus

######################################################################
# Field manipulation helpers
######################################################################


# 4671 does not support chaining, so that's removed
# 4671 protocol does not require dummy reads
# default speed is 1 MHz, conservative for the device.
# would need timing control if going faster than 2 MHz.
class MCU_TMC_SPI_simple:
    def __init__(self, config, pin_option="cs_pin"):
        self.printer = config.get_printer()
        self.mutex = self.printer.get_reactor().mutex()
        self.spi = bus.MCU_SPI_from_config(
            config, 3, default_speed=1000000, pin_option=pin_option
        )

    def reg_read(self, reg):
        cmd = [reg, 0x00, 0x00, 0x00, 0x00]
        # self.spi.spi_send(cmd)
        with self.mutex:
            params = self.spi.spi_transfer(cmd)
        pr = bytearray(params["response"])
        return (pr[1] << 24) | (pr[2] << 16) | (pr[3] << 8) | pr[4]

    def reg_write(self, reg, val, print_time=None):
        minclock = 0
        if print_time is not None:
            minclock = self.spi.get_mcu().print_time_to_clock(print_time)
        data = [
            (reg | 0x80) & 0xFF,
            (val >> 24) & 0xFF,
            (val >> 16) & 0xFF,
            (val >> 8) & 0xFF,
            val & 0xFF,
        ]
        with self.mutex:
            self.spi.spi_send(data, minclock)
        return self.reg_read(reg)


# Helper code for working with TMC devices via SPI
# 4671 does have overlay registers, so support those
class MCU_TMC_SPI:
    def __init__(self, config, field_helper, tmc_frequency, pin_option):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.tmc_spi = MCU_TMC_SPI_simple(config, pin_option=pin_option)
        self.mutex = self.tmc_spi.mutex
        self.field_helper: FieldHelper = field_helper
        self.tmc_frequency = tmc_frequency

    def get_field_helper(self):
        return self.field_helper

    def get_register(self, reg):
        reg_enum = self.field_helper.lookup_register_info(reg)
        reg_addr = reg_enum.value.reg_addr
        sub_addr = reg_enum.value.sub_addr
        if sub_addr is not None:
            for retry in range(5):
                v = self.tmc_spi.reg_write(reg_addr + 1, sub_addr)
                if v == sub_addr:
                    break
            else:
                raise self.printer.command_error(
                    f"Unable to write tmc spi '{self.name}' address register {reg_enum.name} (last read {v})"
                )

        read = self.tmc_spi.reg_read(reg_addr)
        return read

    def set_register_once(self, reg, val, print_time=None):
        reg_enum = self.field_helper.lookup_register_info(reg)
        reg_addr = reg_enum.value.reg_addr
        sub_addr = reg_enum.value.sub_addr
        if sub_addr is not None:
            v = self.tmc_spi.reg_write(reg_addr + 1, sub_addr, print_time)
            if v != sub_addr:
                raise self.printer.command_error(
                    f"Unable to write tmc spi '{self.name}' address register {reg_enum.name} (last read {v})"
                )
        v = self.tmc_spi.reg_write(reg_addr, val, print_time)

    def set_register(self, reg, val, print_time=None):
        reg_enum = self.field_helper.lookup_register_info(reg)
        reg_addr = reg_enum.value.reg_addr
        sub_addr = reg_enum.value.sub_addr
        if sub_addr is not None:
            for retry in range(5):
                v = self.tmc_spi.reg_write(reg_addr + 1, sub_addr, print_time)
                if v == sub_addr:
                    break
            else:
                raise self.printer.command_error(
                    f"Unable to write tmc spi '{self.name}' address register {reg_enum.name} (last read {v})"
                )
        for retry in range(5):
            v = self.tmc_spi.reg_write(reg_addr, val, print_time)
            if v == val:
                return
        raise self.printer.command_error(
            f"Unable to write tmc spi '{self.name}' register {reg_enum.name} (last read {v})"
        )

    def raw_reg_read(self, reg_addr: int):
        return self.tmc_spi.reg_read(reg_addr)

    def get_tmc_frequency(self):
        return self.tmc_frequency

    def read_field(self, field):
        reg = self.field_helper.lookup_register_info(field)
        reg_value = self.get_register(reg)
        return self.field_helper.get_field(field, reg_value=reg_value, reg=reg)

    def write_field(self, field_name, val):
        reg = self.field_helper.lookup_register_info(field_name)
        reg_value = self.get_register(reg)
        self.set_register(
            reg,
            self.field_helper.set_field(
                field_name, val, reg_value=reg_value, reg=reg
            ),
        )

    def write_register_cache(self, print_time):
        for reg in list(self.field_helper.register_cache.keys()):
            if reg == Registers4671.STATUS_FLAGS:
                continue
            val = self.field_helper.register_cache[
                reg
            ]  # Val may change during loop
            self.set_register(reg, val, print_time)


class PIDHelper:
    def __init__(
        self,
        config,
        mcu_tmc: MCU_TMC_SPI,
        field: FieldEnum,
        field_val_def: float,
        n_field: FieldEnum,
        n_val_def: int,
    ):
        self.mcu_tmc = mcu_tmc
        self.field_helper = mcu_tmc.get_field_helper()
        field_name = field.name
        n_field_name = n_field.name
        logging.info(
            f'TMC: {",".join((str(i) for i in [field.name, field_val_def, n_field.name, n_val_def]))}'
        )
        n_val = self.field_helper.set_config_field(config, n_field, n_val_def)

        if n_val:
            self.to_f = FormatUtils.to_q4_12
            self.from_f = FormatUtils.from_q4_12
        else:
            self.to_f = FormatUtils.to_q8_8
            self.from_f = FormatUtils.from_q8_8

        self.field_helper.set_formatter(field, self.from_f)
        self.field_helper.set_parser(n_field, self.to_f)

        self.field_helper.set_config_field(
            config, field, self.to_f(field_val_def)
        )
        self.field = field

    def write_coefficient(self, value):
        self.mcu_tmc.write_field(self.field, self.to_f(value))


class FieldHelper:
    def __init__(
        self,
        field_enum: FieldEnum,
        register_enum: RegisterEnum,
        printer,
        signed_fields=[],
        field_formatters={},
        prefix="driver_",
    ):
        self.field_enum = field_enum
        self.register_enum = register_enum
        self.register_cache: OrderedDict[RegisterEnum, int] = OrderedDict()
        self.printer = printer
        self.reg_to_field: dict[RegisterEnum, list[FieldEnum]] = {
            reg: [
                field
                for field in field_enum.members()
                if field.value.register == reg
            ]
            for reg in register_enum.members()
        }
        # self.all_fields = all_fields
        # self.signed_fields = {sf: 1 for sf in signed_fields}
        # self.field_formatters = field_formatters
        # self.field_to_register = {
        #     f: r for r, fields in self.all_fields.items() for f in fields
        # }
        self.prefix = prefix
        self.cached_formatters = {}
        self.cached_parsers = {}

    @property
    def parsers(self):
        # merge parsers with cached parsers
        return {**FIELD_PARSERS, **self.cached_parsers}

    @property
    def formatters(self):
        # merge formatters with cached formatters
        return {**FIELD_FORMATTERS, **self.cached_formatters}

    def set_formatter(self, field, formatter):
        self.cached_formatters[field] = formatter

    def set_parser(self, field, parser):
        self.cached_parsers[field] = parser

    def name_is_register(self, name):
        return name in self.register_enum.member_names()

    def name_is_field(self, name):
        return name in self.field_enum.member_names()

    def lookup_fields_for_reg(self, reg) -> list[FieldEnum]:
        return self.reg_to_field.get(reg, [])

    def lookup_register_name(self, field_or_reg):
        name = self.resolve_reg_or_field_name(field_or_reg)
        if self.name_is_register(name):
            return name
        field = self.field_enum.get(name)
        if field is not None:
            return field.value.register.name
        return None

    def lookup_register_info(self, field_or_reg, default=None) -> RegisterEnum:
        name = self.resolve_reg_or_field_name(field_or_reg)
        if self.name_is_register(name):
            # name is a register, return it
            return self.register_enum.get(name)
        # name is a field, return its register
        field = self.field_enum.get(name, default)
        if field is not None:
            return field.value.register
        return None

    def lookup_field_info(
        self, field, default=None, error_on_missing=True
    ) -> FieldEnum:
        name = self.resolve_reg_or_field_name(field)
        field = self.field_enum.get(name, default)
        if field is None and error_on_missing:
            raise self.printer.command_error(f"Invalid field name: {name}")
        return field

    def get_field(self, field, reg_value=None, reg=None):
        field_name = self.resolve_reg_or_field_name(field)
        reg_name = self.resolve_reg_or_field_name(reg)
        # Returns value of the register field
        if reg_name is None:
            register = self.lookup_register_info(field_name)
            reg_name = register.name
        else:
            register = self.lookup_register_info(reg_name)

        if reg_value is None:
            if reg_name not in self.register_cache:
                logging.info(f"no value for {reg_name} in cache, using 0...")
                reg_value = 0
            else:
                reg_value = self.register_cache.get(reg_name)

        if self.name_is_register(field_name):
            mask = 0xFFFFFFFF
            signed = register.value.signed
        else:
            field = self.lookup_field_info(field_name).value
            mask = field.mask
            signed = field.signed

        field_value = (reg_value & mask) >> BitUtils.ffs(mask)

        if signed and ((reg_value & mask) << 1) > mask:
            field_value -= 1 << field_value.bit_length()
        return field_value

    def set_field(self, field, field_value, reg_value=None, reg=None):
        if reg is None:
            reg = self.lookup_register_info(field)
        else:
            # reg can be a register or a str, so make sure we have a register
            reg = self.lookup_register_info(reg)
        # Returns register value with field bits filled with supplied value
        if reg_value is None:
            if reg not in self.register_cache:
                logging.info(f"no value for {reg} in cache, using 0...")
                reg_value = 0
            else:
                reg_value = self.register_cache.get(reg)

        if self.name_is_register(field):
            mask = 0xFFFFFFFF
        else:
            mask = self.lookup_field_info(field).value.mask

        new_value = (reg_value & ~mask) | (
            (field_value << BitUtils.ffs(mask)) & mask
        )
        self.register_cache[reg] = new_value
        return new_value

    def set_config_field(self, config, field, default):
        field_name = self.resolve_reg_or_field_name(field)
        # Allow a field to be set from the config file
        config_name = self.prefix + field_name
        register = self.lookup_register_info(field_name)
        if register is None:
            raise self.printer.config_error(
                f"invalid field name: '{field_name}'"
            )
        reg_name = register.name
        if self.name_is_register(field_name):
            mask = 0xFFFFFFFF
            signed = register.value.signed
            parser = FIELD_PARSERS.get(register)
        else:
            field = self.lookup_field_info(field_name).value
            mask = field.mask
            signed = field.signed
            parser = FIELD_PARSERS.get(field)

        maxval = mask >> BitUtils.ffs(mask)
        if maxval == 1:
            val = config.getboolean(config_name, default)
        elif signed:
            config_maxval = maxval // 2
            config_minval = -(config_maxval + 1)
            val = config.getfloat(
                config_name,
                float(default),
                minval=config_minval,
                maxval=config_maxval,
            )
        else:
            val = config.getfloat(
                config_name, float(default), minval=0, maxval=maxval
            )

        if isinstance(val, float):
            if parser is not None:
                val = parser(val)
            else:
                val = int(val)

        return self.set_field(field_name, val, reg_name=reg_name)

    def pretty_format(self, reg: RegisterEnum, reg_value):
        # Provide a string description of a register
        field_val_ = self.get_reg_fields(reg, reg_value)

        fields = []
        for field_name, field_val in field_val_.items():
            formatter_func = self.formatters.get(field_name, str)
            sval = formatter_func(field_val)
            if sval and sval != "0":
                fields.append(" %s=%s" % (field_name.lower(), sval))
        return "%-11s %08x%s" % (reg.name + ":", reg_value, "".join(fields))

    def pretty_format_field(
        self, field, reg_val=None, reg: RegisterEnum = None
    ):
        field = self.lookup_field_info(field)
        # Provide a string description of a field
        field_val = self.get_field(field, reg_value=reg_val, reg=reg)
        formatter_func = self.formatters.get(field, str)
        formatted_val = formatter_func(field_val)
        return "%-11s %s" % (
            reg.name + " -- " + field.name + ":",
            formatted_val,
        )

    def get_reg_fields(self, reg, reg_value) -> dict[str, FieldEnum]:
        reg_name = self.resolve_reg_or_field_name(reg)
        # Provide fields (values) found in a register
        reg_fields = self.lookup_fields_for_reg(reg)
        return {
            field.name: self.get_field(field.name, reg_value, reg_name)
            for field in reg_fields
        }

    def resolve_reg_or_field_name(self, item) -> str | None:
        if item is None:
            return None
        if isinstance(item, RegisterEnum):
            return item.name
        if isinstance(item, FieldEnum):
            return item.value.register.name
        return item


######################################################################
# Current control
######################################################################

MAX_CURRENT = 10.000


class CurrentHelper:
    def __init__(self, config, mcu_tmc: MCU_TMC_SPI):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.mcu_tmc = mcu_tmc
        self.field_helper = mcu_tmc.get_field_helper()
        self.run_current = config.getfloat(
            "run_current", above=0.0, maxval=MAX_CURRENT
        )
        self.homing_current = config.getfloat(
            "homing_current",
            above=0.0,
            maxval=MAX_CURRENT,
            default=self.run_current,
        )
        self.flux_current = config.getfloat(
            "flux_current", above=0.0, maxval=MAX_CURRENT, default=0.0
        )
        self.current_scale = config.getfloat(
            "current_scale_ma_lsb", 1.272, above=0.0, maxval=10
        )
        self.flux_limit = self._calc_flux_limit(self.run_current)
        self.field_helper.set_field(
            Registers4671.PID_TORQUE_FLUX_LIMITS, self.flux_limit
        )
        self.flux_limit = self._calc_flux_limit(self.flux_current)
        self.field_helper.set_field(Fields4671.PID_FLUX_OFFSET, self.flux_limit)

    def _calc_flux_limit(self, current):
        flux_limit = round(current * 1e3 / self.current_scale)
        return flux_limit

    def set_flux_current(self, current):
        self.flux_current = current
        self.flux_limit = self._calc_flux_limit(self.flux_current)
        self._write_field(Fields4671.PID_FLUX_OFFSET, self.flux_limit)
        return self.flux_limit

    def convert_adc_current(self, adc):
        return adc * self.current_scale * 1e-3

    def get_run_current(self):
        return self.run_current

    def get_homing_current(self):
        return self.homing_current

    def get_current(self):
        c = self.convert_adc_current(
            self._read_field(Registers4671.PID_TORQUE_FLUX_LIMITS)
        )
        iux = self.convert_adc_current(self._read_field(Fields4671.ADC_IUX))
        iv = self.convert_adc_current(self._read_field(Fields4671.ADC_IV))
        iwy = self.convert_adc_current(self._read_field(Fields4671.ADC_IWY))
        return c, MAX_CURRENT, iux, iv, iwy

    def set_current(self, run_current):
        self.run_current = run_current
        self.flux_limit = self._calc_flux_limit(self.run_current)
        self._write_field(Registers4671.PID_TORQUE_FLUX_LIMITS, self.flux_limit)
        return self.flux_limit

    def _read_field(self, field_name):
        return self.mcu_tmc.read_field(field_name)

    def _write_field(self, field_name, val):
        return self.mcu_tmc.write_field(field_name, val)


######################################################################
# Helper class for "sensorless homing"
######################################################################


class TMCVirtualPinHelper:
    def __init__(
        self, config, mcu_tmc: MCU_TMC_SPI, current_helper: CurrentHelper
    ):
        self.printer = config.get_printer()
        self.mcu_tmc = mcu_tmc
        self.field_helper = mcu_tmc.get_field_helper()
        self.current_helper = current_helper
        self.diag_pin = config.get("diag_pin", None)
        self.mcu_endstop = None
        self.en_pwm = False
        # Stalls show up as either IQ_ERRSUM or V_OUTPUT.
        # Include the reference switches so can connect endstops
        # to driver boards.
        self.status_mask_entries = config.getlist(
            "homing_mask",
            [
                Fields4671.PID_IQ_OUTPUT_LIMIT.name,
                Fields4671.PID_ID_OUTPUT_LIMIT.name,
                # Fields4671.PID_IQ_ERRSUM_LIMIT.name,
                # Fields4671.PID_ID_ERRSUM_LIMIT.name,
                # Fields4671.PID_IQ_TARGET_LIMIT.name,
                Fields4671.PID_ID_TARGET_LIMIT.name,
                # Fields4671.PID_X_OUTPUT_LIMIT.name,
                Fields4671.PID_V_OUTPUT_LIMIT.name,
                Fields4671.REF_SW_R.name,
                Fields4671.REF_SW_L.name,
            ],
        )
        self.status_mask = 0
        for f in self.status_mask_entries:
            self.status_mask = self.field_helper.set_field(
                f, 1, self.status_mask, Registers4671.STATUS_FLAGS
            )
        # Register virtual_endstop pin
        name_parts = config.get_name().split()
        self.name = "_".join(name_parts)
        logging.info(
            "TMC virtual endstop %s, mask is %x", self.name, self.status_mask
        )
        ppins = self.printer.lookup_object("pins")
        ppins.register_chip("%s" % (self.name), self)

    def setup_pin(self, pin_type, pin_params):
        # Validate pin
        ppins = self.printer.lookup_object("pins")
        if pin_type != "endstop" or pin_params["pin"] != "virtual_endstop":
            raise ppins.error("tmc virtual endstop only useful as endstop")
        if pin_params["invert"] or pin_params["pullup"]:
            raise ppins.error("Can not pullup/invert tmc virtual pin")
        if self.diag_pin is None:
            raise ppins.error("tmc virtual endstop requires diag pin config")
        # Setup for sensorless homing
        self.printer.register_event_handler(
            "homing:homing_move_begin", self.handle_homing_move_begin
        )
        self.printer.register_event_handler(
            "homing:homing_move_end", self.handle_homing_move_end
        )
        self.mcu_endstop = ppins.setup_pin("endstop", self.diag_pin)
        return self.mcu_endstop

    def handle_homing_move_begin(self, hmove):
        if self.mcu_endstop not in hmove.get_mcu_endstops():
            return
        # self.mcu_tmc.write_field("PID_VELOCITY_LIMIT", 3000)
        self.current_helper.set_current(
            self.current_helper.get_homing_current()
        )
        self.mcu_tmc.set_register_once(Registers4671.STATUS_FLAGS, 0)
        self.printer.lookup_object("toolhead").dwell(0.005)
        self.mcu_tmc.set_register_once(Registers4671.STATUS_FLAGS, 0)
        self.mcu_tmc.write_field(Registers4671.STATUS_MASK, self.status_mask)
        status = self.mcu_tmc.get_register(Registers4671.STATUS_FLAGS)
        fmt = self.field_helper.pretty_format(
            Registers4671.STATUS_FLAGS, status
        )
        logging.info("TMC 4671 '%s' status at homing start %s", self.name, fmt)

    def handle_homing_move_end(self, hmove):
        status = self.mcu_tmc.get_register(Registers4671.STATUS_FLAGS)
        fmt = self.field_helper.pretty_format(
            Registers4671.STATUS_FLAGS, status
        )
        logging.info("TMC 4671 '%s' status at homing end %s", self.name, fmt)
        if self.mcu_endstop not in hmove.get_mcu_endstops():
            return
        # self.mcu_tmc.write_field("PID_VELOCITY_LIMIT", 0x300000)
        self.mcu_tmc.set_register_once(Registers4671.STATUS_FLAGS, 0)
        self.current_helper.set_current(self.current_helper.get_run_current())
        self.mcu_tmc.write_field(Registers4671.STATUS_MASK, 0)
        self.mcu_tmc.set_register_once(Registers4671.STATUS_FLAGS, 0)


######################################################################
# Helper to configure the microstep settings
######################################################################


def StepHelper(config, mcu_tmc: MCU_TMC_SPI):
    field_helper = mcu_tmc.get_field_helper()
    stepper_name = " ".join(config.get_name().split()[1:])
    if not config.has_section(stepper_name):
        raise config.error(
            "Could not find config section '[%s]' required by tmc4671 driver"
            % (stepper_name,)
        )
    sconfig = config.getsection(stepper_name)
    steps = {1 << i: 1 << i for i in range(0, 16)}
    res = sconfig.getchoice("full_steps_per_rotation", steps, default=8)
    mres = sconfig.getchoice("microsteps", steps, default=256)
    if res * mres > 65536:
        raise config.error(
            "Product of res and mres must not be more than 65536 for [%s]"
            % (stepper_name,)
        )
    step_width = 65536 // (res * mres)
    field_helper.set_field("STEP_WIDTH", step_width)


# parsers must return an integer
FIELD_PARSERS = {
    Fields4671.PID_FLUX_P: FormatUtils.to_q4_12,
    Fields4671.PID_FLUX_I: FormatUtils.to_q4_12,
    Fields4671.PID_TORQUE_P: FormatUtils.to_q4_12,
    Fields4671.PID_TORQUE_I: FormatUtils.to_q4_12,
    Fields4671.PID_VELOCITY_P: FormatUtils.to_q8_8,
    Fields4671.PID_VELOCITY_I: FormatUtils.to_q4_12,
    Fields4671.PID_POSITION_P: FormatUtils.to_q8_8,
    Fields4671.PID_POSITION_I: FormatUtils.to_q4_12,
}
FIELD_FORMATTERS = {
    Registers4671.CONFIG_BIQUAD_X_A_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_X_A_2: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_X_B_0: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_X_B_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_X_B_2: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_V_A_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_V_A_2: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_V_B_0: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_V_B_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_V_B_2: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_T_A_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_T_A_2: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_T_B_0: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_T_B_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_T_B_2: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_F_A_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_F_A_2: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_F_B_0: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_F_B_1: FormatUtils.format_q3_29,
    Registers4671.CONFIG_BIQUAD_F_B_2: FormatUtils.format_q3_29,
    Registers4671.HALL_PHI_E_PHI_M_OFFSET: FormatUtils.format_phi,
    Registers4671.HALL_PHI_M: FormatUtils.format_phi,
    Registers4671.PHI_E: FormatUtils.format_phi,
    Fields4671.HALL_POSITION_000: FormatUtils.format_phi,
    Fields4671.HALL_POSITION_120: FormatUtils.format_phi,
    Fields4671.HALL_POSITION_240: FormatUtils.format_phi,
    Fields4671.HALL_POSITION_060: FormatUtils.format_phi,
    Fields4671.HALL_POSITION_180: FormatUtils.format_phi,
    Fields4671.HALL_POSITION_300: FormatUtils.format_phi,
    Fields4671.HALL_PHI_E: FormatUtils.format_phi,
    Fields4671.HALL_PHI_E_INTERPOLATED: FormatUtils.format_phi,
    Fields4671.HALL_PHI_E_OFFSET: FormatUtils.format_phi,
    Fields4671.HALL_PHI_M_OFFSET: FormatUtils.format_phi,
    Fields4671.ABN_DECODER_PHI_M: FormatUtils.format_phi,
    Fields4671.ABN_DECODER_PHI_E: FormatUtils.format_phi,
    Fields4671.ABN_DECODER_PHI_E_OFFSET: FormatUtils.format_phi,
    Fields4671.ABN_DECODER_PHI_M_OFFSET: FormatUtils.format_phi,
    Fields4671.PID_FLUX_P: FormatUtils.format_q4_12,
    Fields4671.PID_FLUX_I: FormatUtils.format_q4_12,
    Fields4671.PID_TORQUE_P: FormatUtils.format_q4_12,
    Fields4671.PID_TORQUE_I: FormatUtils.format_q4_12,
    Fields4671.PID_VELOCITY_P: FormatUtils.format_q8_8,
    Fields4671.PID_VELOCITY_I: FormatUtils.format_q4_12,
    Fields4671.PID_POSITION_P: FormatUtils.format_q8_8,
    Fields4671.PID_POSITION_I: FormatUtils.format_q4_12,
}
