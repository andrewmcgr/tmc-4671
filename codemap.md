# Repository Atlas: tmc-4671

## Project Responsibility
Kalico 3D printer firmware plugin for Trinamic TMC 4671 FOC motor driver. Implements closed-loop PID control, encoder integration, temperature sensing, and self-calibrating motor characterization. Communicates over SPI with the TMC4671 chip (25 MHz external clock). Supports TMC6100 companion gate driver.

## System Entry Points
- `__init__.py` — Kalico plugin `load_config_prefix()` registration.
- `pyproject.toml` — Package manifest, entry-point registration.
- `install.sh` — Klipper `extras/` symlink installer.
- `README.md` — Hardware wiring, moonraker config, PID tuning guide.

## Directory Map
All modules reside in the repository root. Each Python module is documented below.

---

## Module Map

### `__init__.py`

**Responsibility**
Kalico plugin entry-point. Registers `tmc4671.load_config_prefix()` with the Kalico config loader.

**Design**
Minimal loader: imports the `tmc4671` module and exposes `load_config_prefix()` for Kalico.

**Flow**
1. Kalico loads plugin → calls `load_config_prefix(config)`.
2. Returns the `tmc4671` module for further resolution.

**Integration**
- Consumed by: Kalico plugin system.
- Depends on: `tmc4671.py` (exports `load_config_prefix`).

---

### `tmc4671.py`

**Responsibility**
Core driver implementation. Manages SPI communication with the TMC4671 chip, PID tuning, calibration (ADC, inductance, resistance), motion mode control, error monitoring, and G-code commands. Also provides the SPI helper classes (`MCU_TMC_SPI`, `MCU_TMC_SPI_simple`), field accessors (`FieldHelper`, `FieldProxy`, `SingleFieldAccessor`, `MultiFieldAccessor`), and the `CurrentHelper`, `TMCErrorCheck`, `TMCVirtualPinHelper`, and `StepHelper` integrations.

**Design Patterns**
- **Field accessor layer**: `FieldHelper` → `FieldProxy` → `SingleFieldAccessor` / `MultiFieldAccessor` — each level decouples register metadata from SPI transport. Uses `__getattr__` for ergonomic field attribute access.
- **Shadow register cache**: `FieldProxy._shadow` holds post-write register values so reads can avoid an extra SPI transfer.
- **SPI transaction guard**: per-instance `mutex` serializes all SPI bus access across the Klipper reactor thread.
- **Register map composition**: `Registers` + `Fields` + `SignedFields` + `FloatFields` + `FieldFormatters` are composed into the `FieldHelper`. 6100 companion has a separate `Registers6100` / `Fields6100`.
- **Biquad filter pipeline**: `BiquadFilter` dataclass → `biquad_Z_tmc` Z-transform → `biquad_tmc` normalization → register write.
- **Profile resolution**: `_resolve_profile()` looks up user-defined sections first, falls back to built-in profiles.

**Flow**
1. `TMC4671.__init__` — resolves motor/board profiles, applies `ConfigWithDefaults`, creates SPI helper, configures PWM frequency / MDEC, sets initial motion registers, registers PID/FF helpers, biquad filters, G-code commands, and event handlers.
2. `klippy:connect` event → `_handle_connect` — initializes all registers, calibrates ADC, aligns the motor, measures R/L via `_align_and_measure`, then applies optional current/motion PID tuning.
3. `klippy:mcu_identify` → `_handle_mcu_identify` — looks up stepper, sets pulse duration.
4. Motor enable/disable → `_handle_stepper_enable` — writes `MODE_MOTION` (position_mode / stopped_mode).
5. `TMCErrorCheck._do_periodic_check` runs every 1 s (via `reactor.register_timer`): queries `STATUS_FLAGS`, temperature, and current.
6. `TMCVirtualPinHelper` registers as a Klipper `pins` chip for sensorless homing.
7. Each G-code command dispatched to the corresponding handler method on the driver instance.

