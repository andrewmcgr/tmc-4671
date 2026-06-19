# Sensorless homing options for TMC4671

`TMCVirtualPinHelper` exposes a `virtual_endstop` pin. Its mechanism:
`STATUS_FLAGS & STATUS_MASK` drives the TMC4671's STATUS output pin → `diag_pin` GPIO on the MCU → Klipper polls it as an endstop.

The signalling path (STATUS pin → MCU → Klipper) works. The problem is that the STATUS_FLAGS bits currently in the homing mask do not fire reliably when the motor hits a hard mechanical stop.

## Why the current mask fails

When the motor stalls in position mode:

1. Step pulses keep advancing the position target
2. Position error grows → position PID drives velocity target up to `PID_VELOCITY_LIMIT`
3. Velocity error = velocity_target − 0 → velocity PID I-term drives torque target upward
4. Torque target is clamped by `PID_TORQUE_FLUX_LIMITS` (= run_current = 3.54 A)
5. At standstill, 3.54 A only needs V = R × I ≈ 1.14 × 3.54 ≈ **4 V**, far below the PIDOUT_UQ_UD_LIMITS of 31440/32767 × 24 V ≈ **23 V**

`PID_IQ_OUTPUT_LIMIT` and `PID_ID_OUTPUT_LIMIT` — the two primary bits in the current mask — only fire when UQ/UD hits PIDOUT_UQ_UD_LIMITS (23 V). A stalled motor at the current limit needs only 4 V. **They never fire.**

`PID_V_OUTPUT_LIMIT` does eventually fire, but only after the velocity I-term accumulates enough to saturate the torque target. With `foc_pid_velocity_i = 0.0188` and a velocity error of ~47253 counts/s, detection takes **3–4 seconds**. That is too slow for practical homing.

`PID_X_OUTPUT_LIMIT` (bit 3) — the position PID output limit — is **not in the current mask at all**, and would fire faster than the velocity output limit.

There is no dedicated "stall" register or flag in the TMC4671; there is no StallGuard equivalent.

## Options

### Option A — Tighten PIDOUT_UQ_UD_LIMITS during homing (most reliable, fastest)

The voltage a free-moving motor needs at homing speed is approximately
`V_free ≈ R × I_homing + Kt × ω`. At slow homing speeds back-EMF is negligible,
so `V_free ≈ R × I_homing`. Set PIDOUT_UQ_UD_LIMITS to just above `V_free`:

```
limit = round((R * I_homing * safety_factor) / VM * 32767)
# e.g. R=1.14, I=1A, VM=24V, factor=1.5 → round(1.14*1*1.5/24*32767) ≈ 2333
```

At stall UQ immediately tries to maintain current but the voltage limit clamps it →
`IPARK_CIRLIM_LIMIT_U_Q` (bit 17) fires within microseconds. Restore normal limits
in `handle_homing_move_end`.

Add `IPARK_CIRLIM_LIMIT_U_Q` and `IPARK_CIRLIM_LIMIT_U_D` (bits 16–17) to the
homing mask.

The `safety_factor` needs tuning: too tight → false trigger during free movement;
too loose → slow detection.

### Option B — Reduce PID_VELOCITY_LIMIT + add PID_X_OUTPUT_LIMIT to mask

There is already a commented-out line in `handle_homing_move_begin` (tmc4671.py line ~707):

```python
#self.mcu_tmc.write_field("PID_VELOCITY_LIMIT", 3000)
```

`PID_X_OUTPUT_LIMIT` (bit 3) fires when the position PID output (velocity target) hits
`PID_VELOCITY_LIMIT`. Position error needed = `PID_VELOCITY_LIMIT / P_position`.
With P = 15.7:

| PID_VELOCITY_LIMIT | Error needed | Motor rotation |
|---|---|---|
| 47253 (current) | 3010 counts | ~270° — far too much |
| 3000 | 191 counts | ~17° — still large |
| 500 | 32 counts | ~3° / ~0.1 mm — usable |

Constraint: PID_VELOCITY_LIMIT must be ≥ the velocity commanded during homing, or the
motor cannot track the step pulses during free movement. The correct value depends on
homing speed in TMC4671 velocity units. Option A avoids this dependency.

Also add `PID_X_OUTPUT_LIMIT` to `homing_mask` (it is currently absent).

### Option C — Add PID_IQ_TARGET_LIMIT to mask (slow but trivial)

`PID_IQ_TARGET_LIMIT` (bit 12) fires when the velocity I-term drives the torque target
above the current limit. Add this bit to `homing_mask` in the config. Detection still
takes several seconds, but it will eventually fire. Reasonable fallback if nothing else
is working yet — requires no code change, only a config line:

```ini
homing_mask: PID_IQ_TARGET_LIMIT, PID_V_OUTPUT_LIMIT, PID_X_ERRSUM_LIMIT, PID_ID_TARGET_LIMIT, REF_SW_R, REF_SW_L
```

### Option D — Velocity mode homing (most reliable long-term)

Position mode is the wrong mode for sensorless homing. In velocity mode:

- Command a small constant velocity target directly to `PID_VELOCITY_TARGET`
- Motor moves at that velocity; at stall, actual velocity drops to zero
- Velocity error = constant `velocity_target` → `PID_V_ERRSUM_LIMIT` fires quickly
  (the I-term saturates proportionally to velocity_target, not accumulated position error)
- Detection time is predictable and tunable

This requires a custom `TMC_HOME STEPPER=x DIRECTION=+ SPEED=5` G-code command that:

1. Switches to velocity mode
2. Commands the appropriate velocity
3. Waits for STATUS_FLAGS (with `PID_V_ERRSUM_LIMIT` in mask) or timeout
4. Switches back to position mode, resets position

This bypasses standard G28/step-pulse homing but integrates cleanly with Klipper's
macro system via `[homing_override]`.

### Option E — Software position-deviation polling

Read `PID_ERROR_PID_POSITION_ERROR` (register 0x6C, addr=3) via SPI every 20ms from a
reactor callback during homing. If deviation exceeds a threshold, stop the move.
The problem is that there is no clean way to inject a stop into Klipper's trsync from
the host side without MCU cooperation. Complex; not recommended.

## Recommended path

**Immediate diagnostic**: `handle_homing_move_end` already logs STATUS_FLAGS. Check
which bits (if any) were set when the motor hit the stop.

**Practical fix**: **Option A** — tighten PIDOUT_UQ_UD_LIMITS during homing and add
`IPARK_CIRLIM_LIMIT_U_Q`/`U_D` to the homing mask. This converts stall detection from
"wait N seconds for PID integration" to "immediate voltage saturation." The limit value
is directly calculable from measured R, homing current, and VM.

**Long-term**: **Option D** — velocity-mode `TMC_HOME` command. Most reliable
architecture and the best fit for what the hardware does naturally.
