# Inertia measurement — status and open problems

Branch: `measure-inertia-ratio` (not merged to main as of June 2026).

## What was implemented

`TMC_MEASURE_INERTIA STEPPER=<name>` measures the Kt/J ratio (motor torque constant divided by effective rotor + load inertia, in rad s⁻² A⁻¹). The value is stored in `motor_jt` and shown by `TMC_DEBUG_MOTOR`.

### Method

1. All other TMC4671 axes are de-energised (stopped mode, TMC6100 gate driver disabled) to break the CoreXY magnetic coupling.
2. The target motor is aligned to PHI_E = 0 in UQ/UD-EXT mode (d-axis hold at half run-current) with a 0.75 s dwell.
3. **Successive approximation** (new as of `4799a8f`): starting at 20 mA, the current is scaled proportionally toward `ppr // 8` counts (one-eighth revolution ≈ 45°) of displacement per pulse, converging in ~2–3 iterations.
4. The found current is used for a **4-pulse measurement** in closed-loop torque mode (PHI_E_SELECTION = 3, torque_mode): forward × 2, reverse × 2, each = torque pulse for `dt` + zero torque coast-to-stop for `settle`.
5. The second pulse in each direction is used for the Kt/J calculation (first pulse absorbs backlash).
6. Formula: `alpha = d_avg × 4π / (PPR × dt²)`, `motor_jt = alpha / Iq_A` (coast-to-stop overshoot means this is a slight upper bound on the true value).
7. All other axes are restored (PWM_CHOP = 7, gate driver re-enabled). Motors need M17 to resume position mode.

### Parameters

| Parameter | Default | Notes |
|---|---|---|
| `PULSE_DURATION` | 0.05 s | Accel phase duration |
| `SETTLE_DURATION` | 1.0 s | Coast-to-stop wait |
| `MAX_CURRENT` | run_current / 2 | Upper bound for the current search |

## Known problems / open work

### Kt/J is very high on this hardware

The measured value on the CoreXY at v24p4 is approximately **1800 rad s⁻² A⁻¹**. This is a linear-rail machine with very low friction, so the effective J is small.

Consequence: even at the auto-selected "small" current, the motor can reach significant angular velocity within `dt = 0.05 s`:
- v_peak = Kt/J × Iq × dt = 1800 × Iq × 0.05

For the motor to coast to rest within `settle = 1.0 s`, friction must decelerate it from v_peak. On low-friction rails this may require many seconds. The successive approximation targets `ppr // 8` displacement (≈ 45°), which for Kt/J = 1800 corresponds to:
- d = ½ × alpha × dt² = ½ × 1800 × Iq × 0.05² = 2.25 × Iq (in rad, then × PPR/2π for counts)
- At PPR = 4000: target_counts = 500 → Iq ≈ 2.25 × Iq × 4000/(2π) ... solving: Iq = 500 × 2π / (4000 × 2.25) ≈ 0.175 A
- v_peak = 1800 × 0.175 × 0.05 = 15.75 rad/s ≈ 150 RPM

Stopping from 150 RPM against viscous friction alone can take 3–10 s on smooth linear rails, well beyond the 1 s settle. The measurement still works in practice if `SETTLE_DURATION` is increased, but the default is too short for low-friction machines.

### Possible fixes

**A — Adaptive settle**: after zeroing torque, poll `ABN_DECODER_COUNT` repeatedly until it stops changing. No hardware velocity register exists (`ABN_DECODER_VELOCITY` is not in the register map), so this must be done by reading the position twice with a short gap and checking for drift. Adds SPI traffic but avoids needing a large fixed settle time.

**B — Braking phase**: re-introduce the braking phase that was in `b411b08` before `4cb6441` removed it. Apply −Iq for `dt` after the accel pulse. The motor decelerates predictably and stops within `dt` seconds. Settle time can then be reduced to ~2× dt. The formula uses `d_mid` (displacement at mid-point = end of accel phase only), which gives an exact result with no coast contribution. This is the most reliable approach.

**C — Reduce `dt`**: shrink the pulse duration so v_peak is smaller. At dt = 0.01 s: v_peak = 1800 × 0.175 × 0.01 = 3.15 rad/s — would settle in 1 s even on smooth rails. Displacement = 500 × (0.01/0.05)² = 20 counts, which may be too small for reliable counting (encoder noise, quantisation).

**D — Velocity feedback target**: instead of a fixed pulse duration, apply torque until a target v_peak is reached (e.g., 5 rad/s), then zero torque. Requires reading a velocity estimate, which the TMC4671 provides indirectly via differencing `ABN_DECODER_COUNT` reads.

### Recommendation

Option B (restore braking phase) is the cleanest long-term solution. It eliminates the settle-time problem entirely, gives a physically exact formula, and is robust across a wide range of Kt/J values and friction levels. The additional complexity (one extra dwell + mid-point encoder read) is modest.