**Integration**
- Depends on: `tmc4671_regs.py` (register map), `tmc4671_biquad.py` (filter design), `tmc4671_profiles.py` (profile resolution).
- Consumed by: `__init__.py`, each per-stepper plugin section.
- Events: `klippy:connect`, `klippy:mcu_identify`, `klippy:disconnect`, `homing:homing_move_begin/end`, `homing:home_rails_begin`, `stepper_enable`.
- G-code: `SET_TMC_FIELD`, `DUMP_TMC`, `TMC_DEBUG_MOVE`, `TMC_TUNE_MOTION_PID`, `TMC_TUNE_PID`, `INIT_TMC`, `SET_TMC_CURRENT`, `SET_TMC_BIQUAD_FILTER`, `TMC_DEBUG_VOLTAGE`, `TMC_DEBUG_CURRENT`, `TMC_DEBUG_MOTOR`, `TMC_DEBUG_TUNING`, `TMC_MEASURE_IMPEDANCE`. 6100 companion adds `DUMP_TMC6100`.
- Klipper objects consulted: `pins`, `force_move`, `stepper_enable`, `configfile`, `gcode`, `toolhead`, `reactor`.

---

### `tmc4671_regs.py`

**Responsibility**
SPI register map for both TMC4671 and TMC6100. Each register entry is `(address, sub-address)`; each field entry maps field name → bitmask.

**Design Patterns**
- **Address-alias layer**: Sub-register fields are encoded as `(reg, addr)` pairs so the same SPI address can expose different fields via `REG+1` selector writes.
- **Mask-based fields**: Each field value is the LSB-positioned bitmask (e.g. `0xff << 8`), with `ffs(mask)` as the shift. `SignedFields` / `FloatFields` lists annotate which fields are signed or float-encoded.
- **Format functions**: `FieldFormatters` maps each register field to a formatter (`format_q4_12`, `format_phi`, etc.). Q-format I/O (`to_q4_12` ↔ `from_q4_12`, `to_q8_8` ↔ `from_q8_8`, `to_q2_30` ↔ `from_q2_30`) covers the chip's fixed-point conventions.

**Flow**
1. Imported by `tmc4671.py` → `Registers`, `Fields`, `SignedFields`, `FloatFields`, `FieldFormatters`, Q-format converters are composed into the `FieldHelper`.
2. `Registers6100` / `Fields6100` are composed into a separate `FieldHelper` when a 6100 companion is present.

**Integration**
- Consumed by: `tmc4671.py`.
- Standalone: no dependencies.

---

### `tmc4671_biquad.py`

**Responsibility**
Biquad filter design and normalization. Provides `BiquadFilter` dataclass and four filter design functions (`biquad_lpf`, `biquad_notch`, `biquad_apf`, plus TMC-specific `biquad_lpf_tmc`). Also Z-transforms and normalizes to TMC register format via `biquad_Z_tmc` / `biquad_tmc`.

**Design Patterns**
- **Tuned canonical filters**: each filter produces `(b0, b1, b2, a0, a1, a2)` in canonical form. TMC normalization divides by `a0` and scales by 2^29 for Q3.29 register representation.
- **Filter-target map**: `BIQUAD_FILTER_TARGETS` binds each filter target (flux/torque/velocity/position) to its enable register.

**Flow**
1. User config → `tmc4671.py` instantiates `BiquadFilter` per target.
2. `_apply_current_pid` / `_apply_motion_pid` redesign the filter for the chosen bandwidth, run `biquad_tmc` normalization, write registers via `enable_biquad`.

**Integration**
- Consumed by: `tmc4671.py`.
- Standalone: no dependencies.

---

### `tmc4671_profiles.py`

**Responsibility**
Profile infrastructure: `_MISSING` sentinel, `ConfigWithDefaults` wrapper that injects motor/board defaults, and `FocProfile` base class for `[foc_motor]` / `[tmc4671_board]` sections. Maintains `BUILTIN_MOTORS` and `BUILTIN_BOARDS` dicts.

