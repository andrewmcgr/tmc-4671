Understood. A formal, text-only specification is often much easier to port into whatever architecture or state machine you are using.

Here is the specification for the stochastic demodulation technique, with all mathematical operations written in Python syntax.

### System Prerequisites & Inputs

**Required Libraries**

* Requires a math library equivalent for `math.sqrt()` and `math.pi`.

**Required Input Variables**

* `R_ohms`: Phase DC resistance in Ohms (float).
* `V_ac`: Applied open-loop voltage amplitude in Volts (float). Must account for bus voltage and PWM scaling.
* `F_inject`: Non-integer injection frequency in Hz (float). Example: 2317.0.
* `N_samples`: Number of erratic samples to accumulate (integer). Example: 500.

---

### Phase 1: Hardware Configuration & Data Acquisition

**1. Configure TMC4671**

* Set `OPENLOOP_VELOCITY` to `F_inject`.
* Set `OPENLOOP_UQ_UD_EXT` to apply `V_ac`.
* Set `PHI_E_SELECTION` to open-loop mode.

**2. Execute Stochastic Sampling**

* Loop `N_samples` times.
* In each iteration, read the raw 16-bit registers for `PID_ERROR_DATA_ID` and `PID_ERROR_DATA_IQ`.
* Accumulate the read values into running totals. Erratic polling delays (e.g., around 1 ms) are preferred to ensure the 2x frequency ripple is sampled stochastically.

**3. Cleanup and Scaling**

* Disable the open-loop voltage injection immediately after the loop completes.
* Divide the accumulated totals by `N_samples` to extract the raw DC offsets.
* Convert the raw ADC offsets into real continuous Amperes. Assign these to `Id_amps` and `Iq_amps`.

---

### Phase 2: Geometric Admittance Extraction

**1. Calculate Midpoint Admittance**

* Conductance: `G = Id_amps / V_ac`
* Susceptance: `B = Iq_amps / V_ac`
* *Note: Inductive susceptance must be negative. If hardware scaling flips the sign to positive, multiply `B` by -1.*

**2. Define the Admittance Circle**

* Center X: `Cx = 1.0 / (2.0 * R_ohms)`
* Center Y: `Cy = 0.0`
* Radius: `r = 1.0 / (2.0 * R_ohms)`

**3. Calculate Distance to Midpoint**

* Delta X: `dx = G - Cx`
* Delta Y: `dy = B`
* Distance: `d = math.sqrt((dx  2) + (dy  2))`

**4. Calculate Chord Half-Length**

* Calculate the square of the half-length: `h_squared = (r  2) - (d  2)`
* Clamp to zero to prevent floating-point faults: `h_squared = max(0.0, h_squared)`
* Half-length: `h = math.sqrt(h_squared)`

**5. Calculate Perpendicular Unit Vector**

* Vector X: `vx = -dy / d`
* Vector Y: `vy = dx / d`

**6. Locate Distinct Admittances on the Circle**

* Point 1 Conductance: `G1 = G + (h * vx)`
* Point 1 Susceptance: `B1 = B + (h * vy)`
* Point 2 Conductance: `G2 = G - (h * vx)`
* Point 2 Susceptance: `B2 = B - (h * vy)`

---

### Phase 3: Inductance Conversion & Assignment

**1. Convert Admittances to Inductance**

* Angular Frequency: `omega = 2.0 * math.pi * F_inject`
* Inductance 1: `L1 = -B1 / (omega * ((G1  2) + (B1  2)))`
* Inductance 2: `L2 = -B2 / (omega * ((G2  2) + (B2  2)))`

**2. Assign Axes Based on Saliency**

* Torque Axis (`Lq`): `max(L1, L2)`
* Flux Axis (`Ld`): `min(L1, L2)`
