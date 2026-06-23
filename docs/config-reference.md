# TMC4671 Configuration Reference

All config entries for `[tmc4671 <stepper>]` sections, plus the
`[foc_motor <name>]` and `[tmc4671_board <name>]` profile sections.

Entries are grouped by what "owns" the knowledge:
- **[Motor](#motor-specific)** — properties of the motor itself (from the datasheet or measurement)
- **[Board](#board-specific)** — properties of the TMC4671 driver board (analog front-end, gate driver)
- **[Instance](#instance-specific)** — properties of the specific installation (wiring, tuning, load)

---

## Motor-specific

These entries describe the motor's physical and electrical properties. Candidates
for `[foc_motor <name>]`.

### Pole pairs and feedback source

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `n_pole_pairs` | int | `4` | — | Number of electrical pole pairs. |
| `phi_e_selection` | int | `3` | — | Electrical angle source. `3` = ABN encoder, `5` = Hall. |

### Torque constant

Specify either `motor_kt` directly, or both `holding_current` and `holding_torque`
to derive it automatically.

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `motor_kt` | float | `0.0156` | N·m/A | Motor torque constant Kt. |
| `holding_current` | float | — | A (peak) | Holding current from datasheet. Both this and `holding_torque` must be provided together. |
| `holding_torque` | float | — | N·m | Holding torque from datasheet. Both this and `holding_current` must be provided together. When both are given, `motor_kt = holding_torque / holding_current`. |

### Inertia

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `jmotor` | float | `8.45e-6` | kg·m² | Rotor moment of inertia. |

### ABN incremental encoder

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `abn_decoder_ppr` | int | `4000` | counts/rev | Encoder pulses per revolution. |
| `abn_direction` | int | `0` | — | Invert encoder direction. `0` = normal, `1` = inverted. |
| `abn_apol` | int | `0` | — | A-channel polarity. `0` = active high, `1` = active low. |
| `abn_bpol` | int | `0` | — | B-channel polarity. |
| `abn_npol` | int | `0` | — | N (index) channel polarity. |
| `abn_use_abn_as_n` | int | `0` | — | Use ABN signal as index. |
| `abn_cln` | int | `0` | — | Clear position on N pulse. |

### AENC absolute encoder

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `aenc_deg` | int | `0` | degrees | AENC alignment offset in degrees. |
| `aenc_ppr` | int | `0` | counts/rev | AENC pulses per revolution. |

### Hall sensor

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `hall_interp` | int | `0` | — | Hall interpolation enable. |
| `hall_sync` | int | `1` | — | Hall sync enable. |
| `hall_polarity` | int | `0` | — | Hall sensor polarity. |
| `hall_dir` | int | `0` | — | Hall direction inversion. |
| `hall_dphi_max` | int | `0xAAAA` | — | Maximum Hall phase difference. |
| `hall_phi_e_offset` | int | `0` | — | Hall electrical angle offset. |
| `hall_blank` | int | `2` | — | Hall blanking time. |

### Motor type

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `motor_type` | int | `2` | — | Motor winding type. `2` = two-phase stepper, `3` = three-phase BLDC. |

---

## Board-specific

These entries describe the TMC4671 driver board's analog front-end, gate driver, and
ADC channel routing. Candidates for `[tmc4671_board <name>]`.

### Power and voltage measurement

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `voltage_scale_ratio` | float | `40.875` | counts/V | ADC counts per volt on the VM sense input. Default matches the OpenFFBoard resistor divider. |

### Current sensing

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `current_scale_ma_lsb` | float | `1.272` | mA/LSB | Milliamps per ADC LSB. Depends on shunt resistor value and current sense amplifier gain. Default matches the OpenFFBoard. |

### ADC channel routing

The TMC4671 has two ADC inputs (I0, I1) that are multiplexed to the UX/V/WY current
sense channels. These must match the board's PCB routing.

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `adc_i_ux_select` | int | `0` | — | ADC channel for phase U/X current. |
| `adc_i_v_select` | int | `2` | — | ADC channel for phase V current. |
| `adc_i_wy_select` | int | `1` | — | ADC channel for phase W/Y current. |
| `adc_i0_select` | int | `0` | — | ADC I0 input selection. |
| `adc_i1_select` | int | `1` | — | ADC I1 input selection. |

### PWM and gate driver

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `pwm_freq_target` | float | `142857` | Hz | Target PWM switching frequency. Actual frequency is rounded to the nearest achievable value from the 25 MHz TMC clock. Range: 10 kHz – 150 kHz. |
| `pwm_bbm_l` | int | `10` | counts | Bottom-side gate driver dead time (break-before-make). |
| `pwm_bbm_h` | int | `10` | counts | Top-side gate driver dead time. |
| `pidout_uq_ud_limits` | int | `29000` | 1/32768 Vm | Maximum output voltage from the current controllers. `32768` = 100% Vm. Also acts as anti-windup. |

### TMC6100 gate driver (optional)

Present only when `drv_cs_pin` is configured. These fields follow the TMC6100
register naming convention.

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `singleline` | int | `0` | — | Single-shunt mode. |
| `normal` | int | `1` | — | Normal mode select. |
| `drvstrength` | int | `0` | — | Gate driver strength. |
| `bbmclks` | int | `10` | clocks | Break-before-make clock cycles. |

### AGPI temperature sensing

All temperature-sensing parameters live here. In practice the thermistors used measure
driver board output-stage temperatures (not motor winding temperatures), so this
configuration belongs entirely to the board profile.

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `adc_temp_reg` | choice | — | — | AGPI pin used for temperature sensing: `AGPI_A` or `AGPI_B`. Omit to disable. |
| `adc_temp_pullup_resistor` | float | `1500.0` | Ω | Pulldown resistor in the AGPI voltage divider (R_low). Default matches the OpenFFBoard. |
| `adc_temp_t1` | float | `25.0` | °C | Thermistor reference temperature. |
| `adc_temp_r1` | float | `10000.0` | Ω | Thermistor resistance at `adc_temp_t1`. |
| `adc_temp_beta` | float | `4300.0` | K | Thermistor beta coefficient. |

---

## Instance-specific

These entries are specific to a particular `[tmc4671 <stepper>]` installation and
cannot generally be shared across motors or boards.

### Profile references

`[foc_motor]` and `[tmc4671_board]` sections must appear **before** any `[tmc4671]`
section in `printer.cfg` that references them.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `motor_profile` | string | — | Name of a `[foc_motor]` section to inherit motor defaults from. |
| `board_profile` | string | — | Name of a `[tmc4671_board]` section to inherit board defaults from. |

### Hardware pins

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `cs_pin` | pin | **required** | SPI chip-select pin for the TMC4671. |
| `drv_cs_pin` | pin | — | SPI chip-select for the TMC6100 gate driver. Omit if not present. |
| `spi_speed` | int | `1000000` | SPI clock speed in Hz. |
| `spi_bus` | string | — | SPI bus identifier. |
| `spi_software_mosi_pin` | pin | — | Software SPI MOSI pin. |
| `spi_software_miso_pin` | pin | — | Software SPI MISO pin. |
| `spi_software_sclk_pin` | pin | — | Software SPI SCLK pin. |
| `diag_pin` | pin | — | MCU GPIO connected to the TMC4671 DIAG output for sensorless homing. |

### Current

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `run_current` | float | **required** | A | Motor current during motion. |
| `homing_current` | float | `run_current` | A | Motor current during homing moves. |
| `flux_current` | float | `0.0` | A | Field-weakening (D-axis) flux current. |

### Load dynamics

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `jload` | float | `5e-5` | kg·m² | Load moment of inertia reflected to the motor shaft. Overridden if `load_mass` is given. |
| `load_mass` | float | — | kg | Mass of a linear load. When given, `jload` is computed as `mass × (pitch_m / 2π)²` where `pitch_m = rotation_distance / (1000 × gear_ratio)`. |

### Feedback source selection

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `position_selection` | int | `9` | — | Position feedback source. `9` = phi\_m\_abn (mechanical, ABN encoder). `0`–`8` = electrical angle sources. |
| `velocity_selection` | int | `3` | — | Velocity feedback source. `3` = phi\_e\_abn (electrical). `9`–`12` = mechanical sources. |
| `velocity_meter_selection` | int | `1` | — | Velocity measurement method. `0` = delta-sigma, `1` = PWM frequency meter. |
| `mode_pid_smpl` | int | `0` | — | PID position sampling. `0` = sample at PWM frequency. |
| `mode_pid_type` | int | `1` | — | PID algorithm. `1` = advanced PI. |

### PID autotuning

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `tune_current_pid` | bool | `False` | — | Auto-compute flux/torque PID gains at startup using motor electrical parameters. Requires `_align_and_measure` to succeed. |
| `tune_motion_pid` | bool | `False` | — | Auto-compute velocity/position PID gains at startup using inertia and bandwidth targets. |
| `current_bandwidth` | float | `1200.0` | Hz | Target bandwidth for flux and torque current loops. Used as default for `flux_bandwidth` and `torque_bandwidth`. |
| `flux_bandwidth` | float | `current_bandwidth` | Hz | Flux (D-axis) current loop bandwidth. |
| `torque_bandwidth` | float | `current_bandwidth` | Hz | Torque (Q-axis) current loop bandwidth. |
| `velocity_bandwidth` | float | `450.0` | Hz | Velocity loop bandwidth. |
| `position_bandwidth` | float | `100.0` | Hz | Position loop bandwidth. |
| `velocity_alpha` | float | `0.35` | — | Velocity low-pass filter coefficient (0 = no filtering, 1 = maximum). |

### PID gains

These can be written by `TMC_TUNE_PID` / `TMC_TUNE_MOTION_PID` and saved via `SAVE_CONFIG`.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `flux_p` | float | `9.4` | Flux (D-axis) proportional gain. |
| `flux_i` | float | `0.087` | Flux integral gain. |
| `current_p_n` | int | `0` | Flux P gain normalisation shift. |
| `current_i_n` | int | `1` | Flux I gain normalisation shift. |
| `torque_p` | float | `9.4` | Torque (Q-axis) proportional gain. |
| `torque_i` | float | `0.087` | Torque integral gain. |
| `velocity_p` | float | `4.5` | Velocity proportional gain. |
| `velocity_i` | float | `0.0` | Velocity integral gain. |
| `velocity_p_n` | int | `0` | Velocity P gain normalisation shift. |
| `velocity_i_n` | int | `1` | Velocity I gain normalisation shift. |
| `position_p` | float | `2.5` | Position proportional gain. |
| `position_i` | float | `0.0` | Position integral gain. |
| `position_p_n` | int | `0` | Position P gain normalisation shift. |
| `position_i_n` | int | `1` | Position I gain normalisation shift. |

### Feed-forward

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mode_ff` | int | `0` | Feed-forward mode. `0` = disabled. |
| `feed_forward_velocity_gain` | float | `0.0` | Velocity feed-forward gain. |
| `feed_forward_velocity_filter_constant` | float | `0.0` | Velocity feed-forward filter constant. |
| `feed_forward_torque_gain` | float | `0.0` | Torque feed-forward gain. |
| `feed_forward_torque_filter_constant` | float | `0.0` | Torque feed-forward filter constant. |

### Biquad filters

Four independent second-order filters — one per control loop. Targets: `flux`, `torque`,
`velocity`, `position`.

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `biquad_{target}_filter` | choice | `lpf` | — | Filter type: `lpf` (low-pass), `notch`, `apf` (all-pass). |
| `biquad_{target}_frequency` | float | **required** | Hz | Cutoff or center frequency. Required unless `tune_current_pid` (for flux/torque) or `tune_motion_pid` (for velocity) is `True`, in which case it defaults to `0` (disabled). |
| `biquad_{target}_slope` | float | `0.707` | — | Q factor / slope (√½ for Butterworth response). |

### Position and velocity limits

| Key | Type | Default | Unit | Description |
|-----|------|---------|------|-------------|
| `pid_position_limit_low` | int | `-268435456` | counts | Lower position limit. |
| `pid_position_limit_high` | int | `268435456` | counts | Upper position limit. |
| `pid_velocity_limit` | int | `268435456` | RPM | Velocity magnitude limit. |

---

## Design notes — profile inheritance

### `[foc_motor <name>]` example

```ini
[foc_motor LDO_2504b-EN1000]
motor_type: 2
n_pole_pairs: 50
holding_current: 1.0
holding_torque: 0.165
jmotor: 7.6e-7
abn_decoder_ppr: 1000
```

### `[tmc4671_board OpenFFBoard]` example

The `OpenFFBoard` board profile is also available as a built-in — you can write
`board_profile: OpenFFBoard` without defining a config section.

```ini
[tmc4671_board OpenFFBoard]
voltage_scale_ratio: 40.875
current_scale_ma_lsb: 1.272
adc_i_ux_select: 0
adc_i_v_select: 2
adc_i_wy_select: 1
adc_temp_reg: AGPI_B
adc_temp_pullup_resistor: 1500
adc_temp_t1: 25
adc_temp_r1: 10000
adc_temp_beta: 4300
```

### `[tmc4671 stepper_x]` with profiles

Profile sections must appear **before** the `[tmc4671]` section that references them.

```ini
[foc_motor LDO_2504b-EN1000]
# ... motor parameters ...

[tmc4671_board OpenFFBoard]
# ... or omit and rely on the built-in ...

[tmc4671 stepper_x]
motor_profile: LDO_2504b-EN1000
board_profile: OpenFFBoard
cs_pin: ...
run_current: 0.8
load_mass: 0.6
tune_current_pid: True
tune_motion_pid: True
```