**Design Patterns**
- **Wrapper with interception**: `ConfigWithDefaults` subclasses the Klipper `getfloat` / `getint` / `getboolean` / `getchoice` / `get` API, intercepting each call's `default` argument and replacing with the profile value. Falls through via `__getattr__` for any call not covered.
- **Prefix-stripping key lookup**: matches `foc_n_pole_pairs` → `n_pole_pairs` in profile; same for `drv_` prefix.
- **Profile precedence**: earlier (motor) dicts take priority; merge in reverse order so motor wins.

**Flow**
1. `tmc4671.py` builds `FocMotor` / `FocBoard` subclasses, validates each via `_validate()`, returns `get_values()`.
2. `_resolve_profile()` in `tmc4671.py` looks up a user-defined section first, then built-in DB.
3. When either lookup succeeds, the returned dict is wrapped by `ConfigWithDefaults`.

**Integration**
- Consumed by: `foc_motor.py`, `tmc4671_board.py`, `tmc4671.py` (profile resolver).
- Standalone: no external dependencies.

---

### `foc_motor.py`

**Responsibility**
`[foc_motor <name>]` config section. Captures motor-specific parameters: pole pairs, encoder geometry (ABN, Hall), Kt (direct or holding-current derived), rotor inertia, rated current.

**Design Patterns**
- **FocProfile subclass**: `ALLOWED` defines (key, type) pairs; all keys optional; `_validate()` derives `motor_kt` from the holding pair.
- **Validation**: rejects `holding_current` / `holding_torque` specified as only one, and rejects `motor_kt` overlap with the holding pair.

**Flow**
1. `load_config_prefix(config)` instantiates `FocMotor`, validates.
2. `tmc4671.py` calls `_resolve_profile(..., BUILTIN_MOTORS, 'foc_motor')` which registers as a printer object at `foc_motor <name>`.

**Integration**
- Depends on: `tmc4671_profiles.py`.
- Consumed by: `tmc4671.py` (profile resolver).

---

### `tmc4671_board.py`

**Responsibility**
`[tmc4671_board <name>]` config section. Captures board-specific parameters: voltage/current scaling, ADC channel assignments, PWM BBM, voltage limit, 6100 companion settings, AGPI thermistor beta coefficients, brake enable.

**Design Patterns**
- **FocProfile subclass**: same `ALLOWED` pattern as `foc_motor.py`. No validation.

**Flow**
1. `load_config_prefix(config)` instantiates `FocBoard`.
2. `tmc4671.py` calls `_resolve_profile(..., BUILTIN_BOARDS, 'tmc4671_board')` which registers as a printer object at `tmc4671_board <name>`.

**Integration**
- Depends on: `tmc4671_profiles.py`.
- Consumed by: `tmc4671.py` (profile resolver).

---

### `tmc4671_temperature_sensor.py`

**Responsibility**
`[tmc4671_temperature_sensor <stepper>]` config section. Integrates the TMC4671 AGPI thermistor as a Kalico heater manager sensor. Reports temperature for min/max tracking, registers the heater event.

**Design Patterns**
- **Klipper sensor adapter**: implements `get_temp`, `stats`, `get_status` as expected by the `heaters` plugin.
- **Two-object coupling**: each sensor must match a `[tmc4671 <stepper>]` section with `adc_temp_reg` configured — located via the `tmc4671_agpi <stepper>` name.

**Flow**
1. `load_config_prefix(config)` instantiates `TMC4671TemperatureSensor`, registers with `heaters` plugin.
2. `klippy:connect` → `_handle_connect` — looks up the matching `TMCErrorCheck` object, sets min/max, registers temperature callback.
3. Each temperature reading → `_temperature_callback` → updates last_temp, measured_min/max.
4. Heater consumers call `get_temp(eventtime)` for status output.

**Integration**
- Depends on: `tmc4671.py` (`TMCErrorCheck` provides the ADC reader and callback contract).
- Consumed by: Kalico `heaters` plugin.
