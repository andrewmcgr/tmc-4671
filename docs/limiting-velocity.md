Here is the mathematical relationship and its definitions formatted strictly in standard Markdown.

---

## The Voltage Limiting Formula

To find the maximum electrical velocity (**$\omega_{max}$**) before the motor hits voltage saturation and requires a reduction in acceleration, use the following equation:

$$\omega_{max} = \frac{-R_s I_q K_e + \sqrt{(R_s I_q K_e)^2 - (K_e^2 + \omega^2 L_d^2)\left((R_s I_d + \alpha L_d I_q)^2 + (R_s I_q + \alpha L_q I_d)^2 - \frac{V_{bus}^2}{3}\right)}}{K_e^2 + \omega^2 L_d^2}$$

### Simplified Linear Approximation

If we assume $I_d = 0$ (no field weakening) and neglect the cross-coupling inductive voltage drops during acceleration to look at the primary bottleneck, the formula simplifies to:

$$\omega_{max} \approx \frac{\sqrt{\frac{V_{bus}^2}{3} - (R_s I_q)^2} - \alpha L_q I_q}{K_e}$$

---

## Variable Definitions

| Variable | Description | Unit |
| --- | --- | --- |
| **$\omega_{max}$** | Maximum electrical speed before saturation | $\text{rad/s}$ (electrical) |
| **$V_{bus}$** | DC bridge supply voltage | $\text{V}$ (Volts) |
| **$K_e$** | Motor Back-EMF constant | $\text{V} \cdot \text{s/rad}$ (electrical) |
| **$\alpha$** | Target electrical acceleration | $\text{rad/s}^2$ (electrical) |
| **$I_q$** | Quadrature axis (torque-producing) current | $\text{A}$ (Amperes) |
| **$I_d$** | Direct axis (flux-altering) current | $\text{A}$ (Amperes) |
| **$R_s$** | Motor phase resistance | $\Omega$ (Ohms) |
| **$L_d$** | Direct axis inductance | $\text{H}$ (Henries) |
| **$L_q$** | Quadrature axis inductance | $\text{H}$ (Henries) |

---

### Useful Conversion Notes

* **Mechanical Speed:** To convert the electrical speed ($\omega_{max}$) to standard mechanical RPM, use:

$$\text{RPM} = \frac{\omega_{max} \times 60}{2\pi \times \text{Pole Pairs}}$$


* **Acceleration Current:** The required $I_q$ current for your acceleration target is tied directly to system inertia ($J$) and the motor torque constant ($K_t$) via:

$$I_q = \frac{J \alpha}{K_t}$$
