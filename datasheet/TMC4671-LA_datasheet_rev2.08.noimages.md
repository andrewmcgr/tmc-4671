Ily functional servo controller for a wide range

## TMC4671 Datasheet

IC Version V1.3 | Document Revision V2.08 · 2022-July-26

TheTMC4671isafullyintegratedservocontroller, providing Field Oriented Control for BLDC/PMSM and 2-phase Stepper Motors as well as DC motors and voice coils. All control functions are implemented in hardware. Integrated ADCs, position sensor interfaces, position interpolators, enable a fully functional servo controller for a wide range of servo applications.


## Applications

- Pick and Place Machines
- Robotics
- Factory Automation

## Simplified Block Diagram


©2022 TRINAMIC Motion Control GmbH &amp; Co. KG, Hamburg, Germany Terms of delivery and rights to technical change reserved. Download newest version at: www.trinamic.com




- E-Mobility

## Features

- Torque Control (FOC), Velocity Control, Position Control
- Servo Controller w/ Field Oriented Control (FOC)
- Integrated ADCs, ∆Σ -ADCFrontend
- Supports 3-Phase PMSM/BLDC, 2-Phase Stepper Motors, and 1-Phase DC Motors
- EncoderEngine: Hall analog/digital, Encoder analog/digital
- Fast PWMEngine(25kHz...100kHz)
- Step-Direction Interface (S/D)
- Application SPI + Debug (UART, SPI)
- Pumps
- Laboratory Automation · Blowers

## Contents

| 2 Functional Summary                                                                                                                                                                             | 2 Functional Summary                                                                                                                                                                             | 2 Functional Summary                                                                                                                                                 | 7     |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| 3 FOC Basics 3.1 Why FOC? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        | 3 FOC Basics 3.1 Why FOC? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        | 3 FOC Basics 3.1 Why FOC? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                            | 9     |
| . . . . . . . .                                                                                                                                                                                  | . . . . . . . .                                                                                                                                                                                  | . . . . . . . .                                                                                                                                                      | 9     |
| 3.2 What is FOC? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                         | 3.2 What is FOC? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                         | . . . . . . . . .                                                                                                                                                    | 9     |
| 3.3 Why FOC as pure Hardware Solution? . . . . . . . . . . . . . . .                                                                                                                             | 3.3 Why FOC as pure Hardware Solution? . . . . . . . . . . . . . . .                                                                                                                             | . . . . . . . . . . . . . . . . .                                                                                                                                    | 9     |
| 3.4 How does FOC work? . . . . . . . . . . . . . . .                                                                                                                                             | 3.4 How does FOC work? . . . . . . . . . . . . . . .                                                                                                                                             | . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                                      | 10    |
| 3.5 What is Required for FOC?                                                                                                                                                                    | 3.5 What is Required for FOC?                                                                                                                                                                    | . . . . . . . . . . . . . . .                                                                                                                                        | 10 11 |
|                                                                                                                                                                                                  | 3.5.1                                                                                                                                                                                            | . . . . . . . . . . . . . . . . . Coordinate Transformations - Clarke, Park, iClarke, iPark . . . . . . . . . . . . . . . . . . . . . . . . .                        |       |
|                                                                                                                                                                                                  | 3.5.2 3.5.3                                                                                                                                                                                      | Measurement of Stator Coil Currents . . . . . . . Stator Coil Currents I_U, I_V, I_W and                                                                             | 11    |
|                                                                                                                                                                                                  |                                                                                                                                                                                                  | . . . . . . . . Association to Terminal Voltages U_U, U_V, U_W A/LSB - ADC Integer Current Value to Real World Unit . . .                                            | 11    |
|                                                                                                                                                                                                  | 3.5.4                                                                                                                                                                                            | IgainADC [ ] . . . . . . . Unit .                                                                                                                                    | 12 12 |
|                                                                                                                                                                                                  | 3.5.5                                                                                                                                                                                            | UgainADC [ V/LSB ] - ADC Integer Voltage Value to Real World . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                             |       |
|                                                                                                                                                                                                  | 3.5.6                                                                                                                                                                                            | Measurement of Rotor Angle . .                                                                                                                                       | 12    |
|                                                                                                                                                                                                  | 3.5.7                                                                                                                                                                                            | . . . . . . . . Measured Rotor Angle vs. Magnetic Axis of Rotor vs. Magnetic Axis of Stator .                                                                        | 12 13 |
|                                                                                                                                                                                                  | 3.5.8                                                                                                                                                                                            | . Knowledge of Relevant Motor Parameters and Position Sensor (Encoder) Parameters                                                                                    | 14    |
|                                                                                                                                                                                                  | 3.5.9                                                                                                                                                                                            | Proportional Integral (PI) Controllers for Closed Loop Current Control . . . . . . Pulse Width Modulation (PWM) and Space Vector Pulse Width Modulation (SVPWM)      | 14    |
|                                                                                                                                                                                                  | 3.5.10                                                                                                                                                                                           | . . .                                                                                                                                                                |       |
|                                                                                                                                                                                                  | 3.5.11                                                                                                                                                                                           | Orientations, Models of Motors, and Coordinate Transformations . . . . . .                                                                                           | 15    |
| 4 Functional Description                                                                                                                                                                         | 4 Functional Description                                                                                                                                                                         | 4 Functional Description                                                                                                                                             | 16    |
| 4.1 Functional Blocks . . . . . . . . . . . . 4.2 . .                                                                                                                                            | 4.1 Functional Blocks . . . . . . . . . . . . 4.2 . .                                                                                                                                            | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                        | 16 17 |
|                                                                                                                                                                                                  | Communication Interfaces . . . . 4.2.1 SPI Slave User Interface .                                                                                                                                | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                        |       |
|                                                                                                                                                                                                  |                                                                                                                                                                                                  | . . . . . . . . . . . . . . . .                                                                                                                                      | 17    |
|                                                                                                                                                                                                  | 4.2.2                                                                                                                                                                                            | . . . . . . . . . . . . . . . . . TRINAMIC Real-Time Monitoring Interface (SPI Master) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 20 21 |
|                                                                                                                                                                                                  | 4.2.3                                                                                                                                                                                            | UART Interface . . . . . . . . . . . . . . . .                                                                                                                       |       |
|                                                                                                                                                                                                  | 4.2.4 4.2.5                                                                                                                                                                                      | Step/Direction Interface . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                   | 22    |
|                                                                                                                                                                                                  |                                                                                                                                                                                                  | Single Pin Interface . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                         | 22 23 |
|                                                                                                                                                                                                  | 4.2.6                                                                                                                                                                                            | GPIO Interface . . . . Representation,                                                                                                                               |       |
| . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4.3 Numerical Electrical Angle, Mechanical Angle, and Pole Pairs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4.3 Numerical Electrical Angle, Mechanical Angle, and Pole Pairs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | . . . .                                                                                                                                                              | 24    |
|                                                                                                                                                                                                  | 4.3.1                                                                                                                                                                                            | Numerical Representation . . . .                                                                                                                                     | 24    |
|                                                                                                                                                                                                  | 4.3.2                                                                                                                                                                                            | N_POLE_PAIRS, PHI_E, PHI_M . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                         | 25    |
|                                                                                                                                                                                                  | 4.3.3                                                                                                                                                                                            | . . . . . . Numerical Representation of Angles PHI . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                           | 26    |
| 4.4 ADC Engine . 4.4.1 ADC                                                                                                                                                                       | 4.4 ADC Engine . 4.4.1 ADC                                                                                                                                                                       | . . . . . . . . . . . . . . . . . . . .                                                                                                                              | 28    |
|                                                                                                                                                                                                  | 4.4.2                                                                                                                                                                                            | . . . . . current sensing channels ADC_I1 and ADC_I0 . . . . . . . . . . . . . . . . . . ADCforanalogHall signals or analogsin-cos-encodersAENC_UX,AENC_VN,AENC_WY   | 28 28 |
|                                                                                                                                                                                                  |                                                                                                                                                                                                  | ADC_VM .                                                                                                                                                             | 28    |
|                                                                                                                                                                                                  | 4.4.3                                                                                                                                                                                            | ADC supply voltage measurement . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                               |       |
|                                                                                                                                                                                                  | 4.4.4                                                                                                                                                                                            | ADC_VM for Brake Choppper . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                        | 29    |
|                                                                                                                                                                                                  | 4.4.5                                                                                                                                                                                            | ADC EXT register option . . . . . . . . . . . . . . . ADC general purpose                                                                                            | 29    |
|                                                                                                                                                                                                  | 4.4.6                                                                                                                                                                                            | . . . . . . . . . . . . . . . . . analog inputs AGPI_A and AGPI_B . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                      | 29    |
|                                                                                                                                                                                                  | 4.4.7                                                                                                                                                                                            | ADC RAW values . . . . . . . . . . . . . . ADC_SCALE and                                                                                                             | 29    |
|                                                                                                                                                                                                  | 4.4.8 4.4.9                                                                                                                                                                                      | ADC_OFFSET . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                         | 29 29 |
|                                                                                                                                                                                                  |                                                                                                                                                                                                  | . . . . . . ADC Gain Factors for Real World Values . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                         | 30    |
|                                                                                                                                                                                                  | 4.4.10                                                                                                                                                                                           | Internal Delta Sigma ADCs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                              | 30    |
|                                                                                                                                                                                                  | 4.4.11 4.4.12                                                                                                                                                                                    | . . . . . Internal Delta Sigma ADC Input Stage Configuration External Delta Sigma ADCs . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .               | 32    |
|                                                                                                                                                                                                  | 4.4.13                                                                                                                                                                                           | ADC Group A and ADC Group B . . . . . . . . . . . .                                                                                                                  | 32    |
|                                                                                                                                                                                                  | 4.4.14                                                                                                                                                                                           | . . . . . . . . . . . . Delta . . . . . . . . . . . . Internal                                                                                                       | 32    |
|                                                                                                                                                                                                  | 4.4.15                                                                                                                                                                                           | . . . . . Sigma Configuration and Timing Configuration . . . . . Delta Sigma Modulators - Mapping of V_RAW to . . . . . . . .                                        | 36    |
|                                                                                                                                                                                                  | 4.4.16                                                                                                                                                                                           | ADC_RAW External Delta Sigma Modulator Interface . . . . . . . . . . . . . . . . . . . . . . .                                                                       | 37    |


1

Order Codes

6

4.5

Analog Signal Conditioning

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

39

|         | 4.5.1                                                               | 4.5.1                                                                                                                                                    | 39    |
|---------|---------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
|         |                                                                     | FOC3 - Stator Coil Currents I_U, I_V, I_W and associated Voltages FOC2                                                                                   |       |
|         | 4.5.2                                                               | U_U, U_V, - Stepper Coil Currents I_X, I_Y and associated Voltages U_X, U_Y                                                                              | 40    |
|         | 4.5.3                                                               | . . FOC1 - DC Motor Coil Current I_X1, I_X2, and associated Voltage U_X1, U_X2 ADC . . . . . . . . . . . . . . . .                                       | 40    |
|         | 4.5.4                                                               | Selector & ADC Scaler w/ Offset Correction . . . . . . . . . . . . . . . . . . . . . . . .                                                               | 41    |
| 4.6     | Encoder Engine .                                                    | . . . . . . . . . . . . . . .                                                                                                                            | 42    |
|         | 4.6.1 4.6.2                                                         | Open-Loop Encoder . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . Incremental ABN                                                            | 42    |
|         | 4.6.3                                                               | . . Encoder . . . . . . . . . . . . . . . . . . . . . . . . . . Secondary Incremental                                                                    | 43    |
|         |                                                                     | . . . ABN . . . . Digital                                                                                                                                | 45    |
|         | 4.6.4                                                               | Encoder . . . . . . . . . . . . . . . . . . Hall Sensor Interface with optional Interim Position Interpolation . Interpolation . . . . . . . . . .       | 45    |
|         | 4.6.5                                                               | Digital Hall Sensor - Interim Position . . . .                                                                                                           | 46    |
|         | 4.6.6                                                               | Digital Hall Sensors - Masking, Filtering, and PWMcenter sampling . . . . Digital Hall Sensors together with Incremental Encoder . . . . . .             | 46    |
|         | 4.6.7 4.6.8                                                         | . . . . . Analog                                                                                                                                         | 48 48 |
|         |                                                                     | Hall and Analog Encoder Interface (SinCos of 0° 90° or 0° 120° 240°)                                                                                     |       |
|         | 4.6.9                                                               | Analog Position Decoder (SinCos of 0°90° or 0°120°240°) . . . . . . . . . . Initialization Support . . . . . . . . . . . . . . . .                       | 49    |
|         | 4.6.10 4.6.11                                                       | Encoder . . . . . . . . . . Velocity Measurement . . . . .                                                                                               | 50    |
|         |                                                                     | . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                    | 50    |
|         | 4.6.12 FOC23                                                        | Reference Switches . . . . . . . . . . . . . . . . . . . . . . . Engine . . . . . . . . .                                                                | 51 52 |
| 4.7     | . . . . . . . . . . . . . . . . . . . pins . . . . . . . . . . . .  | . . . . . . . . . . . . . . . . . . . . . .                                                                                                              |       |
|         | 4.7.1                                                               | ENI and ENO . . . . . . . . . . . . . . . . . . . . . .                                                                                                  | 52    |
|         | 4.7.2                                                               | PI Controllers . . . . . . . . . . . . . . . . .                                                                                                         | 52    |
|         | 4.7.3                                                               | . . . . . . . . . . . . . . . . . . . PI Controller Calculations - Classic Structure . . . . . . . . . . . . . . . . . PI                                | 52    |
|         | 4.7.4                                                               | . Controller Calculations - Advanced Structure . . . . . . . . . . . . . . . . Controller - Clipping . . . . . . . . . . . . . . .                       | 54    |
|         | 4.7.5 4.7.6                                                         | PI . . . . . . . . . . . . . . . .                                                                                                                       | 56    |
|         | 4.7.7                                                               | PI Flux & PI Torque Controller . . . . . . . . . . . . . . . . . . . . . . . . . . PI Velocity Controller . . . . .                                      | 57    |
|         |                                                                     | . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                    | 57 58 |
|         | 4.7.8                                                               | P Position Controller . . . . . . . . . . . . . . . . . . .                                                                                              |       |
|         | 4.7.9                                                               | . . . . . . . . . . . . . Inner FOC Control Loop - Flux & Torque . . . . . . . . . .                                                                     | 58    |
|         | 4.7.10 4.7.11                                                       | . . . . . . . . . . FOC Transformations and PI(D) for control of Flux & Torque . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 58    |
|         |                                                                     | Motion Modes . . . . . . . Brake Chopper                                                                                                                 | 59 60 |
|         | 4.7.12 Filtering                                                    | . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                      |       |
| 4.8     | . . . . . . . . . and Feed-Forward Control . . . . . . . . . . . .  | . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                                      | 61    |
|         | 4.8.1                                                               | Biquad Filters . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                       | 61    |
|         | 4.8.2 4.8.3                                                         | Standard Velocity Filter . . . . . . . . . . . . . . . . . . . . . . . .                                                                                 | 62    |
|         |                                                                     | . . . . . . Feed-Forward Control Structure . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                               | 62 63 |
| 4.9     | PWMEngine . . . . . . . . . . . . . 4.9.1 PWMPolarities . . . . . . | . . . . . . . . . . . . . . . . . . . . . .                                                                                                              |       |
|         |                                                                     | . . . . . . . . . . . . . . . . . . . .                                                                                                                  | 63    |
|         | 4.9.2 4.9.3                                                         | . . . . . . . . . PWMEngine and associated Motor Connectors . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                  | 64 65 |
|         | 4.9.4                                                               | PWMFrequency . . . . . . . . . . . . . . . . . . . .                                                                                                     | 65    |
|         |                                                                     | PWMResolution . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                    |       |
|         | 4.9.5                                                               | PWMModes . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                       | 65    |
|         | 4.9.6                                                               | . . . . . . Break-Before-Make (BBM) . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                | 65    |
|         | 4.9.7 4.9.8                                                         | . . Space Vector PWM(SVPWM) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                      | 66 66 |
| 5       | Real- and Integer-Conversions . Safety Functions FOC                | Real- and Integer-Conversions . Safety Functions FOC                                                                                                     | 67    |
| 6       | Setup - How to Turn a Motor                                         | Setup - How to Turn a Motor                                                                                                                              | 70 70 |
|         | Select Motor Type . . . . . . .                                     | . . . . . . . . . . .                                                                                                                                    |       |
|         | 6.1.1                                                               | . . . . . . . . . . . . . . . . . . . FOC1 Setup - How to Turn a Single Phase DC Motor                                                                   |       |
| 6.1     |                                                                     | . . . . . . . . . . . . . . . Setup - How to Turn a Two Phase Motor (Stepper) . . . . . . . . . . .                                                      | 70 70 |
|         | 6.1.2 6.1.3                                                         | FOC2 FOC3 Setup - How to Turn a Three Phase Motor (PMSM or BLDC) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                 | 70 70 |
|         | Set Number of Pole Pairs (NPP) Run Motor Open Loop . . . .          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                                          | 71    |
| 6.2 6.3 |                                                                     |                                                                                                                                                          |       |


6.3.1

Determination of Association between Phase Voltage and Phase Currents

.

.

.

.

.

.

71

| 6.3.2                                                                                                                                                                      | Determination of Direction of Rotation and Phase Shift of                                                      | . 71        |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|-------------|
| Selection of Position Sensors . . . . .                                                                                                                                    | Selection of Position Sensors . . . . .                                                                        |             |
| 6.4                                                                                                                                                                        | . . . . . . . . . . . . . .                                                                                    | . 71 71     |
| 6.4.1 6.4.2                                                                                                                                                                | . . Selection of FOC sensor for PHI_E . . . . . . . . . . . . . Selection of sensor for                        | . 71        |
| 6.4.3                                                                                                                                                                      | VELOCITY . . . . . . . . . . . . . .                                                                           | . 71        |
|                                                                                                                                                                            | Selection of sensor for POSITION . . . . . . . . of Operation - (Open Loop),                                   | .           |
| . . . . . 6.5 Modes Torque, Velocity, . . . . . . . . . . . . . . . . . . .                                                                                                | Positioning                                                                                                    | . 72        |
| 6.6 Controller Tuning .                                                                                                                                                    | . . . . . . . .                                                                                                | . 72        |
| Register Map 7.1                                                                                                                                                           | Register Map 7.1                                                                                               | 72 73       |
| Register Map - Overview Register Map -                                                                                                                                     | . . . . . . . . . . . . . . . . . .                                                                            | . 77        |
| . . . . . . 7.2 Functional Description                                                                                                                                     | . . . . . . . . . . . . . . . .                                                                                | .           |
| 7.3 Register Map - Defaults, min, max . .                                                                                                                                  | . . . . . . . . . . . . . . . .                                                                                | . 111       |
| Pinning                                                                                                                                                                    | Pinning                                                                                                        | 128         |
| TMC4671 Pin Table                                                                                                                                                          | TMC4671 Pin Table                                                                                              | 130         |
| 10 Electrical Characteristics . . . . . . . . . . . . . . . . . .                                                                                                          | . .                                                                                                            | 134 134     |
| 10.1 Absolute Maximum Ratings . . 10.2                                                                                                                                     | 10.1 Absolute Maximum Ratings . . 10.2                                                                         |             |
| Electrical Characteristics . . . . . . . . . 10.2.1 Operational Range . . . . . . .                                                                                        | . . . . . . . . . . . . . . .                                                                                  | . . 134     |
|                                                                                                                                                                            | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                        | . 134 .135  |
| 10.2.2 DC Characteristics . Sample Circuits                                                                                                                                | 10.2.2 DC Characteristics . Sample Circuits                                                                    |             |
|                                                                                                                                                                            | . . . . . . . . . . . . . . . . . . . .                                                                        | 136         |
| 11.1 Supply Pins . . . . . . . . . . . . 11.2 Clock and Reset Circuitry . . . . 11.3 Digital Encoder, Hall Sensor                                                          | . . . . . . . . . . . . . . . . . . .                                                                          | .136 .136   |
| .                                                                                                                                                                          | Switches .                                                                                                     | .136        |
| Interface and Reference 11.4 Analog Frontend . . . . . . . . . . . . . . . 11.5 Phase Current Measurement . . . . . . . . . . . . . . .                                    | . . . . . . . . . . . . . . . . . . . . . . . . . .                                                            | . 137 137   |
| .                                                                                                                                                                          | .                                                                                                              | . .139      |
| 11.6 Power Stage Interface . . . .                                                                                                                                         | . . . . . . . . . . . . .                                                                                      |             |
| 12 Setup Guidelines                                                                                                                                                        | 12 Setup Guidelines                                                                                            | 140         |
| 13 Package Dimensions 14                                                                                                                                                   | 13 Package Dimensions 14                                                                                       | 141         |
|                                                                                                                                                                            |                                                                                                                | 144         |
| Supplemental Directives 14.1 Producer Information . . . . 14.2 Copyright . . . . . . . . . . . .                                                                           | . . . .                                                                                                        | 144         |
| . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                                                                          | . . . . . . . .                                                                                                | . . 144 144 |
| 14.3 Trademark Designations and Symbols . . . . 14.4 Target User . . . . . . . . . . . . . . . . . . . . . .                                                               | . . . .                                                                                                        | . . 144     |
| 14.5 Disclaimer: Life Support Systems . . . . . . . . .                                                                                                                    | 14.5 Disclaimer: Life Support Systems . . . . . . . . .                                                        | .           |
| . . . .                                                                                                                                                                    | . . . .                                                                                                        | 144 .       |
| 14.6 Disclaimer: Intended Use . . . 14.7 Collateral Documents & Tools .                                                                                                    | . . . . . . . . . . . . .                                                                                      | 144         |
|                                                                                                                                                                            | . . . . . . . . . . . . . . . . . . . .                                                                        | .145        |
| 15 Errata of TMC4671-LA/-ES2/-ES                                                                                                                                           | . . . .                                                                                                        | 146 .146    |
| 15.1 Errata of TMC4671-LA . . . . . . . . . . . . . . . 15.2 Fixes of TMC4671-LA/-ES2 vs. Errata of TMC4671-ES                                                             | 15.1 Errata of TMC4671-LA . . . . . . . . . . . . . . . 15.2 Fixes of TMC4671-LA/-ES2 vs. Errata of TMC4671-ES |             |
| . . . . . . . . .                                                                                                                                                          | . . . . . .                                                                                                    | .146 147    |
| . 15.3 Errata of TMC4671-ES Engineering Samples as Reference . 15.4 Actions to Avoid Trouble . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | . . .                                                                                                          | . .148      |
| 15.5 Recommendations . . . . . .                                                                                                                                           | . . .                                                                                                          | .148        |
| 16 Figures Index                                                                                                                                                           | 16 Figures Index                                                                                               | 149         |
| 17 Tables Index                                                                                                                                                            | 17 Tables Index                                                                                                | 150         |


| 18 Revision History 18.1 IC Revision .   | 151   |
|------------------------------------------|-------|
|                                          | . 151 |
| . . . .                                  |       |

.

.

.

.

.

.

.

.

.

.

.

.

. 151


18.2 Document Revision . .

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

## 1 Order Codes

Order Code

Table 1: Order codes

| TMC4671-LA                                                                                                                                | TMC4671 FOC Servo Controller IC   | 10.5mm x 6.5mm                                                              |
|-------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|-----------------------------------------------------------------------------|
| TMC4671-EVAL TMC4671-BOB Landungsbruecke TMC-UPS-2A24V-A-EVAL TMC-UPS-10A70V-A-EVAL TMC4671-2A24V-EV-KIT TMC4671-10A70V-EV-KIT USB-2-RTMI | TMC4671 Evaluation Board          | 55mm x 85mm 38mm x 40mm 85mm x 55mm 85mm x 55mm 85mm x 55mm - - 40mm x 20mm |
|                                                                                                                                           | TMC4671 Breakout Board            |                                                                             |
|                                                                                                                                           | MCU Board                         |                                                                             |
|                                                                                                                                           | Power Stage Board                 |                                                                             |
|                                                                                                                                           | Power Stage Board                 |                                                                             |
|                                                                                                                                           | Evaluation Kit                    |                                                                             |
|                                                                                                                                           | Evaluation Kit                    |                                                                             |
|                                                                                                                                           | Interface Adapter to use RTMI     |                                                                             |

Description

Size


## 2 Functional Summary

- -Torque (and flux) control mode

## · Servo Controller with Field Oriented Control (FOC)

- -Velocity control mode

## · Control Functions/PI Controllers

- -Position control mode
- -Programmable clipping of inputs and outputs of interim results
- -Status output with programmable mask for internal status signal selection
- -Integrator windup protection for all controllers

## · Supported Motor Types

- -FOC2 : 2-phase stepper motors
- -FOC3 : 3-phase permanent magnet synchronous motors (PMSM) / brushless DC motor (BLDC)
- -FOC1 : 1-phase brushed DC motors, or linear voice coil motors
- -Integrated Delta Sigma ADCs for current sense voltage, supply voltage, analog encoder, AGPIs

## · ADC Engine with Offset Correction and Scaling

- -Interface for isolated external current sensing Delta Sigma modulators
- -Open loop position generator (programmable [rpm], [rpm/s]) for initial setup

## · Position Feedback

- -Digital incremental encoder (ABN resp. ABZ, up to 2 MHz)
- -Digital Hall sensor interface (H1, H2, H3 resp. H\_U, H\_V, H\_W) with interim position interpolation
- -Secondary digital incremental encoder
- -Analog encoder/analog Hall sensor interface (SinCos (0°, 90°) or 0°, 120°, 240°)
- -multi-turn position counter (32-bit)
- -Position target, velocity and target torque filters (Biquad)

## · PWMEngine Including SVPWM

- -PWMauto scaling for transparent change of PWM frequency during motion
- -Programmable PWM frequency within the range of 25 kHz ...100 kHz
- -Programmable Brake-Before-Make (BBM) times (0 ns ...2.5 µ s) for digital gate control signals
- -Single bit SVPWM control (on/off) for Space Vector Modulation (switchable during operation)


## · SPI Application Communication Interface

- -Immediate SPI read response (register read access by single datagram)
- -40 bit datagram length (1 ReadWrite bit + 7 address bits + 32 data bits)
- -SPI clock frequency fSCK up to 2 MHz (8 MHz write, 8 MHz read w/ 500 ns pause after address)
- -High frequency sampling of real-time data via TRINAMIC's real-time monitoring system

## · TRINAMIC Real Time Monitoring Interface

- -Only single 10 pin high density connector on PCB needed

## · UART Debug Interface

- -Enables frequency response identification and auto tuning options with TRINAMIC's IDE
- -Three pin (GND, RxD, TxD) 3.3 V UART interface (1N8; 9600 (default), 115200, 921600, 3M bps)
- -Transparent register access parallel to embedded user application interface (SPI)
- -Available as port for external position sensors (e.g. absolute encoder together with processor)

## · Supply Voltages

## · IO Voltage

- -5V and 3.3V; VCC\_CORE is internally generated
- -3.3V for all digital IOs (choosable by VCCIO Supply)

## · Clock Frequency

- -5V common mode analog input voltage range (1.25V ... 2.5V differential operating range)
- -25 MHz (from external oscillator)
- -QFN76

## · Packages


## 3 FOC Basics

## 3.1 Why FOC?

This section gives a short introduction into some basics of Field Oriented Control (FOC) of electric motors.

TheField Oriented Control (FOC), alternatively named Vector Control (VC), is a method for the most energyefficient way of turning an electric motor.

The Field Oriented Control was independently developed by K. Hasse, TU Darmstadt, 1968, and by Felix Blaschke, TU Braunschweig, 1973. The FOC is a current regulation scheme for electro motors that takes the orientation of the magnetic field and the position of the rotor of the motor into account, regulating the strength in such way that the motor gives that amount of torque that is requested as target torque. The FOC maximizes active power and minimizes idle power - that finally results in power dissipation - by intelligent closed-loop control illustrated by figure 1.

Figure 1: Illustration of the FOC basic principle by cartoon: Maximize active power and minimize idle power and power dissipation by intelligent closed-loop control.


## 3.3 Why FOC as pure Hardware Solution?

The hardware FOC as an existing standard building block drastically reduces the effort in system setup. With that off the shelf building block, the starting point of FOC is the setup of the parameters for the FOC. Setting up and implement the FOC itself and building and programming required interface blocks is no longer necessary. The real parallel processing of hardware blocks de-couples the higher lever application software from high speed real-time tasks and simplifies the development of application software. With the TMC4671, the user is free to use its qualified CPU together with its qualified tool chain, freeing the user from fighting with processer-specific challenges concerning interrupt handling and direct memory access. There is no need for a dedicated tool chain to access the TMC4671 registers and to operate it just SPI (or UART) communication needs to be enabled for any given CPU.

The initial setup of the FOC is usually very time consuming and complex, although source code is freely available for various processors. This is because the FOC has many degrees of freedom that all need to fit together in a chain in order to work.

The hardware integration of the FOC drastically reduces the number of required components and reduces the required PCB space. This is in contrast to classical FOC servos formed by motor block and separate


## 3.2 What is FOC?

controller box wired with motor cable and encoder cable. The high integration of FOC, together with velocity controller and position controller, enables the FOC as a standard peripheral component that transforms digital information into physical motion. Compact size together with high performance and energy efficiency especially for battery powered mobile systems are enabling factors when embedded goes autonomous.

Two force components act on the rotor of an electric motor. One component is just pulling in radial direction (ID) where the other component is applying torque by pulling tangentially (IQ). The ideal FOC performs a closed loop current control that results in a pure torque generating current IQ - without direct current ID.

## 3.4 How does FOC work?

Figure 2: FOC optimizes torque by closed loop control while maximizing IQ and minimizing ID to 0


From top point of view, the FOC for 3-phase motors uses three phase currents of the stator interpreted as a current vector (Iu; Iv; Iw) and calculates three voltages interpreted as a voltage vector (Uu; Uv; Uw) taking the orientation of the rotor into account in a way that only a torque generating current IQ results.

To do so, the knowledge of some static parameters (number of pole pairs of the motor, number of pulses per revolution of an used encoder, orientation of encoder relative to magnetic axis of the rotor, count direction of the encoder) is required together with some dynamic parameters (phase currents, orientation of the rotor).

From top point of view, the FOC for 2-phase motors uses two phase currents of the stator interpreted as a current vector (Ix; Iy) and calculates two voltages interpreted as a voltage vector (Ux; Uy) taking the orientation of the rotor into account in a way that only a torque generating current IQ results.

The adjustment of P parameter P and I parameters of two PI controllers for closed loop control of the phase currents depends on electrical parameters of the motor (resistance, inductance, back EMF constant of the motor that is also the torque constant of the motor, supply voltage).

## 3.5 What is Required for FOC?

The FOC needs to know the direction of the magnetic axis of the rotor of the motor in reference to the magnetic axis of the stator of the motor. The magnetic flux of the stator is calculated from the currents through the phases of the motor. The magnetic flux of the rotor is fixed to the rotor and thereby determined by an encoder device.

The challenge of the FOC is the high number of degrees of freedom in all parameters.

For the FOC, the user needs to measure the currents through the coils of the stator and the angle of the rotor. The measured angle of the rotor needs to be adjusted to the magnetic axes.


## 3.5.1 Coordinate Transformations - Clarke, Park, iClarke, iPark

The TMC4671 takes care of the required transformations so the user no longer has to fight with implementation details of these transformations.

TheFOCrequiresdifferentcoordinatetransformations formulated as a set of matrix multiplications. These are the Clarke Transformation (Clarke), the Park Transformation (Park), the inverse Park Transformation (iPark) and the inverse Clarke Transformation (iClarke). The Park transformation is also known as DQ transformation, whereas the Clarke transformation is known as αβ transformation.

## 3.5.2 Measurement of Stator Coil Currents

Coil current stands for motor torque in context of FOC. This is because motor torque is proportional to motor current, defined by the torque constant of a motor. In addition, the torque depends on the orientation of the rotor of the motor relative to the magnetic field produced by the current through the coils of the stator of the motor.

The measurement of the stator coil currents is required for the FOC to calculate a magnetic axis out of the stator field caused by the currents flowing through the stator coils.

## 3.5.3 Stator Coil Currents I\_U, I\_V, I\_W and Association to Terminal Voltages U\_U, U\_V, U\_W

The correct association between stator terminal voltages U\_U, U\_V, U\_W and stator coil currents I\_U, I\_V, I\_W is essential for the FOC. In addition to the association, the signs of each current channel need to fit. Signs of the current can be adapted numerically by the ADC scaler. The mapping of ADC channels is programmablevia configuration registers for the ADC selector. Initial setup is supported by the integrated open loop encoder block, that can support the user to turn a motor open loop.

## 3.5.3.1 Chain of Gains for ADC Raw Values

$$S ^ { 6 } \sin ^ { 4 } \text {path intersection} \cos ^ { 6 } \text {
} \\ \text {ADC_RAW} = ( I _ { - } S E S \ast \text {ADC_GAIN} ) + \text {ADC_OFFSET} .$$

An ADC raw value is a result of a chain of gains that determine it. A coil current I\_SENSE flowing through a sense resistor causes a voltage difference according to Ohm's law. The resulting ADC raw value is a result of the analog signal path according to

The ADC\_GAIN is a result of a chain of gains with individual signs. The sign of the ADC\_GAIN is positive or negative, depending on the association of connections between sense amplifier inputs and the sense resistor terminals. The ADC\_OFFSET is the result of electrical offsets of the phase current measurement signal path. For the TMC4671, the maximum ADC\_RAW value ADC\_RAW\_MAX = (2 16 -1) and the minimum ADC raw value is ADC\_RAW\_MIN = 0.

$$\begin{array} { c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c c$$

For the FOC, the ADC\_RAW is scaled by the ADC scaler of the TMC4671 together with subtraction of offset to compensate it. Internally, the TMC4671 FOC engine calculates with s16 values. Thus, the ADC scaling needs to be chosen so that the measured currents fit into the s16 range. With the ADC scaler, the user can choose a scaling with physical units like [ mA ] .


## 3.5.4 IgainADC [ A/LSB ] - ADC Integer Current Value to Real World Unit

$$\int \lim i t s _ { \ } a n d { I } \varphi _ { I } & \colon \\ I _ { 0 } [ A ] & \ = \ \varinjlim A D C [ A / L S B ] * A D C _ { I } I _ { 0 } \\ I _ { 1 } [ A ] & \ = \ \varinjlim A D C [ A / L S B ] * A D C _ { I } I _ { 1 }$$

Together with ADC\_I0\_SCALE and ADC\_I0\_OFFSET and ADC\_I1\_SCALE and ADC\_I1\_OFFSET, measured ADC currents represented as 16 bit signed interger numbers (s16) represent real world currents. Multiplication of integer current value with gain scaling factor in unit Ampere per LSB (Low Significant Bit) gives the real world value of current in unit Ampere.

Different scalings between two associated current ADC channels can be trimmed by programing ADC\_I0\_SCALE and ADC\_I1\_SCALE. The IgainADC [ A/LSB ] needs to be determined from ADC gain factors, ADC reference voltage selection, and actual ADC scaling factor settings.

## 3.5.5 UgainADC [ V/LSB ] - ADC Integer Voltage Value to Real World Unit

$$\| \ v o n i g a { \varepsilon } \| _ { S } \ u n i t { v } .$$

MeasuredADCvoltagesrepresentedas16bitsignedinterger numbers (s16) represent real world voltages. Multiplication of integer voltage value with gain scaling factor in unit Volt per LSB (Low Significant Bit) gives the real world value of voltage in unit Volt.

TheUgainADC [ V/LSB ] needs to be determined from ADC gain factors, actual ADC gains, and ADC reference voltage settings.

## 3.5.6 Measurement of Rotor Angle

The TMC4671 does not support sensorless FOC.

Determination of the rotor angle is either done by sensors (digital encoder, analog encoder, digital Hall sensors, analog Hall sensors) or sensorless by a reconstruction of the rotor angle. Currently, there are no sensorless methods available for FOC that work in a general purpose way as a sensor down to velocity zero.

## 3.5.7 Measured Rotor Angle vs. Magnetic Axis of Rotor vs. Magnetic Axis of Stator

The direction of counting depends on the encoder, its mounting, and wiring and polarities of encoder signals and motor type. So, the direction of encoder counting is programmable for comfortable definition for a given combination of motor and encoder.

The rotor angle, measured by an encoder, needs to be adjusted to the magnetic axis of the rotor. This is because an incremental encoder has an arbitrary orientation relative to the magnetic axis of the rotor, and the rotor has an arbitrary orientation to magnetic axis of the stator.


## 3.5.7.1 Direction of Motion - Magnetic Field vs. Position Sensor

With an absolute encoder, once adjusted to the relative orientation of the rotor and to the relative orientation of the stator, one could start the FOC without initialization of the relative orientations.

For FOC it is essential, that the direction of revolution of the magnetic field is compatible with the direction of motion of the rotor position reconstructed from encoder signals: For revolution of magnetic field with positive direction, the decoder position needs to turn into the same positive direction. For revolution of magnetic field with negative direction, the decoder position needs to turn into the same negative direction.

## 3.5.7.2 Bang-Bang Initialization of the Encoder

A Bang-Bang initialization is an initialization where the motor is forced with high current into a specific position. For Bang-Bang initialization, the user sets a current into direction D that is strong enough to move the rotor into the desired direction. Other initialization methods ramp up the current smoothly and adjust the current vector to rotor movement detected by the encoder.

## 3.5.7.3 Encoder Initialization using Hall Sensors

The encoder can be initialized using digital Hall sensor signals. Digital Hall sensor signals give absolute positions within each electrical period with a resolution of sixty degrees. If the Hall sensor signals are used to initialize the encoder position on the first change of a Hall sensor signal, an absolute reference within the electrical period for commutation is given.

## 3.5.7.4 Minimum Movement Initialization of the Encoder

For minimal movement initialization of the encoder, the user slowly increases a current into direction D and adjusts an offset of the measured angle in a way that the rotor of the motor does not move during initialization while the offset of the measured angle is determined.

## 3.5.8 Knowledge of Relevant Motor Parameters and Position Sensor (Encoder) Parameters

The number of pole pairs is an essential motor parameter. It defines the ratio between electrical revolutions and mechanical revolutions. For a motor with one pole pair, one mechanical revolution is equivalent to one electrical revolution. For a motor with npp pole pairs, one mechanical revolution is equivalent to npp electrical revolutions, with n = 1, 2, 3, 4, ....

## 3.5.8.1 Number of Pole Pairs of a Motor

Some define the number of poles NP instead of number of pole pairs NPP for a motor, which results in a factor of two that might cause confusion. For the TMC4671, we use NPP number of pole pairs.

## 3.5.8.2 Number of Encoder Positions per Revolution

Some encoder vendors give the number of lines per revolution (LPR) or just named line count (LC) as encoder parameter. Line count and positions per revolution might differ by a factor of four. This is because of the quadrature encoding - A signal and B signal with phase shift - that give four positions per

For the encoder, the number of positions per revolution (PPR) is an essential parameter. The number of positions per revolution is essential for the FOC.


line, enabling the determination of the direction of revolution. Some encoder vendors associate counts per revolution (CPR) or pulses per revolution associated to PPR acronym.

The TMC4671 uses Positions Per Revolution (PPR) as encoder parameter.

## 3.5.9 Proportional Integral (PI) Controllers for Closed Loop Current Control

Last but not least, two PI controllers are required for the FOC. The TMC4671 is equipped with two PI controllers - one for control of torque generating current I\_Q and one to control current I\_D to zero.

## 3.5.10 Pulse Width Modulation (PWM) and Space Vector Pulse Width Modulation (SVPWM)

With this, the TMC4671 is advanced compared to software solutions where PWM and SVPM configuration of CPU internal peripherals normally needs settings of many parameters.

The PWM power stage is a must-have for energy efficient motor control. The PWM engine of the TMC4671 just needs a couple of parameters to set PWM frequency fPWM and switching pauses for both high side switches tBBM\_H and low side switches tBBM\_L. Some control bits are for the programming of power switch polarities for maximum flexibility in the selection in gate drivers for the power MOS-FETs. An additional control bit selects SVPWM on or off. The TMC4671 allows for change of PWM frequency by a single parameter during operation.


120°

W

240°

90°

## 3.5.11 Orientations, Models of Motors, and Coordinate Transformations

The actual magnetic axis of the stator - formed by the motor coils - is determined by measurement of the coil currents.

The orientation of magnetic axes (U, V, W for FOC3 resp. X, Y for FOC2) is essential for the FOC together with the relative orientation of the rotor. Here, the rotor is modeled by a bar magnet with one pole pair (n\_pole\_pairs = 1) with magnetic axis in north-south direction.

The actual magnetic axis of the rotor is determined by incremental encoder or by Hall sensors. Incremental encoders need an initialization of orientation, where Hall sensors give an absolute orientation, but with low resolution. A combination of Hall sensor and incremental encoder is useful for start-up initialization.


Figure 3: Orientations UVW (FOC3) and XY (FOC2)



Figure 4: Compass Motor Model w/ 3 Phases UVW (FOC3) and Compass Motor Model w/ 2 Phases (FOC2)


x

TMC4671 Servo Controller

## 4 Functional Description

SVPWM

MCU

PWM

PWM

Uv. Uv. Uw

MEASURE

- Pm - BEM

-

Power

PMSM

MOTOR

PMSM

MOTOR

The TMC4671 is a fully integrated controller for field-oriented control (FOC) of either one 3-phase brushless motor (FOC3) or one 2-phase stepper motor (FOC2) or, as well as 1-phase DC motor or voice coil actuator (FOC1). Containing the complete control loop core architecture (position, velocity, torque), the TMC4671 also has the required peripheral interfaces for communication with an application controller, for feedback (digital encoder, analog interpolator encoder, digital Hall with interpolator, analog inputs for current and voltage measurement), and helpful additional IOs. The TMC4671 supports highest control loop speed and PWM frequencies.

The TMC4671 is the building block which takes care of all real-time critical tasks of field-oriented motor control. It decouples the real-time field-oriented motor control and its real-time sub-tasks such as current measurement, real-time sensor signal processing, and real-time PWM signal generation from the user application layer as outlined by figure 5.

Figure 5: Hardware FOC Application Diagram


The Application interface, register bank, ADC engine, encoder engine, FOC torque PI controller, velocity PI controller, position P controller, and PWM engine make up the TMC4671.

## 4.1 Functional Blocks

Figure 6: Hardware FOC Block Diagram


Hardware-FOC


WRnRD

8 BIT ADDR

40 BIT DATAGRAM

32 DATA

The ADC engine interfaces the integrated ADC channels and maps raw ADC values to signed 16 bit (s16) values for the inner FOC current control loop based on programmable offset and scaling factors. The FOC torque PI controller forms the inner base component including required transformations (Clark, Park, inverse Park, inverse Clark). All functional blocks are pure hardware.

The TMC4671 is equipped with an SPI slave user interface for access to all registers of the TMC4671. The SPI slave user interface is the main application interface.

## 4.2 Communication Interfaces

An additional UART interface is intended for system setup. With that interface, the user can access all registers of the TMC4671 in parallel to the application accessing them via the SPI communication interface - via the user's firmware or via evaluation boards and the TMCL-IDE. The data format of the UART interface is similar to the SPI communication interface - SPI 40 bit datagrams sent to the TMC4671 and SPI 40 bit datagrams received by the MCU vs. five bytes sent via UART and five bytes received via UART. Sending a burst of different real-time data for visualization and analysis via the TMCL-IDE can be triggered using special datagrams. With that, the user can set up an embedded application together with the TMCL-IDE, without having to write a complex set of visualization and analysis functions. The user can focus on its application.

The TMC4671 is also equipped with an additional SPI master interface (TRINAMIC Real-time Monitoring Interface, DBGSPI) for high-speed visualization of real-time data together with the TMCL-IDE.

## 4.2.1 SPI Slave User Interface

- The MSB (bit#39) is sent first. The LSB (bit#0) is sent last.

TheSPIoftheTMC4671fortheuserapplicationhasaneasycommandandcontrolstructure. TheTMC4671 user SPI acts as a slave. The SPI datagram length is 40 bit with a clock rate up to 8 MHz (1 MHz for the TMC4671-ES).

- The MSB (bit#39) is the WRITE\_notREAD (WRnRD) bit.
- Bits (bit#31) to (bit#0) are 32 data bits.
- The bits (bit#39 to bit#32) are the address bits (ADDR).

The SPI of the TMC4671 immediately responses within the actual SPI datagram on read and write for ease-of-use communication and uses SPI mode 3 with CPOL = 1 and CPHA = 1.


Figure 7: SPI Datagram Structure

A simple SPI datagram example:

```
0x81000000000   // 1st write 0x00000000 into address 0x01 (CHIPINFO_ADDR)
         0x0000000000   // 2nd read register 0x00 (CHIPINFO_DATA), returns 0x34363731 <=> ACSII "4671"

```


nSCS

SCK

MOSI

MISO

·tac m tcc* tcL

- tc bit39

bit38

X

tcH →* cc x bito


Figure 8: SPI Timing

| Parameter                                          | Symbol       |   Min |   Typ |   Max | Unit   |
|----------------------------------------------------|--------------|-------|-------|-------|--------|
| SCK valid before or after change of nSCS           | t CC         |  62.5 |       |       | ns     |
| nSCS high time                                     | t CSH        |  62.5 |       |       | ns     |
| nSCS low time                                      | t CSL        |  62.5 |       |       | ns     |
| SCK high time                                      | t CH         |  62.5 |       |       | ns     |
| SCK low time                                       | t CL         |  62.5 |       |       | ns     |
| tSCKpause time after read address byte             | t SCKpause   | 500   |       |       | ns     |
| SCK frequency with tSCKpause after write ad- dress | f SCKpauseWR |       |       |     8 | MHz    |
| SCK frequency for write access without pause       | f SCKwr      |       |       |     8 | MHz    |
| SCK frequency with tSCKpause after read address    | f SCKpauseRD |       |       |     8 | MHz    |
| SCK frequency for read access without tSCKpause    | f SCKrd      |       |       |     2 | MHz    |
| MOSI setup time before rising edge of SCK          | t DU         |  62.5 |       |       | ns     |
| MOSI hold time after falling edge of SCK           | t DH         |  62.5 |       |       | ns     |
| MISO data valid time after falling edge of SCK     | t DO         |       |    20 |       | ns     |

Characteristics, fCLK = 25MHz

Table 2: SPI Timing Parameter

SPI Interface Timing

·


nSCS L

nSCS L

SCK

MOSI

MOSI

MISO

MISO

READ ADDR

WRITE ADDR

## Info

DATA[31...24]

DATA[23...16]

DATA[15...8]

DATA[7..0]

DATA[7...0]

DATA[7..0]

tPAUSE |

DATA[31...24]

DATA[23.16]

DATA[15...8]

SPI write access can be performed up to 8 MHz SPI clock frequency. SPI read access can be performed up to 8 MHz SPI clock frequency if a pause of at least 500 ns is inserted after transfer of the address byte of the SPI datagram. Without a pause of 500 ns after address byte, SPI read access can be performed up to 2 MHz SPI clock frequency.


Figure 10: SPI Timing of Read Access with pause (tPAUSE) of 500 ns with fSCK up to 8MHz.


+Vcc

1

## 4.2.2 TRINAMIC Real-Time Monitoring Interface (SPI Master)

The TRINAMIC Real-Time Monitoring Interface (RTMI, SPI Master) is an additional fast interface enabling real-time identification of motor and system parameters. The user can check configuration and access registers in the TMC4671 via the TMCL-IDE with its build-in configuration wizards for FOC setup in parallel to the user firmware. TRINAMIC provides a Monitoring Adapter to access the interface, which connects easily to a single 10 pin high density connector (Type: Hirose DF20F-10DP-1V) on the user's PCB or on the evaluation board. If the interface is not needed, pins can be left open or can be used as GPIOs according to the specification. The connector needs to be placed near the TMC4671. Its assignment is pictured in figure 11.


Figure 11: Connector for Real-Time Monitoring Interface (Connector Type: Hirose DF20F-10DP-1V)


## 4.2.3 UART Interface

The UART interface is a simple three pin (GND, RxD, TxD) 3.3V UART interface with up to 3 Mbit/s transfer speed with one start bit, eight data bits, one stop bit, and no parity bits (1N8). The default speed is 9600 bps. Other supported speeds are 115200 bps, 921600 bps, and 3000000 bps. The speed must be changed manually in register 0x79 UART\_BPS.

Info

The baudrates must be entered as hexadecimal numbers. Table 3 lists the register value and its corresponding baudrate.

Value of register 0x79

selected baudrate

Table 3: Possible baudrates and corresponding values for register 0x79

| 0x00009600   | 9600 bps    |
|--------------|-------------|
| 0x00115200   | 115200 bps  |
| 0x00921600   | 921600 bps  |
| 0x03000000   | 3000000 bps |

An UART datagram consists of five bytes - similar to the datagrams of the SPI. In contrast to SPI, the UART interface has a time out feature. So, the five bytes of a UART datagram need to be send within one second. A pause of sending more than one second causes a time out and sets the UART protocol handler back into IDLE state. In other words, waiting for more than one second in sending via UART ensures that the UART protocol handler is in IDLE state.

With an 3.3V-UART-to-USB adapter cable (e.g. FTDI TTL-232R-RPi), the user can use the full maximum data rate. The UART port enables In-System-Setup-Support by multiple-ported register access.

A simple UART example (similar to the simple SPI example):

```
0x81	0x00	0x00	0x00	0x00	// 1st write 0x00000000 into address 0x01 (CHIPINFO_ADDR)
	0x00	0x00	0x00	0x00	0x00	// 2nd read register 0x00 (CHIPINFO_DATA), returns 0x34363731
```

WhyUARTInterface? It might become necessary during the system setup phase to simply access some internal registers without disturbing the application, without changing the actual user application software, and without adding additional debugging code that might disturb the application software itself. The UART enables this supporting function. In addition, it also enables easy access for monitoring purposes with its very simple and direct five byte protocol. The UART interface is available to write periodically positions into the TMC4671 via an external CPU used as a protocol translator to enable absolute encoders for the TMC4671.

Info

The UART-write response of the TMC4671 depicted in figure 13 does not contain any useful information. It is only used to signal that the IC has received and processed the write datagram sent by the master.


8 BIT ADDR BYTE#S

8 BIT ADDR BYTE#S

7 BIT ADDR

7 BIT ADDR

40 BIT DATAGRAM (UART) to TMC4671

40 BIT DATAGRAM (UART) to TMC4671

MSB DATA BYTE#4

DATA BYTE#3

DATA BYTE#2

LSB DATA BYTE#1

MSB DATA BYTE#4

DATA BYTE#3

DATA BYTE#2

LSB DATA BYTE#1

40 BIT DATAGRAM (UART) READ response from TMC4671

MSB DATA BYTENA

DATA BYTE#3

DATA BYTE#2

8 BIT ADDR BYTE#S MSB DATA BYTE#4 DATA BYTE#3

8 BIT ADDR BYTE#S

LSB DATA BYTE#1

Figure 12: UART Read Datagram (TMC4671 register read via UART)


Figure 13: UART Write Datagram (TMC4671 register write via UART)


## 4.2.4 Step/Direction Interface

The user can manipulate the target position via the step direction interface. It can be enabled by setting the STEP\_WIDTH (s32) register to a proper step width. The power-on default value of STEP\_WIDTH is 0 that causes position target update with 0 step width that is no stepping. With STEP\_WIDTH = 0 each step pulse on STEP input causes incrementing or decrementing of target position depending on polarity of DIR input. For positive STEP\_WIDTH, DIR = 0 causes incrementing and the DIR = 1 causes decrementing of the target position. For negative STEP\_WIDTH, DIR = 0 causes decrementing and DIR = 1 causes incrementing of the target position. This is because the STEP\_WIDTH is represented as a signed number.

## 4.2.5 Single Pin Interface

glyph[negationslash]

The TMC4671 can be operated in Motion Modes in which the main target value is calculated from either a PWM input signal on PIN PWM\_I or by analog input to AGPI\_A.

Number

Motion Mode

Using PWM\_I or AGPI\_A

|   0 | Stopped Mode       | no   |
|-----|--------------------|------|
|   1 | Torque Mode        | no   |
|   2 | Velocity Mode      | no   |
|   3 | Position Mode      | no   |
|   4 | PRBS Flux Mode     | no   |
|   5 | PRBS Torque Mode   | no   |
|   6 | PRBS Velocity Mode | no   |


8 BIT ADDR BYTE#5

WRnRD

7 BIT ADDR

MSB DATA BYTE#

DATA BYTE#3

DATA BYTE#2

LSB DATA BYTE#1

Number

Motion Mode

Using PWM\_I or AGPI\_A

Table 4: Single Pin Interface Motion Modes

|   7 | PRBS Position Mode   | no     |
|-----|----------------------|--------|
|   8 | UQ UD Ext Mode       | no     |
|   9 | (reserved)           | no     |
|  10 | AGPI_A Torque Mode   | AGPI_A |
|  11 | AGPI_A Velocity Mode | AGPI_A |
|  12 | AGPI_A Position Mode | AGPI_A |
|  13 | PWM_I Torque Mode    | PWM_I  |
|  14 | PWM_I Velocity Mode  | PWM_I  |
|  15 | PWM_I Position Mode  | PWM_I  |

Registers SINGLE\_PIN\_IF\_OFFSET and SINGLE\_PIN\_IF\_SCALE can be used to scale the value to desired range. In case of the PWM input, a permanent low input signal or permanent high signal is treated as input error and chosen target value is set to zero.

A duty cycle of 50% equals an input value of 32768. With the offset and scaling factors it can be mapped to desired range.

Register SINGLE\_PIN\_IF\_CFG configures the length of a digital filter for the PWM\_I signal. Spikes on the signal can be thereby suppressed. Bit 0 in register SINGLE\_PIN\_IF\_STATUS is set high when PWM\_I is constant low, Bit 1 is set high when the PWM\_I is constant high. Writing to this register resets these flags. Maximum PWM period of the PWM signal must be 65000 x 40ns. The calculation of the normalized duty cycle is started on the rising edge of PWM\_I. The PWM frequency needs to be constant as big variations (tolerance of 4 us in PWM period) in the PWM frequency are treated as error.

## 4.2.6 GPIO Interface

The TMC4671 has eight GPIO-pins that are arranged in group A (GPIO 0 to 3) and group B (GPIO 4 to 7). These pins can be configured using bits 0 to 6 of the register GPIO\_dsADCI\_CONFIG (0x7B). The configurations include RTMI, GPI or GPO as well as clock signals, in and out, for external delta sigma modulators. Groups A and B can individually be configured as in or outputs. Single pins within these groups can not be individually configured. Bits 16 to 19 set the GPO values for group A and bits 20 to 23 set the GPO values for group B. If configured as GPIs bits 24 to 27 display the input on group A whereas bits 28 to 31 display the input on the group B GPIs.

GPIO\_dsADCI\_CONFIG (bits 6 to 0)

Configured as group A

group B

| xxxxxx0 b   | RTMI   | 0: Z   | 4: SCK   |
|-------------|--------|--------|----------|
|             |        | 1: Z   | 5: MOSI  |
|             |        | 2: Z   | 6: MISO  |
|             |        | 3: /CS | 7: TRG   |
| xx11001 b   | GPIO   | GPO    | GPO      |
| xx00001 b   | GPIO   | GPI    | GPI      |
| xx01001 b   | GPIO   | GPO    | GPI      |
| xx10001 b   | GPIO   | GPI    | GPO      |


## Info

GPIO\_dsADCI\_CONFIG (bits 6 to 0)

Configured as group A

Table 5: GPIO Configuration Overview with 'x' as don't care

| 11xx111 b   | Delta Sigma ADC   | MCLK_out     | MCLK_out                |
|-------------|-------------------|--------------|-------------------------|
|             |                   | 0: ADCI0     | 4: ADCAGPI_B 5: AENC_UX |
|             |                   | 1: ADCI1     |                         |
|             |                   | 2: ADCVM     | 6: AENC_VN              |
|             |                   | 3: ADCAGPI_A | 7: AENC_WY              |
| 00xx111 b   | Delta Sigma ADC   | MCLK_in      | MCLK_in                 |
|             |                   | 0: ADCI0     | 4: ADCAGPI_B            |
|             |                   | 1: ADCI1     | 5: AENC_UX              |
|             |                   | 2: ADCVM     | 6: AENC_VN              |
|             |                   | 3: ADCAGPI_A | 7: AENC_WY              |

WhentheRTMI-option is selected it is not possible to use the GPIOs and the other way around. On default the RTMI-Mode is chosen and the unused GPIOs 0,1 and 2 are configured as inputs on high impedance Z.

In addition, the only possible Delta Sigma ADC configurations are the ones listed in table 5.

## 4.3 Numerical Representation, Electrical Angle, Mechanical Angle, and Pole Pairs

The TMC4671 uses different numerical representations for different parameters, measured values, and interim results. The terms electrical angle PHI\_E, mechanical angle PHI\_M, and number of pole pairs (N\_POLE\_PAIRS) of the motor are important for setup of FOC. This section describes the different numerical representations of parameters and terms.

## 4.3.1 Numerical Representation

The TMC4671 uses signed and unsigned values of different lengths and fixed point representations for parameters that require a non-integer granularity.

Symbol

Description

Table 6: Numerical Representations

| u16   | unsigned 16 bit value                                                     | 0           | 65535                 |
|-------|---------------------------------------------------------------------------|-------------|-----------------------|
| s16   | signed 16 bit values, 2'th complement                                     | -32767      | 32767                 |
| u32   | unsigned 32 bit value                                                     | 0           | 2 32 = 4294967296     |
| s32   | signed 32 bit values, 2'th complement                                     | -2147483647 | 2 31 - 1 = 2147483647 |
| q8.8  | signed fix point value with 8 bit integer part and 8 bit fractional part  | -32767/256  | 32767/256             |
| q4.12 | signed fix point value with 4 bit integer part and 12 bit fractional part | -32767/4096 | 32767/4096            |

Min

Max


group B

## Info

Two's complement of n bit is -2 ( n -1) . . . -2 ( n -1) -1 . To avoid unwanted overflow, the range is clipped to -2 ( n -1) +1 . . . -2 ( n -1) -1 .

Because the zero is interpreted as a positive number for 2'th complement representation of integer n bit number, the smallest negative number is -2 ( n -1) where the largest positive number is 2 ( n -1) -1 . Using the smallest negative number -2 ( n -1) might cause critical underflow or overflow. Internal clipping takes this into account by mapping -2 ( n -1) to -2 ( n -1) +1 .

Hexadecimal Value u16

s16

q8.8

Table 7: Examples of u16, s16, q8.8, q4.12

| 0x0000 h   |     0 |      0 | 0.0          | 0.0           |
|------------|-------|--------|--------------|---------------|
| 0x0001 h   |     1 |      1 | 1 / 256      | 1 / 4096      |
| 0x0002 h   |     2 |      2 | 2 / 256      | 2 / 4096      |
| 0x0080 h   |   128 |    128 | 0.5          | 0.03125       |
| 0x0100 h   |   256 |    256 | 1.0          | 0.0625        |
| 0x0200 h   |   512 |    512 | 2.0          | 0.125         |
| 0x3FFF h   | 16383 |  16383 | 16383 / 256  | 16383 / 4096  |
| 0x5A81 h   | 23169 |  23169 | 23169 / 256  | 23169 / 4096  |
| 0x7FFF h   | 32767 |  32767 | 32767 / 256  | 32767 / 4096  |
| 0x8000 h   | 32768 | -32768 | -32768 / 256 | -32768 / 4096 |
| 0x8001 h   | 32769 | -32767 | -32767 / 256 | -32767 / 4096 |
| 0x8002 h   | 32770 | -32766 | -32766 / 256 | -32766 / 4096 |
| 0xC001 h   | 49153 | -16383 | -16383 / 256 | -16383 / 4096 |
| 0xFFFE h   | 65534 |     -2 | -2 / 256     | -2 / 4096     |
| 0xFFFF h   | 65535 |     -1 | -1 / 256     | -1 / 4096     |

The q8.8 and q4.12 are used for P and I parameters which are positive numbers. Note that q8.8 and q4.12 are used as signed numbers. This is because theses values are multiplied with signed error values resp. error integral values.

## 4.3.2 N\_POLE\_PAIRS, PHI\_E, PHI\_M

A motor with one (1) pole pair turns once for each electrical period. A motor with two (2) pole pairs turns once for every two electrical periods. A motor with three (3) pole pairs turns once for every three electrical periods. A motor with four pole (4) pairs turns once for every four electrical periods.

The parameter N\_POLE\_PAIRS defines the factor between electrical angle PHI\_E and mechanical angle PHI\_M of a motor (pls. refer figure 14).

Theelectrical angle PHI\_E is relevant for the commutation of the motor. It is relevant for the torque control of the inner FOC loop.


q4.12

1 (2)

$$P H I _ { E } = P H I _ { - } M \cdot N _ { - } P O L E _ { \text {PAIRS} }$$

The mechanical angle PHI\_M is primarily relevant for velocity control and for positioning. This is because one wants to control the motor speed in terms of mechanical turns and not in terms of electrical turns.

$$P H I _ { \_ } M = P H I _ { \_ } E / N _ { \_ } P O L E _ { \_ } P A I R S$$

Different encoders give different kinds of position angles. Digital Hall sensors normally give the electrical position PHI\_E that can be used for commutation. Analog encoders give - depending on their resolution angles that have to be scaled first to mechanical angles PHI\_M and to electrical angles PHI\_E for commutation.

Figure 14: N\_POLE\_PAIRS - Number of Pole Pairs (Number of Poles)


## 4.3.3 Numerical Representation of Angles PHI

Electrical angles and mechanical angles are represented as 16 bit integer values. One full revolution of 360deg is equivalent to 2 16 = 65536 steps. Any position coming from a sensor is mapped to this integer range. Adding an offset of PHI\_OFFSET causes a rotation of an angle PHI\_OFFSET / 2 16 . Subtraction of an offset causes a rotation of an angle PHI\_OFFSET in opposite direction.


Ox7FFF

0x8000

180°

-180°

Y

0x4000

270°

OxBFFF

T 0x3FFF

Figure 15: Integer Representation of Angles as 16 Bit signed (s16) resp. 16 Bit unsigned (u16)


Hexadecimal Value u16

s16

PHI[°]

Table 8: Examples of u16, s16, q8.8

|          |       |        |   u16 |   s16 |
|----------|-------|--------|-------|-------|
| 0x0000 h |     0 |      0 |     0 |     0 |
| 0x1555 h |  5461 |   5461 |    30 |    30 |
| 0x2AAA h | 10922 |  10922 |    60 |    60 |
| 0x4000 h | 16384 |  16384 |    90 |    90 |
| 0x5555 h | 21845 |  21845 |   120 |   120 |
| 0x6AAA h | 27306 |  27768 |   150 |   150 |
| 0x8000 h | 32768 | -32768 |   180 |  -180 |
| 0x9555 h | 38229 | -27307 |   210 |  -150 |
| 0xAAAA h | 43690 | -21846 |   240 |  -120 |
| 0xC000 h | 49152 | -16384 |   270 |   -90 |
| 0xD555 h | 54613 | -10923 |   300 |   -60 |
| 0xEAAA h | 60074 |  -5462 |   330 |   -30 |

The option of adding an offset is for adjustment of angle shift between the motor and stator and the rotor and encoder. Finally, the relative orientations between the motor and stator and the rotor and encoder can be adjusted by just one offset. Alternatively, one can set the counter position of an incremental encoder to zero on initial position. For absolute encoders, one needs to use the offset to set an initial position.


PHI[°]

## 4.4 ADC Engine

The ADC engine controls the sampling, selection, scaling and offset correction of different available ADC channels. Two ADC channels are for phase current measurement, three ADC channels are for analog Hall signals or for analog sin-cos-encoder, one ADC channel is for optional measurement of the motor spupply voltage, two additional ADC channals are general purpose where one general purpose analog input can be used as analog target value by the single pin interface.

## 4.4.1 ADC current sensing channels ADC\_I1 and ADC\_I0

The ADC channels (ADC\_I0\_POS, ADC\_I0\_NEG, ADC\_I1\_POS, ADC\_I1\_NEG) are for current sensing in differential input configuration. In differential configuration, the ADC\_I0\_POS and ADC\_I0\_POS are the inputs for the sense amplifier output signals where ADC\_I1\_NEG and ADC\_I0\_NEG) are for the zero current sensing reference of the sense amplifiers. In single ended configuration, the ADC\_I0\_POS and ADC\_I0\_POS are the inputs for the sense amplifier output signals where ADC\_I1\_NEG and ADC\_I0\_NEG) are internally connected to ground. The third current channel ADC\_I2 as required for three phase FOC is calculated using Kirchhoff's law ADC\_I2 = - (ADC\_I1 + ADC\_I0).

Info

ADC\_I0\_POS, ADC\_I0\_NEG, ADC\_I1\_POS, ADC\_I1\_NEG are low voltage analog inputs and must not directly connected to in-line sense resistors. The TMC4671 requires external dfferential motor supply common mode range current sensing amplifiers for in-line current sensing.

## 4.4.2 ADC for analog Hall signals or analog sin-cos-encoders AENC\_UX, AENC\_VN, AENC\_WY

The three channels AENC\_UX, AENC\_VN, AENC\_WY are for three phase analog sine (with +/-120° phase shift) wave Hall signals. The Signals AENC\_UX and AENC\_WY are for two phase analog sine wave and cosin wave Hall signals. The Signals AENC\_UX and AENC\_WY are for analog sin-cos-encoder. The AENC\_VN is for an optional zero pulse channel of sin-cos-encoders. The AENC\_VN is available for read out by the application software but it is not hardware handled by the TMC4671 for position zerroing.

For analog Hall and for analog encoder, the ADC engine has three disserential input channles (AENC\_UX\_POS, AENC\_UX\_NEG),(AENC\_VN\_POS,AENC\_VN\_NEG),andAENC\_WY\_POS,AENC\_WY\_NEG).Theanalogencoder ADC inputs can be configured single ended (AENC\_UX\_POS, AENC\_VN\_POS, AENC\_WY\_POS) with negative inputs (AENC\_UX\_NEG, AENC\_VN\_NEG, AENC\_WY\_NEG) internally connected to ground.

For long analog signal lines, it might be necessary to use external differential receivers with twisted pair line termination resistors to drive the single ended analog encoder inputs of the TMC4671.

## 4.4.3 ADC supply voltage measurement ADC\_VM

The ADC channel for measurement of supply voltage (ADC\_VM) and is associated with the brake chopper. TheADC\_VMisavailableasrawvalueonlywithoutdigitalscaling. This is because it is not directly processed by the FOC engine.

Info

ADC\_VM must be scaled down electrically by voltage divider to the allowed voltage range, and might require additional supply voltage spike protection.


## 4.4.4 ADC\_VM for Brake Choppper

The ADC\_VM is available as input for optional brake chopper as raw value u16. The brake chopper thresholds have to be set as absolute u16 values to activate and deactivate the brake chopper output depending on the ADC\_VM value.

## 4.4.5 ADC EXT register option

The user can write ADC values into the ADC\_EXT registers of the register bank from external sources or for evaluation purposes. These values can be selected as raw current ADC values by selection. ADC\_EXT registers are primarily intended for test purposes as optional inputs for external current measurement sources.

## 4.4.6 ADC general purpose analog inputs AGPI\_A and AGPI\_B

Two general purpose ADC channels are single-ended analog inputs (AGPI\_A, AGPI\_B). The general purpose analog ADC inputs AGPI\_A and AGPI\_B are available as raw values only without digital scaling. This is because these values are not directly processed by the FOC engine. These general purpose analog inputs (AGPI) are intended to monitor analog voltage signals representing MOSFET temperature or motor temperature. They are two additional ADC channels for the user. Optional, the AGPI\_A is availabe as analog target value signal.

## 4.4.7 ADC RAW values

The sampled raw ADC values are available for read out by the user. This is important during the system setup phase to determine offset and scaling factors.

## 4.4.8 ADC\_SCALE and ADC\_OFFSET

The FOC engine expects offset corrected ADC current values scaled to the used 16 bit (s16) fixed point representation. The integrated scaler and offset compensator maps raw ADC samples of current measurement channels to 16 bit two's complement values (s16). While the offset is compensated by subtraction, the offset is represented as an unsigned value. The scaling value is signed to compensate wrong measurement direction. The s16 scaled ADC values are available for read out from the register (ADC\_I1, ADC\_I0) resp. (AENC\_UX, AENC\_VN, AENC\_WY) by the user.

Info

Wrong scaling factors (ADC\_SCALE) or wrong offsets (ADC\_OFFSET) might cause damages when the FOC is active. Integrated hardware limiters allow protection especially in the setup phase when using careful limits.

## 4.4.9 ADC Gain Factors for Real World Values

Each ADC channel of the TMC4671 has an individual gain factor determined by its associated chain of gain factors and by digital scaling factors if available for an ADC channel. ADC register values are either 16 bit unsigned vaulues (u16) or 16 bit signed vaules (s16). With gain factors one can calculate ADC values as real world values if required.


Gainfactors IgainADC for ADC current values are typical in units [ A/LSB ] or [ mA/LSB ] . Gainfactors UgainADC for ADC voltage values are typical in units [ V/LSB ] or [ mV/LSB ] .

$$\ A D C { \text {measuredCurrent} } [ A ] \ = \ \L i g a i n { \ A D C { [ A / L S B ] } \ * \ \ A D C { \text {CURRENT} } { S 1 6 } }$$

$$\ A D C { \text {measuredVolatility} } [ V ] \ = \ U g a i n A D C { [ V / L S B ] } \ * \ A D C { \text {VOLTEAGE} } { S 1 6 }$$

$$\ A D C { \text {measuredVoltage} } [ V ] \ = \ U g a i n A D C { \left | V / L S \right | } \ \ast \ A D C { \text {VOLTAGE} } \, U 1 6$$

## 4.4.10 Internal Delta Sigma ADCs

Due to high oversampling, the analog input front-end is easier to implement than for successive approximation register ADCs as anti aliasing filters can be chosen to a much higher cutoff frequency. The ADC Engine processes all ADC channels in parallel hardware - avoiding phase shifts between the channels compared to ADC channels integrated in MCUs.

The TMC4671 is equipped with internal delta sigma ADCs for current measurement, supply voltage measurement, analog GPIs and analog encoder signal measurement. Delta sigma ADCs, as integrated within the TMC4671, together with programmable digital filters are flexible in parameterizing concerning resolution vs. speed. The advantage of delta sigma ADCs is that the user can adjust measurement from lower speed with higher resolution to higher speed with lower resolution. This fits with motor control application. Higher resolution is required for low speed signals, while lower resolution satisfies the needs for high speed signals.

## 4.4.11 Internal Delta Sigma ADC Input Stage Configuration

ADC channels can be configured either as differential ended analog inputs (ADC\_I0, ADC\_I1, AENC\_UX, AENC\_VN, AENC\_WY) or as single ended analog inputs (ADC\_VM, AGPI\_A, AGPI\_B). Additionally, the ADC all channels can be set to fixed voltages (0V, VREF/4, VREF/2, 3*VREF/4) for calibrations purposes.

STAGE\_CFG(n+2:n)

CONFIGURATION

DESCRIPTION

COMMENT

Table 9: Delta Sigma ( ∆Σ ) ADC Input Stage Configurations

|   0 | INP vs. INN   | differential mode                 | default configuration        |
|-----|---------------|-----------------------------------|------------------------------|
|   1 | GND vs. INN   | single ended negative INN vs. GND | (for test purposes only)     |
|   2 | VDD/4         | 25% ADC reference voltage         | calibration aid              |
|   3 | 3*VDD/4       | 75% ADC reference voltage         | calibration aid              |
|   4 | INP vs. GND   | single ended mode INP vs. GND     | (half voltage range, offset) |
|   5 | VDD/2         | 50% ADC reference voltage         | calibration aid              |
|   6 | VDD/4         | 25% ADC reference voltage         | (redundant configuration)    |
|   7 | 3*VDD/4       | 75% ADC reference voltage         | (redundant configuration)    |

The three bit vector ADC\_STAGES\_CFG(n+2:n) is part of the DS\_ANALOG\_INPUT\_STAGE\_CFG(31:0) with n = 0, 4, 8, 12, 16, 20, 24, 28 for the eigth delta sigma ADC channels. DS\_ANALOG\_INPUT\_STAGE\_CFG


ADCRAw[u16]

65535 —

configures the associated delta sigma ADC input stages according to table 17. For association of the bit position (bit n+2 to bit n) refere register bank section 7.2.

32768 — 50%

16384 - 25%...

of

-1.25

32768 — 50%

| STAGE_CFG(2:0)   | ADC_I0      | sense voltage of current I0              |
|------------------|-------------|------------------------------------------|
| STAGE_CFG(6:4)   | ADC_I1      | sense voltage of current I1              |
| STAGE_CFG(9:8)   | ADC_VM      | down divided supply voltage              |
| STAGE_CFG(10)    | '1'         | fixed for ADC_VM (STAGE_CFG=4,5,6,7)     |
| STAGE_CFG(13:12) | ADC_AGPI_A  | general purpose analog input A           |
| STAGE_CFG(14)    | '1'         | fixed for ADC_AGPI_A (STAGE_CFG=4,5,6,7) |
| STAGE_CFG(17:16) | ADC_AGPI_B  | general purpose analog input B           |
| STAGE_CFG(18)    | '1'         | fixed for ADC_AGPI_B (STAGE_CFG=4,5,6,7) |
| STAGE_CFG(22:20) | ADC_AENC_UX | analog Hall UX / analog encoder COS      |
| STAGE_CFG(26:24) | ADC_AENC_VN | analog Hall V / analog encoder N         |
| STAGE_CFG(30:28) | ADC_AENC_WY | analog Hall WY / analog encoder SIN      |

-2.5

Table 10: Delta Sigma ( ∆Σ ) ADC Input Stage Configurations



Figure 16: Input Voltage Ranges of internal Delta Sigma ADC Channels)


STAGE\_CFG(n+2:n)

ADC channel function

ADCRAw[416]

Figure 16 illustrates typical relation between input voltage and corresponding raw ADC output. For differential operation the input range between 25% and 75% corresponds to voltage values between 1.25V to 3.75V. This is the recommended operation area of the ADC. Below 25% and above 75% the ADC shows significant non-linearity due to the Delta Sigma measurement principle.

In single ended operation the recommended input range starts at 0V and ends at 1.25V. Measurement below GND might be distorted and is not recommended.

Info

Due to manufacturing tolerances calibration of offset and amplitude is always recommended. Please also consider stability of the reference voltage.

## 4.4.12 External Delta Sigma ADCs

The delta sigma front-end of the ADC engine supports external delta sigma modulators to enable isolated delta sigma modulators for the TMC4671. Additionally, the delta sigma front-end supports low-cost comparators together with two resistors and one capacitor (R-C-R-CMP) forming first order delta sigma modulators, as generic analog front-end for pure digital variants of the TMC4671 core.

## 4.4.13 ADC Group A and ADC Group B

ADC channels of the TMC4671 are grouped into two groups, to enable different sample rates for two groups of analog signals if needed. Running both ADC groups with same sampling frequency is recommended for almost all applications. It might be necessary to run its ADC channels of analog encoder with a much higher frequency than the ADC channels for current measurement in case of using a high resolution analog encoder.

## 4.4.14 Delta Sigma Configuration and Timing Configuration

The delta sigma configuration is programmed via MCFG register that selects the mode (internal/external delta sigma modulator with programmable MCLK; delta sigma modulator clock mode (MCLK output, MCLK input, MCLK used as MDAC output with external R-C-R-CMP configuration); delta sigma modulator clock and its polarity; and the polarity of the delta sigma modulator data signal MDAT).

Info

The power-on delta sigma configuration should fit with most applications when using the intergated delta sigma ADCs of the TMC4671. Primarily, the default delta sigma configuration needs to be adapted when using external delta sigma modulators or to select differential ADC input configurations, or in case of enhanced sampling requirenment for high resolution analog encoders.


dsADC\_CONFIG = ANALOG

dsADC\_CONFIG = MCLKO

dsADC\_CONFIG +

dsADC\_CONFIG = MCLKI

dsADC\_CONFIG = MDAC

dsADC

· NC / MCLKO / MCLKI / MDAC

· VIN / MDAT

dsADC\_CONFIG = ANALOG

VIN o

VREF

ADC\_VIN

ADC\_VREF

Figure 17: Delta Sigma ADC Configurations dsADC\_CONFIG (internal: ANALOG vs. external: MCLKO, MCLKI, MDAC)


dsADC\_CONFIG

Description

NC\_MCLKO\_MCLKI\_MDAC

VIN\_MDAT

| ANALOG   | integrated internal ADC mode, VIN_MDAT is analog input VIN                                 | MCLK not connected (NC)   | VIN (analog)       |
|----------|--------------------------------------------------------------------------------------------|---------------------------|--------------------|
| MCLKO    | external dsModulator (e.g. AD7403) with MCLK input driven by MCLKO                         | MCLK output               | MDAT input         |
| MCLKI    | external dsModulator (e.g. AD7400) with MCLK output that drives MCLKI                      | MCLK input                | MDAT input         |
| MDAC     | external dsModulator (e.g. LM339) realized by external comparator CMP with two R and one C | MDAC output (= MCLK out)  | MDAT input for CMP |

Table 11: Delta Sigma ADC Configurations (figure 17), selected with dsADC\_MCFG\_A and dsADC\_MCFG\_B.


register function

Table 12: Registers for Delta Sigma Configuration

| dsADC_MCFG_B   | delta sigma modulator configuration MCFG (ANALOG, MCLKI, MCLKO, MDAC), group B   |
|----------------|----------------------------------------------------------------------------------|
| dsADC_MCFG_A   | delta sigma modulator configuration MCFG (ANALOG, MCLKI, MCLKO, MDAC), group A   |
| dsADC_MCLK_B   | delta sigma modulator clock MCLK, group B                                        |
| dsADC_MCLK_A   | delta sigma modulator clock MCLK, group A                                        |
| dsADC_MDEC_B   | delta sigma decimation parameter MDEC, group B                                   |
| dsADC_MDEC_A   | delta sigma decimation parameter MDEC, group A                                   |

## 4.4.14.1 Timing Configuration MCLK

$$y \text { ICLK} - \text {OOM} I Z , \text { etc. } \text {MCL} \text {K} \text { (Hz)} \Big / f \text {CL} K [ H z ] \\ \text {MCL} K = 2 ^ { 3 1 } \cdot f \text {MCL} K [ H z ] / f \text {CL} K [ H z ]$$

When the programmable MCLK is selected, the MCLK\_A and MCLK\_B parameter registers define the programmable clock frequency fMCLK of the delta sigma modulator clock signal MCLK for delta sigma modulator group A and group B. For a given target delta sigma modulator frequency fMCLK, together with the internal clock frequency fCLK = 100MHz, the MCLK frequency parameter is calculated by

Due to the 32 bit's length of the MCLK frequency parameter, the resulting frequency fMCLK might differ from the desired frequency fMCLK. The back calculation of the resulting frequency fMCLK for a calculated MCLK parameter with 32 bit length is defined by

$$B \text { bit} \, \L C l { N C L } \, \L C l { H } \, \L C l { Z } \, \L C l { H } \, \L C l { Z } \, \L C l { M } \, \L C L K / H \, \L Z \, \L C l { Z } \, \L C l { Z } ^ { 3 1 }$$

The precise programming of the MCLK frequency is primarily intended for external delta sigma modulators to meet given EMI requirements. With that, the user can programm frequencies fMCLK with a resolution better than 0.1 Hz. This advantage concerning EMI might cause trouble when using external delta sigma modulators if they are sensitive to slight frequency alternating. This is not an issue when using external first-order delta sigma modulators based on R-C-R-CMP (e.g. LM339). But for external second-order delta sigma modulators, it is recommended to configure the MCLK parameter for frequencies fMCLK with kHz quantization (e.g. 10,001,000 Hz instead of 10,000,001 Hz).

fMCLK\_target

MCLK

fMCLK\_resulting comment

| 25 MHz   | ✵①✷✵✵✵✵✵✵✵   | 25 MHz             | w/o fMCLK frequency jitter, recommended   |
|----------|--------------|--------------------|-------------------------------------------|
| 20 MHz   | ✵①✶✾✵✵✵✵✵✵   | 20 MHz -468750 Hz  | recommended for ext. ∆Σ modulator         |
| 20 MHz   | ✵①✶✾✾✾✾✾✾✾   | 20 MHz -0.03 Hz    | might be critical for ext. ∆Σ modulator   |
| 12.5 MHz | ✵①✶✵✵✵✵✵✵✵   | 12.5 MHz           | w/o fMCLK frequency jitter, recommended   |
| 10 MHz   | ✵①✵❈❈❈❈❈❈❈   | 10 MHz -0.04 Hz    | might be critical for ext. ∆Σ modulator   |
| 10 MHz   | ✵①✵❈❈✵✵✵✵✵   | 10 MHz -39062.5 Hz | recommended for ext. ∆Σ modulator         |

Table 13: Delta Sigma MCLK Configurations


## 4.4.14.2 Decimation Parameter MDEC

The delta sigma modulator with Sinc3 filter works with best noise reduction performance when the length of the step response time tSINC3 of the Sinc3 filter is equal to the length of the PWM period tPWM = (PWM\_MAXCNT+1) / fPWMCLK = ((PWM\_MAXCNT+1) * 10 ns) of the period. The length of the step function response of a Sinc3 filter is

The high oversampled single bit delta sigma data stream (MDAT) is digitally filtered by Sinc3 filters. To get raw ADC data, the actual digitally filtered values need to be sampled periodically with a lower rate called decimation ratio. The decimation is controlled by parameter MDEC\_A for ADC group A and MDEC\_B for ADC group B. A new ADC\_RAW value is available after MDEC delta sigma pulses of MCLK. As such, the parameters MCLK and MDEC together define the sampling rate of the 16 bit ADC\_RAW values.

$$\ t S I N C { 3 } = ( 3 \cdot ( M D E C - 1 ) + 1 ) \cdot t M C L K$$

$$M D E _ { \text {recommended} } = \frac { \ t P W M } { 3 \cdot \ t M C L K } - 2$$

MDEC25 (25 kHz, 40

fMCLK

tMCLK

|          |        |   µs |   µs |   µs |
|----------|--------|------|------|------|
| 50 MHz   | 20 ns  |  665 |  331 |  165 |
| 25 MHz   | 40 ns  |  331 |  165 |   81 |
| 20 MHz   | 50 ns  |  265 |  131 |   65 |
| 12.5 MHz | 80 ns  |  165 |   81 |   40 |
| 10 MHz   | 100 ns |  131 |   65 |   31 |

)

MDEC50 (50 kHz, 20

)

MDEC100 (100 kHz, 10

Table 14: Optimal Decimation Parameter MDEC (according to equation (13) for different PWM frequencies fPWM (MDEC25 for fPWM=25kHz w/ PWM\_MAXCNT=3999, MDEC50 for fPWM=50kHz w/ PWM\_MAXCNT=1999, MDEC100 for fPWM=100kHz w/ PWM\_MAXCNT=999).

## Info

MDEC parameter can be changed during operation. This enables adaptive adjustment of performance with respect to resolution versus speed on demand.

For most applications, the power-on decimation setting of MDEC should be sufficient.


)

## 4.4.15 Internal Delta Sigma Modulators - Mapping of V\_RAW to ADC\_RAW

Generally, delta sigma modulators work best for a typical input voltage range of 25% V\_MAX ...75% V\_MAX (unsigned 0% ... 100%). For the integrated delta sigma modulators, this input voltage operation range is recommended with V\_MAX = 5V where V\_MAX = 3.3V is possible. The table 15 defines the recommended voltage ranges for both 5V and 3.3V analog supply voltages.

V\_SUPPLY[V]

(V\_MIN[V])

V\_MIN25%[V]

V\_MAX50%[V]

V\_MAX75%[V]

(V\_MAX[V])

Table 15: Recommended input voltage range from V\_MIN25%[V] to V\_MAX75%[V] for internal Delta Sigma Modulators; V\_SUPPLY[V] = 5V is recommended for the analog part of the TMC4671.

|   (3.3) | (0.0)   |   (0.825) |   (1.65) |   (2.75) | (3.3)   |
|---------|---------|-----------|----------|----------|---------|
|       5 | (0.0)   |      1.25 |      2.5 |     3.75 | (5.0)   |

$$V _ { \ } R A W \ = \ \begin{cases} V _ { \ } M A & \text {for} \quad V _ { \ } I N \quad > \ V _ { \ } M A \\ ( V _ { \ } I N - V _ { \ } R E ) & \text {for} \ \ V _ { \ } M I \ < \ ( V _ { \ } I N - V _ { \ } R E ) \ \ < \ V _ { \ } M A \\ V _ { \ } \min & \text {for} \quad V _ { \ } I N \quad < \ V _ { \ } \min \end{cases}$$

The resulting raw ADC value is

$$The resulting raw ADC value is \\ & \quad \ ADC _ { \ } R W = ( 2 ^ { 1 6 } - 1 ) \cdot \frac { V _ { \ } R W } { V _ { \ } \max } \quad \text {for} \quad V _ { \ } M { \ln } { 2 5 } \% [ V ] < V _ { \ } R W < V _ { \ } \max { 7 5 } \% [ V ] .$$

The idealized expression (equation 14) is valid for recommended voltage ranges (table 15) neglecting deviations in linearities. These deviations primarily depend on different impedance on the analog signal path, but also on digital parameterization. Finally, the deviation is quantified in terms of resulting ADC resolution. So, the Delta Sigma ADC engine maps the analog input voltages V\_RAW = V\_IN - V\_REF of voltage range V\_MIN &lt; V\_RAW &lt; V\_MAX to ADC\_RAW values of range { 0 . . . (2 16 ) -1 } &lt; = &gt; { 0 . . . 65535 } &lt; = &gt; 0x0000 . . . 0xFFFF.

Vmin[V]

Vref[V]

Vmax[V]

VIN[V]

DUTY[%]

ADC\_RAW

Table 16: Delta Sigma input voltage mapping of internal Delta Sigma Modulators

|   0.0 |   2.5 |   5.0 | (0.0)   | (0%)   | (0x0000)   |
|-------|-------|-------|---------|--------|------------|
|     0 |   2.5 |     5 | 1.0     | 25%    | 0x4000     |
|     0 |   2.5 |     5 | 2.5     | 50%    | 0x7fff     |
|     0 |   2.5 |     5 | 3.75    | 75%    | 0xC000     |
|     0 |   2.5 |     5 | (5.0)   | (100%) | (0xffff)   |

For calibrating purposes, the input voltage of the delta sigma ADC inputs can be programmed to fixed voltages (25%, 50%, 75% of analog supply voltage) via the associated configuration register DS\_ANALOG\_INPUT\_STAGE\_CFG.


dsADC\_CONFIG = MDAC

VIN o

MDAC

## 4.4.16 External Delta Sigma Modulator Interface

The TMC4671 is equipped with integrated digital filters for extraction of ADC raw values from delta sigma data stream for both internal and external delta sigma modulators. The interface for external delta sigma modulators is intended for external isolated sigma delta modulators, such as AD7401 (with MCLK input driven by TMC4671), or AD7402 (with MCLK output to drive TMC4671). In addition, the external delta sigma interface supports the use of simple comparator with a R-C-R network as external low cost delta sigma modulators (R-C-R-CMP, e.g. LM339).

Info

When selecting the external delta sigma ADC Interface, the high-performance Debug SPI Interface (RTMI) it not available in parallel due to pin sharing. The UART is always available, but with less performance than the RTMI.

Each external delta sigma modulator channel (dsMOD) has two signals (pls. refer figure 17), one dedicated input, and one programmable input/output. The configuration of the external delta sigma modulator interface is defined by programming associated registers. When selecting external delta sigma ADC, the associated analog ADC inputs are configured as digital inputs for the delta sigma signal data stream MDAT.

## 4.4.16.1 External Delta Sigma Modulator Interface - MDAC Configuration

Figure 18: ∆Σ ADC Configuration - MDAC (Comparator-R-C-R as ∆Σ -Modulator)


In the MDAC delta sigma modulator, the delay of the comparator CMP determines the MCLK of the comparator modulator. A capacitor C MCCMP within a range of 100 pF ...1nF fits in most cases. The time constant τ RC should be in a range of 0.1 tCMP ...tCMP of the comparator. The resistors should be in the range of 1K to 10K. The fMAXtyp depends also on the choice of the decimation ratio.

CMP

tCMPtyp

|       |   [ ns ] |   R MCMP [ k Ω] |   R MDAC [ k Ω] |   C MCMP [ pF ] |         |
|-------|----------|-----------------|-----------------|-----------------|---------|
| LM339 |     1000 |               1 |               1 |             100 | 1 MHz   |
| LM339 |     1000 |              10 |              10 |             100 | 100 kHz |
| LM339 |     1000 |             100 |             100 |             100 | 10 kHz  |

fMCLKmaxTYP

Table 17: Delta Sigma R-C-R-CMP Configurations (pls. refer 17)


For external Delta Sigma R-C-R-CMP modulators, one gets the Delta Sigma input voltage mapping according to table 18. The support of low-cost external comparators used as first order delta sigmal modulators is intended as an generic analog interface option for compatibility of the TMC4671 core in case it would be embedded within a pure digital technology environment.

Vmin[V]

Vref[V]

Vmax[V]

VIN[V]

DUTY[%]

ADC\_RAW

| 0.0     | 1.65    | 3.3     | 0.0    | 0%      | 0x0000   |
|---------|---------|---------|--------|---------|----------|
| 0.0     | 1.65    | 3.3     | 0.825  | 25%     | 0x4000   |
| 0.0     | 1.65    | 3.3     | 1.65   | 50%     | 0x7fff   |
| 0.0     | 1.65    | 3.3     | 2.475  | 75%     | 0xC000   |
| 0.0     | 1.65    | 3.3     | 3.3    | 100%    | 0xffff   |
| Vmin[V] | Vref[V] | Vmax[V] | VIN[V] | DUTY[%] | ADC_RAW  |
| 0.0     | 2.5     | 5.0     | 0.0    | 0%      | 0x0000   |
| 0.0     | 2.5     | 5.0     | 1.0    | 25%     | 0x4000   |
| 0.0     | 2.5     | 5.0     | 2.5    | 50%     | 0x7fff   |
| 0.0     | 2.5     | 5.0     | 3.75   | 75%     | 0xC000   |
| 0.0     | 2.5     | 5.0     | 5.0    | 100%    | 0xffff   |

Table 18: Delta Sigma input voltage mapping of external comparator (CMP)


## 4.5 Analog Signal Conditioning

The range of measured coil currents, resp. the measured voltages of sense resistors, needs to be mapped to the valid input voltage range of the delta sigma ADC inputs. This analog preprocessing is the task of the analog signal conditioning.

## 4.5.0.1 Chain of Gains for ADC Raw Values

$$ADC _ { - } R A W = ( I _ { - } S E S \cdot A D C _ { - } G A N ) + A D C _ { - } \text {OFFSET} .$$

An ADC raw value is a result of a chain of gains that determine it. A coil current I\_SENSE flowing through a sense resistor causes a voltage difference according to Ohm's law. Finally, a current is mapped to an ADC raw value

The ADC\_GAIN is a result of a chain of gains with individual signs. The sign of the ADC\_GAIN is positive or negative, depending on the association of connections between sense amplifier inputs and the sense resistor terminals. The ADC\_OFFSET is the result of electrical offsets of the phase current measurement signal path. For the TMC4671, the maximum ADC\_RAW value is ADC\_RAW\_MAX = (2 16 -1) and the minimumADC raw value is ADC\_RAW\_MIN = 0.

Rsense

$$\text {raw value is ADC_RAW_MIN = 0 .} \\ \quad \text {ADC_GAIN} \quad = \quad ( \quad I _ { \ } SENSE_MAX \cdot R _ { \ } SENSE \quad ) \\ \quad \cdot \quad \text {SENSE_AMPLIFYER_GAIN} \\ \quad \cdot \quad ( \quad ADC_RAW_MAX / ADC_U_MAX \quad )$$

Isense

Usense

|   [ m Ω] |   [ A ] |   [ mV ] |   [ V/V ] |   [ A/V ] |        |
|----------|---------|----------|-----------|-----------|--------|
|        5 |      10 |       50 |        20 |        10 | AD8418 |
|       10 |       5 |       50 |        20 |         5 | AD8418 |

GAIN

ADC\_GAIN

Table 19: Example Parameters for ADC\_GAIN

For the FOC, the ADC\_RAW is scaled by the ADC scaler of the TMC4671 together with subtraction of offset to compensate it. Internally, the TMC4671 FOC engine calculates with s16 values. So, the ADC scaling needs to be chosen so that the measured currents fit into the s16 range. With the ADC scaler, the user can chooseascaling with physical units like [ mA ] . Ascaling to [ mA ] covers a current range of -32 A... +32 A with m [ A ] resolution. For higher currents, the user can choose unusual units like centi Ampere [ cA ] covering -327 A... +327 A or deci Ampere -3276 A... +3276 A .

ADC scaler and offset compensators are for mapping raw ADC values to s16 scaled and offset cleaned current measurement values that are adequate for the FOC.

## 4.5.1 FOC3 - Stator Coil Currents I\_U, I\_V, I\_W and associated Voltages U\_U, U\_V, U\_W

For three-phase motors with three terminals U, V, W, the voltage U\_U is in phase with the current I\_U, U\_V is in phase with I\_V, and U\_W is in phase with I\_W according to equations (18) and (19) for FOC3.

The correct association between stator terminal voltages U\_U, U\_V, U\_W and stator coil currents I\_U, I\_V, I\_W is essential for the FOC.


Sense Amplifier

$$U _ { U V W _ { \ } F O C 3 } ( U _ { D } , \phi _ { \L } ) \ = \ \begin{cases} \ U _ { U } ( \phi _ { e } ) = U _ { D } \ \ & \sin ( \phi _ { e } ) \\ \ U _ { V } ( \phi _ { e } ) = U _ { D } \ \ & \sin ( \phi _ { e } + 1 2 0 ^ { \circ } ) \\ \ U _ { W } ( \phi _ { e } ) = U _ { D } \ \ & \sin ( \phi _ { e } - 1 2 0 ^ { \circ } ) \end{cases}$$

$$I _ { U V W _ { \ } F O C 3 ( I _ { D } , \, \phi \, H I _ { E } ) } \ = \ \left \{ \begin{array} { l l } { I _ { U } ( \phi _ { e } ) = I _ { D } } & { \ \cdot \ \sin ( \phi _ { e } ) } \\ { I _ { V } ( \phi _ { e } ) = I _ { D } } & { \ \cdot \ \sin ( \phi _ { e } + 1 2 0 ^ { \circ } ) } \\ { I _ { W } ( \phi _ { e } ) = I _ { D } } & { \ \cdot \ \sin ( \phi _ { e } - 1 2 0 ^ { \circ } ) } \end{array}$$

## 4.5.2 FOC2 - Stepper Coil Currents I\_X, I\_Y and associated Voltages U\_X, U\_Y

For two-phase motors (stepper) with four terminals UX1, VX2, and WY1, Y2, voltage U\_Ux = U\_X1 - U\_X2 is in phase with the measured current I\_X and U\_Wy = U\_Y1 - U\_Y2 is in phase with the measured current I\_Y according to equations (20) and (21) for FOC2.

$$U _ { X Y } \text {FOC} ^ { 2 } \ = \ \begin{cases} \ U _ { X } ( \phi _ { e } ) = U _ { X } \quad \cdot \quad s i n ( \phi _ { e } ) \\ \ U _ { Y } ( \phi _ { e } ) = U _ { Y } \quad \cdot \quad s i n ( \phi _ { e } + 9 0 ^ { o } ) \end{cases}$$

$$I _ { X Y } \bar { \ } F O C 2 \ = \ \left \{ \begin{array} { l l } { I _ { X } ( \phi _ { e } ) = I _ { D } \ \cdot \ \ s i n ( \phi _ { e } ) } \\ { I _ { Y } ( \phi _ { e } ) = I _ { D } \ \cdot \ \ s i n ( \phi _ { e } + 9 0 ^ { o } ) } \end{array}$$

## 4.5.3 FOC1 - DC Motor Coil Current I\_X1, I\_X2, and associated Voltage U\_X1, U\_X2

For DC motor with with two terminals UX1, VX2, voltage U\_X = U\_X1 - U\_X2 is in phase (same sign) with the measured current I\_X. U\_X is in phase (same sign) with the measured current I\_X according to equations (22) and (23) for FOC1.

$$U _ { - } X Y _ { - } F O C 1 \ = \ U _ { X 1 } - V _ { X 2 }$$

$$I _ { - } X Y _ { - } F O C 1 \ = \ I _ { X 1 } \quad$$


ADC Engine

Register Bank

ADC RAW INPUT CHANNEL SELECTOR

· ADC\_10 (IU, IX)

ADC SCALER

ADC\_I0\_RAWH

ADC\_I0\_RAW

ADC\_10

KIRCHHOFF

→ ADC\_10

ADC\_10-

## 4.5.4 ADC Selector &amp; ADC Scaler w/ Offset Correction

- ADC\_10\_SCALE

ADC OUTPUT SELECTOR

→ ADC\_10

ADO\_UX

ADC\_V

ADC\_WY

TheADCselectorselects ADC channels for FOC. The 3-phase FOC uses two ADC channels for measurement and calculates the third channel via Kirchhoff's Law using the scaled and offset-corrected ADC values. The 2-phase FOC just uses two ADC channels because for a 2-phase stepper motor, the two phases are independent from each other.

## Note

The open-loop encoder is useful for setting up ADC channel selection, scaling, and offset by running a motor open-loop.

The FOC23 Engine processes currents as 16 bit signed (s16) values. Raw ADC values are expanded to 16 bit width, regardless of their resolution. With this, each ADC is available for read out as a 16 bit number. The ADC scaler w/ offset correction is for the preprocessing of measured raw current values. It might be used to map to user's own units (e.g. A or mA). For scaling, gains of current amplifiers, reference voltages, and offsets have to be taken into account.

Info

Raw ADC values generally are of 16 bit width, regardless of their real resolution.

- Info The ADC scaler maps raw ADC values to the 16 bit signed (s16) range and centers the values to zero by removing offsets.

Figure 19: ADC Selector &amp; Scaler w/ Offset Correction


ADCoffsets and ADC scalers for the analog current measurement input channels need to be programmed into the associated registers. Each ADC\_I\_U, ADC\_I\_V, ADC\_I0\_EXT, and ADC\_I1\_EXT are mapped either to ADC\_I0\_RAW or to ADC\_I1\_RAW by ADC\_I0\_SELECT and ADC\_I1\_SELECT.


FOC23 Engine

In addition, the ADC\_OFFSET is for conversion of unsigned ADC values into signed ADC values as required for the FOC. For FOC3, the third current ADC\_I2 is calculated via Kirchhoff's Law. This requires the correct scaling and offset correction beforehand. For FOC2, there is no calculation of a third current. The scaling factors ADC\_I0\_SCALE and ADC\_I1\_SCALE are displayed in a Q8.8 format which results in the following equations:

$$\ A D C _ { - 1 0 } = ( \ A D C _ { - 1 0 } \L R W - \ A D C _ { - 1 0 } \L O F S E T ) \cdot \ A D C _ { - 1 0 } \L S C A L / \ 2 5 6$$

$$\ A D C _ { - 1 } I = ( \ A D C _ { - 1 } I _ { - } R A W - \ A D C _ { - 1 } I _ { - } \text {OFFSET} ) \cdot \ A D C _ { - 1 } I _ { - } \text {SCALE} / 2 5 6$$

The ADC\_UX\_SELECT selects one of the three ADC channels ADC\_I0, ADC\_I1, or ADC\_I2 for ADC\_UX.

The ADC\_WY\_SELECT selects one of the three ADC channels ADC\_I0, ADC\_I1, or ADC\_I2 for ADC\_WY.

The ADC\_V\_SELECT selects one of the three ADC channels ADC\_I0, ADC\_I1, or ADC\_I2 for ADC\_V.

The ADC\_UX, ADC\_V, and ADC\_WY are for the FOC3 (U, V, W).

The ADC\_UX and ADC\_WY (X, Y) are for the FOC2 (UX, WY).

Note

The open-loop encoder is useful to run a motor open loop for setting up the ADC channel selection with correct association between phase currents I\_U, I\_V, I\_W and phase voltages U\_U, U\_V, U\_W.

## 4.6 Encoder Engine

The different position sensors are the position sources for torque and flux control via FOC, for velocity control, and for position control. The PHI\_E\_SELECTION selects the source of the electrical angle phi\_e for the inner FOC control loop. VELOCITY\_SELECTION selects the source for velocity measurement. With phi\_e selected as source for velocity measurement, one gets the electrical velocity. With the mechanical angle phi\_m selected as source for velocity measurement, one gets the mechanical velocity taking the set number of pole pairs (N\_POLE\_PAIRS) of the motor into account. Nevertheless, for a highly precise positioning, it might be useful to do positioning based on the electrical angle phi\_e.

The encoder engine is an unified position sensor interface. It maps the selected encoder position information to electrical position (phi\_e) and to mechanical position (phi\_m). Both are 16 bit values. The encoder engine maps single turn positions from position sensors to multi-turn positions. The user can overwrite the multi-turn position for initialization.

## 4.6.1 Open-Loop Encoder

For initial system setup, the encoder engine is equipped with an open-loop position generator. This allows for turning the motor open-loop by specifying speed in rpm and acceleration in rpm/s, together with a voltage UD\_EXT in D direction. As such, the open-loop encoder is not a real encoder. It simply gives positions as an encoder does. The open-loop decoder has a direction bit to define direction of motion for the application.


1/2 ppr

135°

180°

180°

## Note

225°

225°

1/4 ppr

9

270°

With the open-loop encoder, the user can turn a motor without any position sensor and without any current measurement as a first step of doing the system setup. With the turning motor, the user can adjust the ADC scales and offsets and set up positions sensors (Hall, incremental encoder, ...) according to resolution, orientation, and direction of rotation.

9

The open-loop encoder is useful for initial ADC setup, encoder setup, Hall signal validation, and for validation of the number of pole pairs of a motor. The openloop encoder turns a motor open with programmable velocity in unit [RPM] with programmable acceleration in unit [RPM/s]. 315°

## 4.6.2 Incremental ABN Encoder

NPP =2: phi\_e = 2* phi\_m

The incremental encoders give two phase shifted incremental pulse signals A and B. Some incremental encoders have an additional null position signal N or zero pulse signal Z. An incremental encoder (called ABNencoderorABZencoder)hasanindividualnumberofincrementalpulses per revolution. The number of incremental pulses define the number of positions per revolution (PPR). The PPR might mean pulses per revolution or periods per revolution. Instead of positions per revolution, some incremental encoder vendors call these CPR counts per revolution.

The PPR parameter is the most important parameter of the incremental encoder interface. With that, it forms a modulo (PPR) counter, counting from 0 to (PPR-1). Depending on the direction, it counts up or down. The modulo PPR counter is mapped into the register bank as a dual ported register. The user can overwrite it with an initial position. The ABN encoder interface provides both the electrical position and the multi-turn position, which are accessible through dual-ported read-write registers.

## Note

The PPR parameter must be set exactly according to the used encoder.


Figure 20: Number of Pole Pairs NPP vs. mechanical angle phi\_m and electrical angle phi\_e


45°

d

270°

1/4 ppr

90°

180°

90°

45°

1/8 ppr

120°

V

W

240°

90°

Y

The goal of the initialization of an incremental encoder is to set it up so that the magnetic axis of the rotor fits with the electrical angle phi\_e with the angle zero on D axis. For this, one needs to know the number of pole pairs NPP, the resolution of the incremental encoder in pulses per revolution PPR, and the orientation between measured encoder angle of the rotor and the electrical angle of the field orientation. An encoder measures mechanical angle phi\_m were the FOC needs the electrical angle phi\_e for commutation. The number of pole pairs NPP determines the ratio between mechanical angle phi\_m and electrical angle phi\_e. The parameters phi\_m\_offset and phi\_e\_offset are for compensation of differences in orientation angle by adjustments.

Figure 21: ABN Incremental Encoder N Pulse


The N pulse from an encoder triggers either sampling of the actual encoder count to fetch the position at the N pulse or it re-writes the fetched n position on an N pulse. The N pulse can either be used as stand alone pulse or and-ed with NAB = N and A and B. It depends on the decoder what kind of N pulse has to be used - either N or NAB. For those encoders with precise N pulse within one AB quadrant, the N pulse must be used. For those encoders with N pulse over four AB quadrants the user can enhance the precision of the N pulse position detection by using NAB instead of N.

## Note

Incremental encoders are available with N pulse and without N pulse.

The polarity of N pulse, A pulse and B pulse are programmable. The N pulse is for re-initialization with each turn of the motor. Once fetched, the ABN decoder can be configured to write back the fetched N pulse position with each N pulse.

## Note

Logical ABN = A and B and N might be useful for incremental encoders with low resolution N pulse to enhance the resolution. On the other hand, for incremental encoders with high resolution N pulse a logical ABN = A and B and N might totally suppress the resulting N pulse.

The ABN encoder interface has a direction bit to set to match wiring of motor to direction of encoder.


a

b

n

abn

A

B

N

ABN

Figure 22: Encoder ABN Timing - high precise N pulse and less precise N pulse


## 4.6.3 Secondary Incremental ABN Encoder

The TMC4671 is equipped with a secondary incremental encoder interface. This secondary encoder interface is available as source for velocity control or position control. This is for applications where a motor with a gearing positions an object.

For commutating a motor with FOC, the user selects a position sensor source (digital incremental encoder, digital Hall, analog Hall, analog incremental encoder, ...) that is mounted close to the motor. The inner FOC loop controls torque and flux of the motor based on the measured phase currents and the electrical angle of the rotor.

Info

The secondary incremental encoder is not available for commutation (phi\_e) for the inner FOC. In others words, there is no electrical angle phi\_e selectable from the secondary encoder.

## 4.6.4 Digital Hall Sensor Interface with optional Interim Position Interpolation

The digital Hall interface is the position sensor interface for digital Hall signals. The digital Hall signal interface first maps the digital Hall signals to an electrical position PHI\_E\_RAW. An offset PHI\_E\_OFFSET can be used to rotate the orientation of the Hall signal angle. The electrical angle PHI\_E is for commutation. Optionally, the default electrical positions of the Hall sensors can be adjusted by writes into the associated registers.


110

H2

V

150°

180°

-180°

OxAAAA

W

H3

Ox7FFF

0x8000

Y

90°

30°

H1


4

UX

4

Figure 23: Hall Sensor Angles


Hall sensors give absolute positions within an electrical period with a resolution of 60° as 16 bit positions (s16 resp. u16) PHI. With activated interim Hall position interpolation, the user gets high resolution interim positions when the motor is running at a speed above 60 rpm.

## 4.6.5 Digital Hall Sensor - Interim Position Interpolation

For lower torque ripple the user can switch on the position interpolation of interim Hall positions. This function is useful for motors that are compatible with sine wave commutation, but equipped with digital Hall sensors. When the position interpolation is switched on, it becomes active on speeds above 60 rpm. For lower speeds it automatically disables itself. This is especially important when the motor has to be at rest. Hall sensor position interpolation might fail when Hall sensors are not properly placed in the motor. Please adjust Hall sensor positions for this case.

## Info

Hall interpolation is not intended for positioning applications, especially not with changes of direction. Please check errata section if you want to use hall interpolation and positioning. When using interpolated angles PID\_POSITION\_ACTUAL might glitch when direction is changed or the motor operates at very low velocity.

## 4.6.6 Digital Hall Sensors - Masking, Filtering, and PWM center sampling

Uncorrelated distortions can be filtered via a digital filter of configurable length. If the input signal to the filter does not change for HALL\_DIG\_FILTER\_LENGTH times 5 us, the signal can pass the filter. This filter eliminates issues with bouncing Hall signals. naming with Elliot: Masking is better then Blanking

Sometimes digital Hall sensor signals get disturbed by switching events in the power stage. The TMC4671 can automatically mask switching distortions by correct setting of the HALL\_MASKING register. When a switching event occurs, the Hall sensor signals are held for HALL\_MASKING value times 10 ns. This way, Hall sensor distortions are eliminated.

Spikes on Hall signals (Hx that stands for H1, H2, H3) disturb the FOC loop when Hall signals are used for commutation or for initialization of incremental encoders. Spikes on hall signal lines might occur when


W

UX

PWM\_UX

Y V

W

UX

Hr i ri ulul iu m ntt

PWM\_V

PWM\_WY

H3LLLШIm

PWM\_CENTER

H1

H3

Hall signals are feed on singled ended signal lines in parallel to motor power lines due to electromagnetic cross talk in a single cable. Long Hall signal lines might cause digital Hall signal cross talk even in separate fed cables. Cables that provide Hall signals without spikes should be preferred. A good ground for digital Hall signals is important for clean Hall signals. A good ground shield of the motor might help for clean Hall signals. In best case, Hall signals are fed within separate shielded signal lines together with differential line drivers.

Figure 24: Outline of noisy Hall signals (left) due to electromagnetic interference with PWM switching and noise cleaned Hall signals (right) by PWM center synced sampling of Hall signal vector (H1 H2 H3)


The best is avoiding spikes on digital Hall signals. Nevertheless, to enable lower cost motors with lower performance Hall signal shielding, the TMC4671 is equipped with Hall Signal spike suppression and PWM centered Hall signal vector sampling.

To reduce possible current ripple that might be caused by noisy Hall signals, the sampling of the Hall signal vector can be programmed for sampling once per PWM period at its center for the desired noise reduction. The PWM centered Hall signal sampling is programmable by HALL\_MODE(4) control bit. Continuous sampling is default. This function is not available for TMC4671-ES engineering samples.

Figure 25: Hall Signal PWM Center Sampling on PWM\_CENTER


The PWM center synchronization needs to be qualified for high speed applications due to reduction of Hall signals for PWM frequency. The PWM center might have an influence on Hall signal interpolation and needs to be qualified if Hall signal interpolation is enabled.

For additional spike suppression, the TMC4671 is equipped with a digital hall signal blanking, to support lower performance cabling environments. The blank time for the Hall signals is programmable (HALL\_BLANK) in steps of 10 ns from 0 ns up to 4095 ns. The Hall signal blanking time should be programmed as long as necessary for safe suppression of spikes of maximum duration. On the other side, the Hall signal blanking should be programmed as short as possible to avoid disturbance by too strong filtering that might also disturbe the FOC.


PWM cycle tPWM

UX

4

Y

A

V

W

UX

4

Figure 26: Hall Signal Blanking


## 4.6.7 Digital Hall Sensors together with Incremental Encoder

If a motor is equipped with both Hall sensors and incremental encoder, the Hall sensors can be used for the initialization as a low resolution absolute position sensor. Later on, the incremental encoder can be used as a high resolution sensor for commutation.

## 4.6.8 Analog Hall and Analog Encoder Interface (SinCos of 0° 90° or 0° 120° 240°)

An analog encoder interface is part of the decoder engine. It is able to handle analog position signals of 0° and 90° and of 0° 120° 240°. The analog decoder engine adds offsets and scales the raw analog encoder signals, while also calculating the electrical angle PHI\_E from these analog position signals by an ATAN2 algorithm.

Figure 27: Analog Encoder (AENC) signal waveforms


An individual signed offset is added to each associated raw ADC channel and scaled by its associated scaling factors according to

$$\ A E N _ { - } \, \L A U E = ( A E N _ { - } \, \L A W + A E N _ { - } \, \L O F S E T ) \cdot A E N _ { - } \, \S C A L E$$


## Info

Register Bank

ADC RAW INPUT CHANNEL SELECTOR

AENC SCALER

AENC\_UX

AENC\_V

Decoder Engine

In addition, the AENC\_OFFSET is for conversion of unsigned ADC values into signed ADC values as required for the FOC.

· AENC\_1\_SELECT

The control bit 0 in register AENC\_DECODER\_MODE (0x3B) selects either processing of analog position signals of 0° and 90° (0b0) or analog signals of 0° 120° 240° on (0b1). - AENC\_UX\_SCALE

· AENC\_VN\_OFFSET

· AENC\_VN\_SCALE

Figure 28: Analog Encoder (AENC) Selector &amp; Scaler w/ Offset Correction


In Fig. 27 possible waveforms are shown. The graphs show usual SIN/COS track signals with one and multiple periods per revolution as well as typical waveforms of three phase analog Hall signals for one electrical revolution. The number of periods per revolution can be configured by register AENC\_DECODER\_PPR. The position in one period (AENC\_DECODER\_PHI\_A) is calculated by an ATAN2 algorithm. The periods are counted with respect to the number of periods per revolution to calculate AENC\_DECODER\_PHI\_E and AENC\_DECODER\_PHI\_M. If PPR is the same as the number of pole pairs, AENC\_DECODER\_PHI\_E and AENC\_DECODER\_PHI\_A are identical. This is usually the case for analog hall signals.

Info

The analog N pulse is just a raw ADC value. Handling of analog N pulse similar to N pulse handling of digital encoder N pulse is not implemented for analog encoder.

## 4.6.9 Analog Position Decoder (SinCos of 0°90° or 0°120°240°)

The extracted positions from the analog decoder are available for read out from registers.


## 4.6.9.1 Multi-Turn Counter

Electrical angles are mapped to a multi-turn position counter. The user can overwrite this multi-turn position for initialization purposes.

## 4.6.9.2 Encoder Engine Phi Selector

The angle selector selects the source for the commutation angle PHI\_E. That electrical angle is available for commutation.

## 4.6.9.3 External Position Register

A register value written into the register bank via the application interface is available for commutation as well. With this, the user can interface to any encoder by just writing positions extracted from external encoderinto this regulator. From the decoder engine point of view this is just one more selectable encoder source.

## 4.6.10 Encoder Initialization Support

The TMC4671 needs proper feedback for correct and stable operation. One main parameter is the commutation angle offset PHI\_E\_OFFSET. This offset must not be calculated when an absolute sensor system like analog or digital Hall sensors is used. All other supported feedback systems need to be initialized their PHI\_E\_OFFSETs need to be identified. The user has several options to determine PHI\_E\_OFFSET with support of the TMC4671.

## 4.6.10.1 Encoder Initialization in Open-Loop Mode

In the case of a free driving motor, the motor can be switched to Open-Loop Mode. In this mode, the used commutation angle (PHI\_OPEN\_LOOP) can be used to match the measured PHI\_E. This method is supported by the TMCL-IDE.

## 4.6.10.2 Encoder Initialization by Hall sensors

The TMC4671 can calculate PHI\_E\_OFFSET very precisely at a Hall state change for a second encoder system, when Hall sensors are correctly aligned. Therefore, the function needs to be enabled and calculate a new offset at the next Hall state change. After disabling of the module, the process can be started again. This function can also be used as a rough plausibility check during longer operation.

## 4.6.10.3 Encoder Initialization by N Pulse Detection

After determination of a correct offset, the value can be used again after power cycle. The encoder's N pulse can be used as reference for this. For starters the user can drive the motor in open-loop mode or by using digital Hall sensor signals. After passing the encoder's N pulse, the ABN encoder is initialized and can be used for operation.

## 4.6.11 Velocity Measurement

Servo control comprises position, velocity and current control. The position and the current are measured by separate sensors. The actual velocity has to be calculated by time discrete differentiation from the position signal. the user can choose a calculated position from the various encoder interfaces for velocity measurement by parameter VELOCITY\_SELECTION.


The user can switch between two different velocity calculation algorithms with the parameter VELOC-ITY\_METER\_SELECTION. Default setting (VELOCITY\_METER\_SELECTION = 0) is the standard velocity meter, which calculates the velocity at a sampling rate of about 4369.067 Hz by differentiation. Output value is displayed in rpm (revolutions per minute). This option is recommended for usage with the standard PI controller structure.

By choosing the second option (VELOCITY\_METER\_SELECTION = 1), the sampling frequency is synchronized to the PWM frequency. This option is recommended for usage with the advanced PI controller structure. Otherwise, the controller structure might tend to be unstable due to non-matched sampling. Velocity filters can be applied to reduce noise on velocity signals. Section 4.8 describes filtering opportunities in detail.

## 4.6.12 Reference Switches

With the STATUS\_FLAGS and STATUS\_MASK register the STATUS output can be configured as an IRQ for passing a reference switch.

TheTMC4671isequippedwiththreeinputpinsforreferenceswitches(REF\_SW\_L,REF\_SW\_HandREF\_SW\_R). These pins can be used to determine three reference positions. The TMC4671 displays the status of the reference switches in the register TMC4671\_INPUTS\_RAW and is able to store the actual position at rising edge of the corresponding signal. The signal polarities are programmable and the module reacts only on toggling the ENABLE register. The signals can be filtered with a configurable digital filter, which suppresses spike errors.

The actual position can be latched when passing a reference switch. The latched positions can be displayed in register INTERIM\_DATA (0x6E). Register INTERIM\_ADDR (0x6F) selects the data displayed in IN-TERIM\_DATA with HOME\_POSITION at address 31, LEFT\_POSITION at adress 32 and RIGHT\_POSITION at adress 33.

The position latching can be enabled via register CONFIG\_DATA (0x4D) with CONFIG\_ADDR (0x4E) set to 51 (ref\_switch\_config). Position latching is enabled by setting bit 0 of ref\_switch\_config to 1.If a reference switched is passed the corresponding status bit (HOME\_SWITCH\_PASSED, LEFT\_SWITCH\_PASSED, and RIGHT\_SWITCH\_PASSED) in REF\_SWITCH\_STATUS (INTERIM\_DATA with INTERIM\_ADDRESS = 30) is enabled. The bits can only be cleared by toggling/disabling the enable bit in ref\_switch\_config.

Info

The polarity registers do not affect the status registers. The status flag only represents the current logical state of the switch.


## 4.7 FOC23 Engine

The FOC23 engine performs the inner current control loop for the torque current I Q and the flux current I D including the required transformations. Programmable limiters take care of clipping of interim results. Per default, the programmable circular limiter clips U\_D and U\_Q to U\_D\_R = √ (2) · U\_QandU\_R\_R = √ (2) · U\_D. PI controllers perform the regulation tasks. Please make sure to enable controllers by pulling ENI pin to high level.

## 4.7.1 ENI and ENO pins

The ENI (Enable input) can be used to start and stop control action. During reset ENO (Enable out) is low and afterwards it forwards ENI signal. Thereby it can be used to enable the power stage. When ENI is low, all controllers are deactivated and PWM operates at 50% duty cycle. ENI input value can be read through TMC4671\_INPUTS\_RAW register.

## 4.7.2 PI Controllers

PI controllers are used for current control and velocity control. A P controller is used for position control. The derivative part is not yet supported but might be added in the future. The user can choose between two PI controller structures: The classic PI controller structure, which is also used in the TMC4670, and the advanced PI controller structure. The advanced PI controller structure shows better performance in dynamics and is recommended for high performance applications. User can switch between controllers by setting register MODE\_PID\_TYPE. Controller type can not be switched individually for each cascade level.

## 4.7.3 PI Controller Calculations - Classic Structure

The PI controllers in the classic structure perform the following calculation with

$$Y = P \cdot e + 1 \cdot \int _ { 0 } ^ { t } e ( t ) \, d t$$

$$e = X _ { - } T \arg E - X$$

where X\_TARGET stands for target flux (s16), target torque (s16), target velocity (s32), or target position (s32) with error e, which is the difference between target value and actual values. The Y stands for the output of the PI controller feed as target input to the successive PI controller of the FOC servo controller cascade (position → PI → velocity → PI → current → PI → voltage).

Y\_PID\_FLUX =

PID\_FLUX\_P * ERROR\_FLUX / 256

Y\_PID\_FLUX\_RATE =

PID\_FLUX\_I * ERROR\_FLUX / 65536 / (32 µ s)

Y\_PID\_TORQUE =

PID\_FLUX\_P * ERROR\_TORQUE / 256

Y\_PID\_TORQUE\_RATE

=

PID\_TORQUE\_I * ERROR\_TORQUE / 65536 / (32 µ s)

Y\_PID\_VELOCITY =

PID\_VELOCITY\_P

* ERROR\_VELOCITY / 256

Y\_PID\_VELOCITY\_RATE = PID\_VELOCITY\_I * ERROR\_VELOCITY / 65536 / (256 µ s)


```
Y_PID_POSITION         =   PID_POSITION_P    *   ERROR_POSITION / 65536
Y_PID_POSITION_RATE    =   PID_POSITION_I    *   ERROR_POSITION / 65536 / (256 \, \mu)

```

Table 20: Scalings and Change Rate Timings of PID controllers (classic structure) for currents, velocity, and position for clock frequency fCLK = 25MHz

Number

Motion Mode

Table 21: Motion Modes

|   0 | Stopped Mode         | Disabling all controllers                              |
|-----|----------------------|--------------------------------------------------------|
|   1 | Torque Mode          | Standard Torque Control Mode                           |
|   2 | Velocity Mode        | Standard Velocity Control Mode                         |
|   3 | Position Mode        | Standard Position Control Mode                         |
|   4 | PRBS Flux Mode       | PRBS Value is used as Target Flux Value for Ident.     |
|   5 | PRBS Torque Mode     | PRBS Value is used as Target Torque Value for Ident.   |
|   6 | PRBS Velocity Mode   | PRBS Value is used as Target Velocity Value for Ident. |
|   7 | PRBS Position Mode   | PRBS Value is used as Target Position Value for Ident. |
|   8 | UQ UD Ext Mode       | Voltage control mode (Software Mode)                   |
|   9 | reserved             | reserved                                               |
|  10 | AGPI_A Torque Mode   | AGPI_A used as Target Torque value                     |
|  11 | AGPI_A Velocity Mode | AGPI_A used as Target Velocity value                   |
|  12 | AGPI_A Position Mode | AGPI_A used as Target Position value                   |
|  13 | PWM_I Torque Mode    | PWM_I used as Target Torque value                      |
|  14 | PWM_I Velocity Mode  | PWM_I used as Target Velocity value                    |
|  15 | PWM_I Position Mode  | PWM_I used as Target Position value                    |

Description


target value

Xeargor[s16, s32]

Xtarget input, limit target offset

e (error)

I parameter ddT\_output\_ limit

dXdT[s16, s32]


Figure 29: Classic PI Controller

| Info   | the controller output to jump, as the control error is first integrated and then gained by the I parameter. Jumps can be avoided by incremental changes of I-parameter.                                                              |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Info   | Support for the TMC4671 is integrated into the TMCL-IDE including wizards for set upandconfiguration. With the TMCL-IDE, configuration and operation can be doneinafewstepsandtheusergetsdirect access to all registersoftheTMC4671. |

## 4.7.4 PI Controller Calculations - Advanced Structure

The PI controllers in the advanced controller structure perform the calculation with

$$d X d T = P \cdot e + \int _ { 0 } ^ { t } P \cdot I \cdot e ( t ) \, d t$$

$$e = X _ { - } T \arg E - X$$

where X\_TARGET represents target flux, target torque, target velocity, or target position with control error e, which is the difference between target value and actual values. The time constant d t is set according to the PWM period but can be downsampled for the position controller by register MODE\_PID\_SMPL. Position controller evaluation can be downsampled by a constant factor when needed.


· output value

target value target offset

target\_input\_limit /

## Info

The transfer function of the advanced PI controller can be described by the following pseudo code:

## Info

+

dXdT[s16/s32]

Figure 30: Advanced PI Controller


The P Factor normalization as Q8.8 of the advanced PI controller of the TMC4671ES is selectable for the TMC4671-LA as either Q8.8 or Q4.12. This can be configured in register 0x4D CONFIG\_DATA when register 0x4E CONFIG\_ADDR is set to 0x3E. For more information refer to section 7.2. Using Q4.12 needs changes in the user's application controller software when using the Advanced PI position controller.

$$\text { of the advanced Pl controller can be described by the following pseudo code:} \\ \text {dXdT} = e \cdot P + integrator \\ \intertext { i n t e r g r a $ = $ integrator + ( P \cdot I \cdot e ) / 2 5 6 }$$

For the advanced control structure the integrator input value is additionally divided by 256. (s. equation 31)

P and I are either displayed as Q8.8 (P/256) or Q4.12 (P/4096). This is individually configurable for each controller parameter in the controller cascade. Table 22 gives an overview on how the representation affects the integrator and the output of the PI controller.

PI representation

I 8.8

Table 22: PI normalization overview

| P 8.8   | dXdT = e · P 256 + integrator integrator = integrator + ( P 256 · I 256 · e ) / 256   | dXdT = e · P 256 + integrator integrator = integrator + ( P · I · e ) / 256                     |
|---------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| P 4.12  | dXdT = e · P 4096 + integrator integrator = integrator + ( P 4096 · I 256 · e ) / 256 | 256 4096 dXdT = e · P 4096 + integrator integrator = integrator + ( P 4096 · I 4096 · e ) / 256 |

I 4.12


e (error)

I parameter ddT\_output limit

Downsampling of the advanced position controller can be configured by register MODE\_PID\_SMPL. When the register is 0 the controllers will sample on the PWM-frequency f PWM . The new samplerate will be derived from f PWM and the downsampling-value assigned to register MODE\_PID\_SMPL (range: 0 to 127). The derived sampling frequency is calculated as follows:

## 4.7.5 PI Controller - Clipping

The target input is clipped to X\_TARGET\_LIMIT. The output of a PI controller is named dXdT because it gives the desired derivative d/dt as a target value to the following stage: The position (x) controller gives velocity (dx/dt). The output of the PI Controller is clipped to dXdT\_LIMIT. The error integral of (27) is clipped to dXdT\_LIMIT / I in the classic controller structure, and the integrator output is clipped to dXdT\_output\_limit in the advanced controller structure.

$$\text {frequency is calculated as follows:} \\ \text {Samplerate} \text {new} = \frac { f _ { \text {PWM} } } { \text {downsampling} + 1 }$$

The limiting of target values for PI controllers and output values of PI controllers is programmable. Per power on default these limits are set to maximum values. During initialization, these limits should be set properly for correct operation and clipping.

The output of the torque and flux controller is limited by register 0x5D PIDOUT\_UQ\_UD\_LIMITS.

The minimum input of the position controller is limited by register 0x61 PID\_POSITION\_LIMIT\_LOW.

The input of the torque and flux controller is limited by register 0x5E PID\_TORQUE\_FLUX\_LIMITS. The input of the velocity controller is limited by register 0x60 PID\_VELOCITY\_LIMIT.

The maximum input of the position controller is limited by register 0x62 PID\_POSITION\_LIMIT\_HIGH.


target value target velocity

target position

XtargetEs 16]

Xtarget\_input \_imit target offset

e (error)

I parameter ddT\_output\_limit | dXdT[s16]


oe(t)dt

VELOCITY

target\_input\_ imit

+

e (error)

dXdT \_output\_limit dxdT[s16]


oe(t)dt

Xtarget[s 32]

Xtarget\_ input\_ imit e (error)

ddT\_output limit, dXdT[s32]


+4

+ 7

· output value

· output target torque output target velocity

Figure 31: PI Controllers for position, velocity and current

## 4.7.6 PI Flux &amp; PI Torque Controller

The P part is represented as q8.8 and I is the I part represented as q0.15.

## 4.7.7 PI Velocity Controller

The P part is represented as q8.8 and I is the I part represented as q0.15.

ddT\_LIMIT /I


la TARGET

·

## 4.7.8 P Position Controller

For the position regulator, the P part is represented as q4.12 to be compatible with the high resolution positions - one single rotation is handled as an s16. For the advanced controller structure the P part is represented by q8.8.

lar la

## 4.7.9 Inner FOC Control Loop - Flux &amp; Torque

lu, Iv, lw

The inner FOC loop (figure 32) controls the flux current to the flux target value and the torque current to the desired torque target. The inner FOC loop performs the desired transformations according to figure 33 for 3-phase motors (FOC3). For 2-phase motors (FOC2) both Clarke (CLARKE) transformation and inverse Clarke (iCLARKE) are bypassed. For control of DC motors, transformations are bypassed and only the first full bridge (connected to X1 and X2) is used.

The inner FOC control loop gets a target torque value (I\_Q\_TARGET) which represents acceleration, the rotor position, and the measured currents as input data. Together with the programmed P and I parameters, the inner FOC loop calculates the target voltage values as input for the PWM engine.

Figure 32: Inner FOC Control Loop


## 4.7.10 FOC Transformations and PI(D) for control of Flux &amp; Torque

In case of the FOC2, Clarke transformation CLARKE and inverse Clarke Transformation iCLARKE are skipped.

The Clarke transformation (CLARKE) maps three motor phase currents ( I U , I V , I W ) to a two-dimensional coordinate system with two currents ( I α , I β ). Based on the actual rotor angle determined by an encoder or via sensorless techniques, the Park transformation (PARK) maps these two currents to a quasi-static coordinate system with two currents ( I D , I Q ). The current I D represents flux and the current I Q represents torque. The flux just pulls on the rotor but does not affect torque. The torque is affected by I Q . Two PI controllers determine two voltages ( U D , U Q ) to drive desired currents for a target torque and a target flux. The determined voltages ( U D , U Q ) are re-transformed into the stator system by the inverse Park transformation (iPARK). The inverse Clarke Transformation (iCLARKE) transforms these two currents into three voltages ( U U , U V , U W ). Theses three voltage are the input of the PWM engine to drive the power stage.


Inner FOC Loop

ACTUAL\_POSITION

PIDIN\_ACTUAL\_VELOCITY

PID

Rotor System w/ quasi static

TARGET\_POSITION

voltage vector (UD Ua)

POSITION

PIDOUT\_TARGET\_VELOCITY

MOTION\_MODE = POSITION\_MODE

Rotor System w/ quasi static

Stator System w/

PIDIN\_ACTUAL\_VELOCITY

TARGET\_TORQUE

PID

PIDIN\_TARGET\_VELOCITY

iPARK

iCLARKE

MOTION\_MODE = TORQUE\_MODE


current vector (Io la)

Figure 33: FOC3 Transformations (FOC2 just skips CLARKE and iCLARKE)

## 4.7.11 Motion Modes

TheusercanoperatetheTMC4671inseveralmotionmodes. Standardmotionmodesarepositioncontrol, velocity control and torque control, where target values are fed into the controllers via register access. The motion mode UD\_UQ\_EXTERN allows the user to set voltages for open-loop operation and for tests during setup.

Figure 34: Standard Motion Modes


In position control mode, the user can feed the step and direction interface to generate a position target value for the controller cascade. In additional motion modes target values are fed into the TMC4671 via PWMinterface (Pin: PWM\_IN) or analog input via pin AGPI\_A.


VELOCITY

rotating voltage vector (Ua UB)

PIDOUT\_TARGET\_TORQUE

MOTION\_MODE = VELOCITY\_MODE

PIDIN\_ACTUAL\_ TORQUE

Stator System w/

rotating voltage triple (Uu Uv Uw)

PIDIN\_TARGET\_TORQUE

PID

ua

TORQUE

CIRCULAR

LIMITER

Uv

PID

FLUX

UD

UD\_LIMITED

VQ\_LIMITED

There are additional motion modes, which are using input from the PWM\_I input or the AGPI\_A input. Input signals can be scaled via a standard scaler providing offset and gain correction. The interface can be configured via the registers SINGLE\_PIN\_IF\_OFFSET\_SCALE and SINGLE\_PIN\_IF\_STATUS\_CFG, where the status of the interface can be monitored as well. PWM input signals which are out of frequency range can be neglected. In case of wrong input data, last correct position is used or velocity and torque are set to zero.

|   0 | Stopped Mode         | Disabling all controllers                              |
|-----|----------------------|--------------------------------------------------------|
|   1 | Torque Mode          | Standard Torque Control Mode                           |
|   2 | Velocity Mode        | Standard Velocity Control Mode                         |
|   3 | Position Mode        | Standard Position Control Mode                         |
|   4 | PRBS Flux Mode       | PRBS Value is used as Target Flux Value for Ident.     |
|   5 | PRBS Torque Mode     | PRBS Value is used as Target Torque Value for Ident.   |
|   6 | PRBS Velocity Mode   | PRBS Value is used as Target Velocity Value for Ident. |
|   7 | PRBS Position Mode   | PRBS Value is used as Target Position Value for Ident. |
|   8 | UQ UD Ext Mode       | Voltage control mode (Software Mode)                   |
|   9 | reserved             | reserved                                               |
|  10 | AGPI_A Torque Mode   | AGPI_A used as Target Torque value                     |
|  11 | AGPI_A Velocity Mode | AGPI_A used as Target Velocity value                   |
|  12 | AGPI_A Position Mode | AGPI_A used as Target Position value                   |
|  13 | PWM_I Torque Mode    | PWM_I used as Target Torque value                      |
|  14 | PWM_I Velocity Mode  | PWM_I used as Target Velocity value                    |
|  15 | PWM_I Position Mode  | PWM_I used as Target Position value                    |

Motion Mode

Table 23: Motion Modes

During regenerative braking of the motor, current is driven into the DC link. If the power frontend is not actively controlled, the DC link voltage will rise. The brake chopper output pin (BRAKE) can be used for control of an external brake chopper, which burns energy over a brake resistor. The BRAKE pin is set to high for a complete PWM cycle if measured voltage is higher then ADC\_VM\_LIMIT\_HIGH. Once active it will be deactivated when voltage drops below ADC\_VM\_LIMIT\_LOW. This acts like a hysteresis. BRAKE can be deactivated by setting both registers to Zero. By setting proper values in the registers it is automatically enabled.


Number

## 4.7.12 Brake Chopper

Description

## 4.8 Filtering and Feed-Forward Control

The TMC4671 uses different filters for certain target and actual values. When using standard velocity meter, a standard velocity filter is used which is optimized for velocity signals from Hall sensors. Additional Biquad filters can be used to suppress measurement noise or damp resonances.

## 4.8.1 Biquad Filters

$$Y ( n ) = X ( n ) \cdot b _ { - } 0 + X ( n - 1 ) \cdot b _ { - } 1 + X ( n - 2 ) \cdot b _ { - } 2 + Y ( n - 1 ) \cdot a _ { - } 1 + Y ( n - 2 ) \cdot a _ { - } 2$$

The TMC4671 uses standard biquad filters (standard IIR filter of second order, Wikipedia Article) in the following structure.

In this equation X(n) is the actual input sample, while Y(n-1) is the filter output of the last cycle. All coefficients are S32 values and are normalized to a Q3.29 format. Users must take care of correct parametrization of the filter. There is no built-in plausibility or stability check. All filters can be disabled or enabled via register access. Biquad state variables are reset when parameters are changed. The TRINAMIC IDE supports parametrization with wizards. A standard biquad filter has the following transfer function in the Laplace-Domain:

$$G ( s ) = \frac { b _ { - } 2 _ { \text {cont} } \cdot s ^ { 2 } + b _ { - } 1 _ { \text {cont} } \cdot s + b _ { - } 0 _ { \text {cont} } } { a _ { - } 2 _ { \text {cont} } \cdot s ^ { 2 } + a _ { - } 1 _ { \text {cont} } \cdot s + a _ { - } 0 _ { \text {cont} } }$$

The transfer function needs to be transformed to time discrete domain by Z-Transformation and coefficients need to be normalized. This is done by the following equations.

$$b _ { - } 2 z & = ( b _ { - } 0 _ { c o n t } \cdot T ^ { 2 } + 2 \cdot b _ { - } 1 _ { c o n t } \cdot T + 4 \cdot b _ { - } 2 _ { c o n t } ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { c o n t } \cdot T + 4 \cdot a _ { - } 2 _ { c o n t } ) \\ b _ { - } 2 & = ( b _ { - } 0 _ { c o n t } \cdot T ^ { 2 } + 2 \cdot b _ { - } 1 _ { c o n t } \cdot T + 4 \cdot b _ { - } 2 _ { c o n t } ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { c o n t } \cdot T + 4 \cdot a _ { - } 2 _ { c o n t } )$$

$$b _ { - } 1 & z = ( 2 \cdot b _ { - } 0 _ { - } c o n t \cdot T ^ { 2 } - 8 \cdot b _ { - } 2 _ { - } c o n t ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) \\ b _ { - } 0 & z = ( b _ { - } 0 _ { - } c o n t \cdot T ^ { 2 } - 2 \cdot b _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot b _ { - } 2 _ { - } c o n t ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) \\ & \\$$

$$b _ { - } 2 z & = ( b _ { - } 0 _ { - } c o n t \cdot T ^ { 2 } + 2 \cdot b _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot b _ { - } 2 _ { - } c o n t ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) \\ b _ { - } 1 _ { - } z & = ( 2 \cdot b _ { - } 0 _ { - } c o n t \cdot T ^ { 2 } - 8 \cdot b _ { - } 2 _ { - } c o n t ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) \\ b _ { - } 1 _ { - } z & = ( 1 \cdot b _ { - } 0 _ { - } c o n t \cdot T ^ { 2 } - 8 \cdot b _ { - } 2 _ { - } c o n t )$$

$$b _ { - } 0 _ { z } & = ( b _ { - } 0 _ { c o n t } \cdot T ^ { 2 } - 2 \cdot b _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot b _ { - } 2 _ { c o n t } ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { c o n t } \cdot T + 4 \cdot a _ { - } 2 _ { c o n t } ) \\ a _ { - } 2 _ { z } & = ( T ^ { 2 } + 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { c o n t } ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { c o n t } ) \\ & = ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { c o n t } ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { c o n t } )$$

$$a _ { - } 1 _ { - } z & = ( 2 \cdot T ^ { 2 } - 8 \cdot a _ { - } 2 _ { - } c o n t ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) \\ b _ { - } 0 & = r o u n d ( b _ { - } z - 2 ^ { 2 9 } ) \\ b _ { - } 1 & = 2 ( b _ { - } z - 2 ^ { 2 9 } )$$

$$a _ { - } 2 & z = ( T ^ { 2 } + 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) \\ a _ { - } 1 _ { - } z & = ( 2 \cdot T ^ { 2 } - 8 \cdot a _ { - } 2 _ { - } c o n t ) / ( T ^ { 2 } - 2 \cdot a _ { - } 1 _ { - } c o n t \cdot T + 4 \cdot a _ { - } 2 _ { - } c o n t ) \\ & .$$

$$b _ { - } & = r o u n d ( b _ { - } z - 2 ^ { 2 9 } ) \\ b _ { - 1 } & = r o u n d ( b _ { - } z - 2 ^ { 2 9 } ) \\ & \\$$

$$b _ { - } & 2 = r o u n d ( b _ { - } 2 - z \cdot 2 ^ { 2 9 } ) \\ a _ { - 1 } & = r o u n d ( - a _ { - } 1 _ { - } z \cdot 2 ^ { 2 9 } ) \\ &$$

$$b _ { - } & = r o u n d ( b _ { - } z - 2 ^ { 2 9 } ) \\ b _ { - 2 } & = r o u n d ( b _ { - } z - 2 ^ { 2 9 } ) \\ &$$

$$a _ { - } & = r o u n d ( - a _ { - } 1 _ { - } z \cdot 2 ^ { 2 9 } ) \\ a _ { - } 2 & = r o u n d ( - a _ { - } 2 _ { - } z \cdot 2 ^ { 2 9 } )$$

A standard second order lowpass filter with given cutoff frequency ω c and damping factor D has the following transfer function in the Laplace-Domain:

while T is the sampling time according to PWM\_MAX\_COUNT · 10nsandvariables with index z are auxiliary variables.

$$G _ { L P } ( s ) = \frac { 1 } { \frac { 1 } { \omega _ { c } ^ { 2 } } \cdot s ^ { 2 } + \frac { 2 \, D } { \omega _ { c } } \cdot s + 1 }$$

There are four biquad filters in the control structure. Figure 35 illustrates their placement in the control structure.

Users can determine filter coefficients with the upper equations by comparing coefficients of both transfer functions. The TMCL-IDE also provides a dimensioning tool.


Position target value

Flux target value

Torque target value

Actual

Velocity

·

·

·

·

Biquad

Position

Biquad

Flux

Biquad

Torque

Biquad

Velocity

Filtered

· position target

Filtered flux

Figure 35: Biquad Filters


The biquad filter for the position target value is intended to be used as a low-pass filter for smoothening position input to the control structure. It is evaluated in every PWM cycle, or down-sampled according to the down-sampling factor for the position controller. After powering on it is disabled.

The biquad filter for the torque target value can be used as a low-pass filter for bandwidth limitation and noise suppression. Moreover, it can be designed to suppress a resonance or anti-resonance. Same statements are correct for the velocity biquad filter. Both filters' sampling times are fixed to the PWM period.

The biquad filter for the flux target value is also intended to be used as a low-pass filter for input values from the user's microcontroller. Sampling frequency is fixed to the PWM frequency.

The velocity target value biquad is configured as a second order low-pass with a cutoff frequency at 200 Hz - by default at a sampling frequency of 25 kHz. Biquad filters can be activated separately.

## 4.8.2 Standard Velocity Filter

By using the standard velocity measurement algorithm, the default velocity filter is enabled and can not be switched off. The standard velocity filter is a low-pass filter with a cutoff frequency of 20 Hz (slope of -20 dB/Decade). In this configuration, a new velocity is calculated at a sample rate of approx. 4369.067 Hz. This configuration is intended to be used in low-performance applications with a simple position feedback system like digital Hall sensors.

## 4.8.3 Feed-Forward Control Structure

Note

Software feed forward control via offset registers is recommended, due to missing amplification possibility. Utilize feedforward to actively increase the target value of a controller besides the normal target input. For Torque/Flux use register 0x65 PID\_TORQUE\_FLUX\_OFFSET and for the velocity use register 0x67 PID\_VELOCITY\_OFFSET.


## 4.9 PWMEngine

+Vm motor supply voltage

High Side Transistor T\_H

(UX1, VX2, WY1, Y2)

The PWM engine takes care of converting voltage vectors to pulse width modulated (PWM) control signals. These digital PWM signals control the gate drivers of the power stage. For a detailed description of the PWMcontrol registers and PWM register control bits pls. refer section 7 page 72.

The ease-of-use PWM engine requires just a couple of parameter settings. Primarily, the polarities for the gate control signal of high-side and low-side must be set. The power on default PWM mode is 0, meaning PWM=OFF. For operation, the centered PWM mode must be switched on by setting the PWM mode to 7. A single bit switches the space vector PWM (SVPWM) on. For 3-phase PMSM, the SVPWM = ON gives more effective voltage. Nevertheless, for some applications it makes sense to switch the SVPWM = OFF to keep the star point voltage of a motor almost at rest.

## 4.9.1 PWMPolarities

The PWM polarities register (PWM\_POLARITIES) controls the polarities of the logic level gate control signals. The polarities of the gate control signals are individually programmable for low-side gate control and for high-side gate control. The PWM polarities register controls the polarity of other control signals as well. PWM\_POLARITIES [ 1 ] controls the polarity of the logic level high side gate control signal. PWM\_POLARITIES [ 0 ] controls the polarity of the logic level low side gate control signal.

Figure 36: PWM Gate Driver Control Polarities


PWM\_POLARITIES

| [ ]   |           |           |
|-------|-----------|-----------|
| 0 0   | PWM_H     | PWM_L     |
| 0 1   | PWM_H     | not PWM_L |
| 1 0   | not PWM_H | PWM_L     |
| 1 1   | not PWM_H | not PWM_L |

1...0

PWM\_HIGH\_SIDE

Table 24: Status Flags Register

PWM\_LOW\_SIDE


PIDa

Ua

FOC3

Ua, Up

Uu, Uv, Un

## 4.9.2 PWMEngine and associated Motor Connectors

The PWM engine of the TMC4671 has eight gate control outputs to control up to four power MOS half bridges. For three-phase motors three half bridges are used (U, V, W). For two-phase stepper motors four half bridges are used for (U, V, W, Y). For DC motor control, the first two half bridges (U, V) are used.

Gate Control Signals

FOC3: 3 Phase Motor

FOC2: 2 Phase Stepper

FOC1: Single Phase DC Motor

Table 25: FOC321 Gate Control Signal Configurations

| PWM_UX1_H PWM_UX1_L   | U   | X1   | X1   |
|-----------------------|-----|------|------|
| PWM_VX2_H PWM_VX2_L   | V   | X2   | X2   |
| PWM_WY1_H PWM_WY1_L   | W   | Y1   | -    |
| PWM_Y2_H PWM_Y2_L     | -   | Y2   | -    |

For the DC motor current control (here named FOC1), the number of pole pairs is not relevant - in contrast to closed loop current control of two-phase stepper motors (FOC2) and three-phase permanent magnet motors (FOC3). For DC motor control, the number of pole pairs should be set to 1 to equal mechanical angle and electrical angle for velocity control and for position control.


Figure 37: FOC3 (three phase motor), FOC2 (two phase stepper motor), FOC1 (single phase DC motor)


PIDO

Ua

FOC2

PIDa

Ua

FOC1

PWM

PWM\_H

PWM\_L

PWM\_H\_BBM

PWM\_L\_BBM

## 4.9.3 PWMFrequency

PWM cycle tPWM

The PWM counter maximum length register PWM\_MAXCNT controls the PWM frequency. For a clock frequency fCLK = 25 MHz, the PWM frequency fPWM[Hz] = (4.0 · fCLK[Hz]) / (PWM\_MAXCNT + 1). With fCLK = 25 MHz and power-on reset (POR) default of PWM\_MAXCNT=3999, the PWM frequency fPWM = 25kHz. tPWM\_BBM\_H - tPWM\_BBM\_L

Note

The PWM frequency is the fundamental frequency of the control system. It can be changed at any time, also during motion for the classic PI controller structure. The advanced PI controller structure is tied to the PWM frequency and integrator gains have to be changed. Please make sure to set current measurement decimation rates to fit PWM period in high performance applications.

## 4.9.4 PWMResolution

The base resolution of the PWM is 12 bit internally mapped to 16 bit range. The minimal PWM increment is 20ns due to the symmetrical PWM with 100 MHz counter frequency. MAX\_PWMCNT = 4095 gives the full resolution of 12 bit with ≈ 25kHz w/ fCLK=25MHz. MAX\_PWMCNT=2047 results in 11 bit resolution, but with ≈ 50kHz w/ fCLK=25MHz. So the PWM\_MAXCNT defines the PWM frequency, but also affects the resolution of the PWM.

## 4.9.5 PWMModes

The power-on reset (POR) default of the PWM is OFF. The standard PWM scheme is the centered PWM. Passive braking and freewheeling modes are available on demand. Please refer to section 7 concerning the settings.

## 4.9.6 Break-Before-Make (BBM)

Oneregister controls BBM time for the high side, another register controls BBM time for the low side. The BBM times are programmable in 10ns steps. The BBM time can be set to zero for gate drivers that have their own integrated BBM timers.


Figure 38: BBM Timing


Info

Note

Measured BBM times at MOS-FET gates differ from programmed BBM times due to driver delays and possible additional gate driver BBM times. The programmed BBM times are for the digital control signals.

Too short BBM times cause electrical shortcuts of the MOS-FET bridges - so called shoot through - that short the power supply and might damage the power stage and the power supply.

## 4.9.7 Space Vector PWM (SVPWM)

A single bit enables the Space Vector PWM (SVPWM). No further settings are required for the space vector PWM - just ON or OFF. The power on default for the SVPWM is OFF. Space Vector PWM can be enabled to maximize voltage utilization in the case of an isolated star point of the motor. If the star point is not isolated, SVPWM might cause unintended current flows through the star point. Space Vector PWM is only used for three-phase motors. For other motors the SVPWM must be switched off.

Note

For engineering samples TMC4671-ES, the Space Vector PWM does not allow higher voltage utilization. This is fixed for the release version TMC4671-LA.

## 4.9.8 Real- and Integer-Conversions

Senseamps and their respective shunt resistors can deviate in their properties due to part tolerances or aging. However, their values must still be comparable. This is done by using a scaling factor for both ADCs in order to harmonize their signals.

The TMC4671 displays voltages and currents as integer values. The following tables show how one can convert integer values to real values, see table 26, and the other way round, see table 27. Equation 2 in section 4.5.0.1 describes the chain of gains and introduces ADC\_GAIN. This variable depends on resistance of the shuntresistor as well as the properties of the senseamplifier. It is needed for the current conversions. The voltage conversion depends on the supply voltage V M .

$$\text {monize their signals.} \\ \text {ADC_GAIN} _ { s \text {scaled} } = ( \text {ADC_GAIN} \cdot \frac { \text {ADC_SCALE} } { 2 5 6 } )$$

integer to real

| I uvw,real   | I uvw , s16 ADC _ GAIN scaled   |
|--------------|---------------------------------|
| I αβ ,real   | I αβ, s16 ADC _ GAIN scaled     |
| I dq,real    | I dq , s16 ADC _ GAIN scaled    |
| U dq,real    | U dq , s16 · V M 2 15           |
| U αβ ,real   | U αβ, s16 · V M 2 15            |
| FOC uvw,real | FOC uvw , s16 · V M 2 15        |
| PWM uvw,real | PWM uvw , s16 · V M 2 15        |

Table 26: Factors for integer to real conversion


real to integer

Table 27: Factors for real to integer conversion

| I uvw,s16   | I uvw , real · ADC _ GAIN scaled   |
|-------------|------------------------------------|
| I αβ ,s16   | I αβ, real · ADC _ GAIN scaled     |
| I dq,s16    | I dq , real · ADC _ GAIN scaled    |
| U dq,s16    | U dq , real · 2 15 V M             |
| U αβ ,s16   | U αβ, real · 2 15 V M              |
| FOC uvw,s16 | FOC uvw , real · 2 15 V M          |
| PWM uvw,s16 | PWM dq , real · 2 15 V M           |

The PWM value defines the outputvoltage. It is calculated using the content of register INTERIM\_DATA while INTERIM\_ADDR is 0x11 or 0x12. The s16 PWM value is converted to an u16 value by adding 0x8000. Equation 47 applies for the highside PWM when connected to a DC- or Stepper-motor as well as the three phases of a BLDC-motor when spacevector pwm is inactive:

$$U _ { \text {clamp} } = ( \text {PW} _ { \text {uv} , s | 6 } + 0 x 8 0 0 0 ) \cdot \frac { V _ { \text {M} } } { 2 ^ { 1 6 } }$$

$$U _ { \text {clamp} } = ( - P W M _ { u x w y , s 1 6 } + 0 x 8 0 0 ) \cdot \frac { V _ { M } } { 2 ^ { 1 6 } }$$

Equation 48 describes the outputvoltage on the clamps for the lowside PWM when connected to a DC- or Stepper-motor:

The following equation describes the integer to real transformation for three-phase spacevector-PWM:

$$F O C _ { \min } = & \min ( F O C _ { u } , F O C _ { v } , F O C _ { w } ) \\ F O C _ { \max } = & \max ( F O C _ { u } , F O C _ { v } , F O C _ { w } ) \\ U _ { \text {clamp} , u v w } = & \left ( \frac { 2 } { \sqrt { 3 } } \cdot ( P W M _ { u v w , s l6 } - \frac { F O C _ { \max } + F O C _ { \min } } { 2 } ) + 0 x 8 0 0 0 \right ) \cdot \frac { V _ { M } } { 2 ^ { 1 6 } }$$

## 5 Safety Functions

Internal hardware limiters for real time clipping and monitoring of interim values are available. LIMIT or LIMITS is part of register names of registers associated to internal limiters. Please refer to table 28.

Different safety functions are integrated and mapped to status bits. A programmable mask register selects bits for activation of the STATUS output.

Bit

Source

|   0 | pid_x_target_limit     |
|-----|------------------------|
|   1 | pid_x_target_ddt_limit |
|   2 | pid_x_errsum_limit     |
|   3 | pid_x_output_limit     |
|   4 | pid_v_target_limit     |


5

pid\_v\_target\_ddt\_limit

Table 28: Status Flags Register

|   6 | pid_v_errsum_limit      |
|-----|-------------------------|
|   7 | pid_v_output_limit      |
|   8 | pid_id_target_limit     |
|   9 | pid_id_target_ddt_limit |
|  10 | pid_id_errsum_limit     |
|  11 | pid_id_output_limit     |
|  12 | pid_iq_target_limit     |
|  13 | pid_iq_target_ddt_limit |
|  14 | pid_iq_errsum_limit     |
|  15 | pid_iq_output_limit     |
|  16 | ipark_cirlim_limit_u_d  |
|  17 | ipark_cirlim_limit_u_q  |
|  18 | ipark_cirlim_limit_u_r  |
|  19 | not_PLL_locked          |
|  20 | ref_sw_r                |
|  21 | ref_sw_h                |
|  22 | ref_sw_l                |
|  23 | ---                     |
|  24 | pwm_min                 |
|  25 | pwm_max                 |
|  26 | adc_i_clipped           |
|  27 | adc_aenc_clipped        |
|  28 | ENC_N                   |
|  29 | ENC2_N                  |
|  30 | AENC_N                  |
|  31 | reserved                |

All controllers have input limiters as offsets can be added to target values and they can be limited to remain in certain ranges. Also all controller outputs can be limited and the integrating parts (error sum) of the PI controllers are also limited to controller outputs. If d/dt-limiters are enabled they are also capable of limiting target values.

If one of these limiters gets active, the flag will go to high state. This is usually a normal operation, when controllers are working on the borders of their working area. With STATUS\_MASK register corresponding flags can be activated.


Other status flags go to high state whether the voltage limitation is reached (circular limiter in iPark transformation) or PWM is saturated (pwm\_min and pwm\_max). This is also usual operation as the current controller has to deal with voltage limitation at high velocity operation.

Remaining wd\_error status flag indicates an error on the clock input of the TMC4671 (see following section). Status flags register can be written directly. It is not possible to clear individual bits.

The user can also use the status output to generate an IRQ on reference switch or N-channel of encoder. Also ADC clipping can be monitored which is a good indicator of wrong or faulty behavior.


## 6 FOC Setup - How to Turn a Motor

This section summarizes the basic steps that are required to turn a motor with TMC4671. The wizard of the TMCL-IDE guides the user through theses basic steps. Schematics and Layout of the TMC4671 evaluation kit are open source and available for download from www.trinamic.com

TRINAMIC recommends to use a TMC4671 evaluation kit together with the TMCLIDE with its integrated wizards for initial evaluation and setup.

| Note   | IDE with its integrated wizards for initial evaluation and setup.   |
|--------|---------------------------------------------------------------------|

In order to create own application software please check TRINAMIC's API to reduce software development efforts.

The TMC4671 supports closed loop control of single phase DC motors, stepper motors, and three phase motors. The selection of the motor type defines the configuration of the gate control channels for the power stage and either the usage or bypass of FOC transformations (Clarke, Park, iPark, iClark).

## 6.1 Select Motor Type

## 6.1.1 FOC1 Setup - How to Turn a Single Phase DC Motor

From closed loop velocity control point of view and from closed loop position control point of view there is no difference between electronically FOC controlled BLDC motor or PMSM motor and a mechanical commutated DC motor with electronic closed loop current control.

In case of DC motor, the mechanical commutator of the DC motor realizes something like mechanical field oriented control where the TMC4671 just realizes closed loop current control of the DC motor. From FOC point of view, the FOC converts a brushless motor (BLDC) resp. Permanent Magnet Synchronous Motor (PMSM) into a closed loop current controlled DC motor.

## 6.1.2 FOC2 Setup - How to Turn a Two Phase Motor (Stepper)

The TMC4671 is able to turn a two-phase stepper motor with FOC by internal skip of Clarke transformation and iClarke transformation. A special feature of stepper motors is the high number of pole pairs (NPP) that are typical 50. For stepper motors it is usual to give the number of full steps (FS) per revolution, with NPP = (FS/revolution) / 4. A stepper with 200 full steps per revolution has 50 pole pairs.

## 6.1.3 FOC3 Setup - How to Turn a Three Phase Motor (PMSM or BLDC)

## 6.2 Set Number of Pole Pairs (NPP)

A three phase motor is the classical FOC controlled brushless motor. Users have to take care concerning number of pole pairs (NPP) and the number of poles (NP) with NPP = NP/2.

The number of (magnetic) pole pairs (NPP) is characteristic for each motor and it is essential for commutation of two phase motors and three phase motors with FOC. For DC motor the NPP is not important for commutation itself, but is should be set to one to have same scaling for electrical angle and mechanical angle.


## 6.3 Run Motor Open Loop

Initial turning a motor open loop is useful for determination of the association between phase voltage, phase currents and for position sensor setup. Position sensors that are mounted on a motor might have an opposite direction of rotation compared to the motor. The same direction of rotation is essential for the FOC. In addition, the phase shift between rotor angle and angle that is measured by a position sensor needs to be zero in best case. Otherwise the motor is operated at lower efficiency or turns in wrong direction which causes instability.

## 6.3.1 Determination of Association between Phase Voltage and Phase Currents

For starters, the motor should be turned open loop to measure ADC offsets and set ADC scaler offset. Additionally, the open loop turn is useful to validate (or to determine) the association between motor phase currents and motor phase terminal voltages. This association is essential for the FOC. With proper ADC channel selection setup, voltage U\_UX1 is in phase with current I\_UX1, voltage U\_VX2 is in phase with current I\_VX2, and voltage U\_WY1 is in phase with I\_WY1. For two phase stepper motor, the voltage U\_Y2 is in phase with current I\_Y2. Only two currents are measured and the other current is calculated by TMC4671. For DC motor only one current is measured.

## 6.3.2 Determination of Direction of Rotation and Phase Shift of Angles

## 6.4 Selection of Position Sensors

For absolute position sensors like Hall sensors, the phase shift an the direction of rotation only need to be determined once initially. For relative position sensors, like incremental encoders, the direction of turning needs to be determined everytime after power cycle. The relative orientation between measured incremental encoder angle and rotor angle needs to be determined on each power-up.

For closed loop operation, the type of encoder (digital hall, ABN encoder, analog Hall, SinCos) needs to be set. For analog Hall signals or analog incremental encoders the user needs to adjust the analog ADC channels for the analog encoders - similar to ADC offset and ADC scaling as for current measuring ADC channels. The TMC4671 allows the selection of different types of position sensors for different tasks. One position sensor is for the inner FOC closed loop current control loop.

## 6.4.1 Selection of FOC sensor for PHI\_E

One sensor needs to be selected for the FOC to measure the electrical angle PHI\_E. This sensor is used for the inner closed loop control loop for closed loop current control.

## 6.4.2 Selection of sensor for VELOCITY

One sensor needs to be selected for measurement of velocity. This can be the sensor selected for measurement of PHI\_E but it is more common to use the mechanical angle PHI\_M for measurement of velocity. Using electrical angles can give advantages for applications with slow motion for NPP more than one because the minimum velocity in RPM [revolutions per minute] is one and the electrical angles have higher speed than mechanical angles.

## 6.4.3 Selection of sensor for POSITION

Onesensor needs to be selected for measurement of position of the rotor, the angle of the rotor. This can be the sensor selected for measurement PHI\_E but it is more usual to use the mechanical angle PHI\_M for measurement of position. For stepper motors it might make sense to select the electrical angle PHI\_E for


positioning to have a benefit from higher resolution using electrical angles. This is because each period electrical or mechanical - is normalized to 2 16 = 65536 positions.

## 6.5 Modes of Operation - (Open Loop), Torque, Velocity, Positioning

The TMC4671 can operate in torque mode, velocity mode, or position mode. The control loops (current, velocity, position) are cascaded, thus the outer loops depend on the tuning of the inner loops. So, the current loop must be adjusted first. The velocity loop must be adjusted after the current control loop is adjusted. The position control loop must be adjusted last.

## 6.6 Controller Tuning

## 7 Register Map

PI controller tuning is described throughout the control theory literature. In general there are two main strategies to tune the controllers. First strategy is to observe controller step response for different parameter sets and tune parameters to fit dynamics and settling time. With this approach sampling target and actual value as well as controller output (check for saturation) at fixed frequency is recommended. The USB-2-RTMI adapter in combination with the TMCL-IDE provide tuning tools to support this strategy. Another approach is to identify controller plant parameters and calculate controller parameters from these parameters. This is also supported by the TMCL-IDE for the current control loop. For the other control loops the first strategy is recommended.

The TMC4671 has an register address range of 128 addresses with registers up to 32 bit data width. Some registers hold 32 bit data fields, some hold 2 x 16 bit data fileds and other hold combinations of different data fields with individual data types. Data fields need to extracted by masking and shifting after read from a TMC4671 register within the application. Data fields need to be composed by masking and shifting by the application before writing into a TMC4671 register. Please check TRINAMIC's API to reduce software development efforts. This section describes the register bank of the TMC4671.

Section 7.2 is the detailed reference of all registers and the register fields.

Section 7.1 gives an overview over all registers. It is is intended to give an initial over view of all registers.

Section 7.3 gives the description of power-on-reset default values of all registers.


## 7.1 Register Map - Overview

TheTMC4671hasanaddressspaceof128addresses. Inordertodisplaymorethen128registers, socalled stacked registers were added. These are CHIPINFO\_DATA, ADC\_RAW\_DATA, PID\_ERROR\_DATA, CONFIG\_DATA and INTERIM\_DATA. These data registers display or give access to different subregisters according to their corresponding address registers (CHIPINFO\_ADDR, ADC\_RAW\_ADDR, PID\_ERROR\_ADDR, CONFIG\_ADDR and INTERIM\_ADDR). Read access to a subregister requires a write access to address register and a read access to the data register.

Registers in TMC4671 have different purposes. Some registers are used for test only, other can be used to monitor internal states (e.g. ADC values). Most registers are only accessed during initialisation (e.g. calibration or control parameters). Control registers are used for input of target values to controllers and should be updated regularly according to chosen motion modes (e.g PID\_VELOCITY\_TARGET should be updated in velocity mode). If users don't use a certain functional block they don't need to parametrize it.

Address

Registername

Access

Usage

| 0x00 h   | CHIPINFO_DATA             | R   | Test    |
|----------|---------------------------|-----|---------|
| 0x01 h   | CHIPINFO_ADDR             | RW  | Test    |
| 0x02 h   | ADC_RAW_DATA              | R   | Monitor |
| 0x03 h   | ADC_RAW_ADDR              | RW  | Monitor |
| 0x04 h   | dsADC_MCFG_B_MCFG_A       | RW  | Init    |
| 0x05 h   | dsADC_MCLK_A              | RW  | Init    |
| 0x06 h   | dsADC_MCLK_B              | RW  | Init    |
| 0x07 h   | dsADC_MDEC_B_MDEC_A       | RW  | Init    |
| 0x08 h   | ADC_I1_SCALE_OFFSET       | RW  | Init    |
| 0x09 h   | ADC_I0_SCALE_OFFSET       | RW  | Init    |
| 0x0A h   | ADC_I_SELECT              | RW  | Init    |
| 0x0B h   | ADC_I1_I0_EXT             | RW  | Test    |
| 0x0C h   | DS_ANALOG_INPUT_STAGE_CFG | RW  | Test    |
| 0x0D h   | AENC_0_SCALE_OFFSET       | RW  | Init    |
| 0x0E h   | AENC_1_SCALE_OFFSET       | RW  | Init    |
| 0x0F h   | AENC_2_SCALE_OFFSET       | RW  | Init    |
| 0x11 h   | AENC_SELECT               | RW  | Init    |
| 0x12 h   | ADC_IWY_IUX               | R   | Monitor |
| 0x13 h   | ADC_IV                    | R   | Monitor |
| 0x15 h   | AENC_WY_UX                | R   | Monitor |
| 0x16 h   | AENC_VN                   | R   | Monitor |
| 0x17 h   | PWM_POLARITIES            | RW  | Init    |
| 0x18 h   | PWM_MAXCNT                | RW  | Init    |
| 0x19 h   | PWM_BBM_H_BBM_L           | RW  | Init    |
| 0x1A h   | PWM_SV_CHOP               | RW  | Init    |


Address

Registername

Access

Usage

| 0x1B h   | MOTOR_TYPE_N_POLE_PAIRS        | RW   | Init              |
|----------|--------------------------------|------|-------------------|
| 0x1C h   | PHI_E_EXT                      | RW   | Test              |
| 0x1F h   | OPENLOOP_MODE                  | RW   | Init              |
| 0x20 h   | OPENLOOP_ACCELERATION          | RW   | Init              |
| 0x21 h   | OPENLOOP_VELOCITY_TARGET       | RW   | Init              |
| 0x22 h   | OPENLOOP_VELOCITY_ACTUAL       | RW   | Monitor           |
| 0x23 h   | OPENLOOP_PHI                   | RW   | Monitor/Test      |
| 0x24 h   | UQ_UD_EXT                      | RW   | Init/Test         |
| 0x25 h   | ABN_DECODER_MODE               | RW   | Init              |
| 0x26 h   | ABN_DECODER_PPR                | RW   | Init              |
| 0x27 h   | ABN_DECODER_COUNT              | RW   | Init/Test/Monitor |
| 0x28 h   | ABN_DECODER_COUNT_N            | RW   | Init/Test/Monitor |
| 0x29 h   | ABN_DECODER_PHI_E_PHI_M_OFFSET | RW   | Init              |
| 0x2A h   | ABN_DECODER_PHI_E_PHI_M        | R    | Monitor           |
| 0x2C h   | ABN_2_DECODER_MODE             | RW   | Init              |
| 0x2D h   | ABN_2_DECODER_PPR              | RW   | Init              |
| 0x2E h   | ABN_2_DECODER_COUNT            | RW   | Init/Test/Monitor |
| 0x2F h   | ABN_2_DECODER_COUNT_N          | RW   | Init/Test/Monitor |
| 0x30 h   | ABN_2_DECODER_PHI_M_OFFSET     | RW   | Init              |
| 0x31 h   | ABN_2_DECODER_PHI_M            | R    | Monitor           |
| 0x33 h   | HALL_MODE                      | RW   | Init              |
| 0x34 h   | HALL_POSITION_060_000          | RW   | Init              |
| 0x35 h   | HALL_POSITION_180_120          | RW   | Init              |
| 0x36 h   | HALL_POSITION_300_240          | RW   | Init              |
| 0x37 h   | HALL_PHI_E_PHI_M_OFFSET        | RW   | Init              |
| 0x38 h   | HALL_DPHI_MAX                  | RW   | Init              |
| 0x39 h   | HALL_PHI_E_INTERPOLATED_PHI_E  | R    | Monitor           |
| 0x3A h   | HALL_PHI_M                     | R    | Monitor           |
| 0x3B h   | AENC_DECODER_MODE              | RW   | Init              |
| 0x3C h   | AENC_DECODER_N_THRESHOLD       | RW   | Init              |
| 0x3D h   | AENC_DECODER_PHI_A_RAW         | R    | Monitor           |
| 0x3E h   | AENC_DECODER_PHI_A_OFFSET      | RW   | Init              |
| 0x3F h   | AENC_DECODER_PHI_A             | R    | Monitor           |
| 0x40 h   | AENC_DECODER_PPR               | RW   | Init              |


Address

Registername

Access

Usage

| 0x41 h   | AENC_DECODER_COUNT              | R   | Monitor      |
|----------|---------------------------------|-----|--------------|
| 0x42 h   | AENC_DECODER_COUNT_N            | RW  | Monitor/Init |
| 0x45 h   | AENC_DECODER_PHI_E_PHI_M_OFFSET | RW  | Init         |
| 0x46 h   | AENC_DECODER_PHI_E_PHI_M        | R   | Monitor      |
| 0x4D h   | CONFIG_DATA                     | RW  | Init         |
| 0x4E h   | CONFIG_ADDR                     | RW  | Init         |
| 0x50 h   | VELOCITY_SELECTION              | RW  | Init         |
| 0x51 h   | POSITION_SELECTION              | RW  | Init         |
| 0x52 h   | PHI_E_SELECTION                 | RW  | Init         |
| 0x53 h   | PHI_E                           | R   | Monitor      |
| 0x54 h   | PID_FLUX_P_FLUX_I               | RW  | Init         |
| 0x56 h   | PID_TORQUE_P_TORQUE_I           | RW  | Init         |
| 0x58 h   | PID_VELOCITY_P_VELOCITY_I       | RW  | Init         |
| 0x5A h   | PID_POSITION_P_POSITION_I       | RW  | Init         |
| 0x5D h   | PIDOUT_UQ_UD_LIMITS             | RW  | Init         |
| 0x5E h   | PID_TORQUE_FLUX_LIMITS          | RW  | Init         |
| 0x60 h   | PID_VELOCITY_LIMIT              | RW  | Init         |
| 0x61 h   | PID_POSITION_LIMIT_LOW          | RW  | Init         |
| 0x62 h   | PID_POSITION_LIMIT_HIGH         | RW  | Init         |
| 0x63 h   | MODE_RAMP_MODE_MOTION           | RW  | Init         |
| 0x64 h   | PID_TORQUE_FLUX_TARGET          | RW  | Control      |
| 0x65 h   | PID_TORQUE_FLUX_OFFSET          | RW  | Control      |
| 0x66 h   | PID_VELOCITY_TARGET             | RW  | Control      |
| 0x67 h   | PID_VELOCITY_OFFSET             | RW  | Control      |
| 0x68 h   | PID_POSITION_TARGET             | RW  | Control      |
| 0x69 h   | PID_TORQUE_FLUX_ACTUAL          | R   | Monitor      |
| 0x6A h   | PID_VELOCITY_ACTUAL             | R   | Monitor      |
| 0x6B h   | PID_POSITION_ACTUAL             | RW  | Monitor/Init |
| 0x6C h   | PID_ERROR_DATA                  | R   | Test         |
| 0x6D h   | PID_ERROR_ADDR                  | RW  | Test         |
| 0x6E h   | INTERIM_DATA                    | RW  | Monitor      |
| 0x6F h   | INTERIM_ADDR                    | RW  | Monitor      |
| 0x75 h   | ADC_VM_LIMITS                   | RW  | Init         |
| 0x76 h   | TMC4671_INPUTS_RAW              | R   | Test/Monitor |


Address

Registername

Access

Table 29: TMC4671 Registers

| 0x77 h   | TMC4671_OUTPUTS_RAW   | R   | Test/Monitor   |
|----------|-----------------------|-----|----------------|
| 0x78 h   | STEP_WIDTH            | RW  | Init           |
| 0x79 h   | UART_BPS              | RW  | Init           |
| 0x7B h   | GPIO_dsADCI_CONFIG    | RW  | Init           |
| 0x7C h   | STATUS_FLAGS          | RW  | Monitor        |
| 0x7D h   | STATUS_MASK           | RW  | Monitor        |

Usage


## 7.2 Register Map - Functional Description

DATA TYPE

| ADDR   | NAME              | (BIT MASK)   | FUNCTION                                                                                                            |
|--------|-------------------|--------------|---------------------------------------------------------------------------------------------------------------------|
| 0x00 h | CHIPINFO_DATA     |              | This register displays name and version information of the ac- cessed IC. It can be used for test of communication. |
|        | SI_TYPE           | u32(31:0)    | 0: Hardware type (ASCII).                                                                                           |
|        | SI_VERSION        | u32(31:0)    | 0: Hardware version (u16.u16).                                                                                      |
|        | SI_DATE           | u32(31:0)    | 0: Hardware date (nibble wise date stamp yyyymmdd).                                                                 |
|        | SI_TIME           | u32(31:0)    | 0: Hardware time (nibble wise time stamp -hhmmss)                                                                   |
|        | SI_VARIANT        | u32(31:0)    |                                                                                                                     |
|        | SI_BUILD          | u32(31:0)    |                                                                                                                     |
| 0x01 h | CHIPINFO_ADDR     |              | This register is used to change displayed information in register CHIPINFO_DATA.                                    |
|        | CHIP_INFO_ADDRESS | u8(7:0)      | 0: SI_TYPE 1: SI_VERSION 2: SI_DATE                                                                                 |
|        |                   |              | 3: SI_TIME                                                                                                          |
|        |                   |              | 4: SI_VARIANT                                                                                                       |
|        |                   |              | 5: SI_BUILD                                                                                                         |
| 0x02 h | ADC_RAW_DATA      |              | This registers displays ADC val- ues. Th displayed registers can be switched by register ADC_RAW_ ADDR.             |
|        | ADC_I0_RAW        | u16(15:0)    | Raw phase current I0                                                                                                |
|        | ADC_I1_RAW        | u16(31:16)   | Raw phase current I1                                                                                                |
|        | ADC_VM_RAW        | u16(15:0)    | Raw supply voltage value.                                                                                           |
|        | ADC_AGPI_A_RAW    | u16(31:16)   | Raw analog gpi A value.                                                                                             |
|        | ADC_AGPI_B_RAW    | u16(15:0)    | Raw analog gpi B value.                                                                                             |
|        | ADC_AENC_UX_RAW   | u16(31:16)   | Raw analog encoder signal.                                                                                          |
|        | ADC_AENC_VN_RAW   | u16(15:0)    | Raw analog encoder signal.                                                                                          |
|        | ADC_AENC_WY_RAW   | u16(31:16)   | Raw analog encoder signal.                                                                                          |
| 0x03 h | ADC_RAW_ADDR      |              | This register is used to change displayed information in register ADC_RAW_DATA.                                     |


ADC\_RAW\_ADDR

u8(7:0)

0: ADC\_I1\_RAW &amp; ADC\_I0\_RAW

|        |                                   |           | 1: ADC_AGPI_A_RAW & ADC_VM_ RAW 2: ADC_AENC_UX_RAW & ADC_ AGPI_B_RAW 3: ADC_AENC_WY_RAW & ADC_ AENC_VN_RAW                                                          |
|--------|-----------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x04 h | dsADC_MCFG_B_MCFG_A               |           | This register is used to configure internal ADCs (delta sigma modu- lators). Don't modify if you want to use internal Delta Sigma modu- lators (Standard use case). |
|        | cfg_dsmodulator_a                 | u2(1:0)   | 0: int. dsMOD 1: ext. MCLK input 2: ext. MCLK output 3: ext. CMP                                                                                                    |
|        | mclk_polarity_a                   | bit(2)    | 0: off 1: on                                                                                                                                                        |
|        | mdat_polarity_a                   | bit(3)    | 0: off 1: on                                                                                                                                                        |
|        | sel_nclk_mclk_i_a                 | bit(4)    | 0: off 1: on                                                                                                                                                        |
|        | cfg_dsmodulator_b                 | u2(17:16) | 0: int. dsMOD 1: ext. MCLK input 2: ext. MCLK output                                                                                                                |
|        | mclk_polarity_b                   | bit(18)   | 3: ext. CMP 0: off 1: on                                                                                                                                            |
|        | mdat_polarity_b sel_nclk_mclk_i_b | bit(19)   | 0: off 1: on 0: off                                                                                                                                                 |
|        | dsADC_MCLK_A                      | bit(20)   | 1: on Delta Sigma modulator clock. not modify if you use delta sigma modulators use case). 31                                                                       |
| 0x05 h | dsADC_MCLK_A                      | u32(31:0) | This register is used to modify Do internal (Standard dsADC_MCLK_A = (2 · f MCLK ) f CLK                                                                            |


0x06

dsADC\_MCLK\_B

This register

| h      |                     |            | Delta Sigma modulator clock. Do not modify if you use internal delta sigma modulators (Standard use case).                                                                                                                                        |
|--------|---------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|        | dsADC_MCLK_B        | u32(31:0)  | dsADC_MCLK_B = (2 31 · f MCLK ) f CLK                                                                                                                                                                                                             |
| 0x07 h | dsADC_MDEC_B_MDEC_A |            | This registerisusedtochangedec- imation rates of SINC3 filters for Delta Sigma modulators. Set val- ues according to actual PWM fre- quency. See functional descrip- tion of ADC engine.                                                          |
|        | dsADC_MDEC_A        | u16(15:0)  | 0: PWM synchronous, others ac- cording to register content                                                                                                                                                                                        |
|        | dsADC_MDEC_B        | u16(31:16) | 0: PWM synchronous, others ac- cording to register content                                                                                                                                                                                        |
| 0x08 h | ADC_I1_SCALE_OFFSET |            | This register is used to set calibra- tion data for ADC channel I1 (Off- set and amplitude correction).                                                                                                                                           |
|        | ADC_I1_OFFSET       | u16(15:0)  | Offset for current ADC channel 1.                                                                                                                                                                                                                 |
|        | ADC_I1_SCALE        | s16(31:16) | Scaling factor for current ADC channel 1.                                                                                                                                                                                                         |
| 0x09 h | ADC_I0_SCALE_OFFSET |            | This register is used to set calibra- tion data for ADC channel I0 (Off- set and amplitude correction).                                                                                                                                           |
|        | ADC_I0_OFFSET       | u16(15:0)  | Offset for current ADC channel 0.                                                                                                                                                                                                                 |
|        | ADC_I0_SCALE        | s16(31:16) | Scaling factor for current ADC channel 0.                                                                                                                                                                                                         |
| 0x0A h | ADC_I_SELECT        |            | This register is used to assign cor- rect ADC channel to PWM output channel. For each FOC input cur- rent either an ADC value or the calculated sum of the currents (I2) can be assigned to match internal data processing to power stage design. |
|        | ADC_I0_SELECT       | u8(7:0)    | Select input for raw current ADC_ I0_RAW.                                                                                                                                                                                                         |
|        |                     |            | 0: ADCSD_I0_RAW (sigma delta ADC)                                                                                                                                                                                                                 |
|        |                     |            | 1: ADCSD_I1_RAW (sigma delta ADC)                                                                                                                                                                                                                 |
|        |                     |            | 2: ADC_I0_EXT (from register)                                                                                                                                                                                                                     |
|        |                     |            | 3: ADC_I1_EXT (from register)                                                                                                                                                                                                                     |

is used

to modify


ADC\_I1\_SELECT

u8(15:8)

Select input for raw current ADC\_

|        |                                  |            | I1_RAW. 0: ADCSD_I0_RAW (sigma delta ADC)                                                                                                                                                                               |
|--------|----------------------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|        | ADC_I_UX_SELECT                  | u2(25:24)  | 1: ADCSD_I1_RAW (sigma delta ADC) 2: ADC_I0_EXT (from register) 3: ADC_I1_EXT (from register) 0: UX = ADC_I0 (default) 1: UX = ADC_I1 2: UX = ADC_I2                                                                    |
|        | ADC_I_V_SELECT                   | u2(27:26)  | 0: V = ADC_I0 1: V = ADC_I1 (default) 2: V = ADC_I2                                                                                                                                                                     |
|        | ADC_I_WY_SELECT                  | u2(29:28)  | 0: WY = ADC_I0 1: WY = ADC_I1 2: WY = ADC_I2 (default)                                                                                                                                                                  |
| 0x0B h | ADC_I1_I0_EXT                    |            | This register can be used to write ADC values via SPI in case exter- nal ADCs are used or controller cascade function shall be tested. using external ADCs will probably effect control performance is not recommended. |
|        | ADC_I0_EXT                       | u16(15:0)  | Register for write of ADC_I0 value from external source (eg. CPU).                                                                                                                                                      |
|        | ADC_I1_EXT                       | u16(31:16) | Register for write of ADC_I1 value from external source (eg. CPU).                                                                                                                                                      |
| 0x0C h | DS_ANALOG_INPUT_STAGE_CFG ADC_I0 | u4(3:0)    | This register is used to configure ADC channels for different input configurations and test modes. 0: INP vs. INN 1: GND vs. INN 2: VDD/4                                                                               |
|        |                                  |            | 3: 3*VDD/4                                                                                                                                                                                                              |
|        |                                  |            | 4: INP vs. GND                                                                                                                                                                                                          |
|        |                                  |            | 5: VDD/2 6: VDD/4                                                                                                                                                                                                       |
|        |                                  |            | 7: 3*VDD/4                                                                                                                                                                                                              |
|        | ADC_I1                           | u4(7:4)    | 0: INP vs. INN                                                                                                                                                                                                          |


1: GND vs. INN

|             |           | 2: VDD/4 3: 3*VDD/4           |
|-------------|-----------|-------------------------------|
|             |           | 4: INP vs. GND                |
|             |           | 5: VDD/2 6: VDD/4             |
|             |           | 7:                            |
|             |           | 3*VDD/4                       |
| ADC_VM      | u4(11:8)  | 0: INP vs. INN                |
|             |           | 1: GND vs. INN 2: VDD/4       |
|             |           | 3: 3*VDD/4                    |
|             |           | 4: INP vs. GND                |
|             |           | 5: VDD/2                      |
|             |           | 6: VDD/4                      |
|             |           | 7: 3*VDD/4                    |
| ADC_AGPI_A  | u4(15:12) | 0: INP vs. INN 1: GND vs. INN |
|             |           | 2: VDD/4                      |
|             |           | 3: 3*VDD/4 4: INP vs. GND     |
|             |           | 5: VDD/2 6: VDD/4             |
|             |           | 7: 3*VDD/4                    |
| ADC_AGPI_B  | u4(19:16) | 0: INP vs. INN                |
|             |           | 1: GND vs. INN                |
|             |           | 2: VDD/4                      |
|             |           | 3: 3*VDD/4                    |
|             |           | 4: INP vs. GND                |
|             |           | 5: VDD/2                      |
|             |           | 6: VDD/4                      |
|             |           | 7: 3*VDD/4                    |
| ADC_AENC_UX | u4(23:20) | 0: INP vs. INN                |
|             |           | 1: GND vs. INN                |
|             |           | 2: VDD/4                      |
|             |           | 3: 3*VDD/4                    |
|             |           | 4: INP vs. GND                |


5: VDD/2

|        |                     |            | 6: VDD/4                                                                                                  |
|--------|---------------------|------------|-----------------------------------------------------------------------------------------------------------|
|        |                     |            | 7: 3*VDD/4                                                                                                |
|        | ADC_AENC_VN         | u4(27:24)  | 0: INP vs. INN                                                                                            |
|        |                     |            | 1: GND vs. INN                                                                                            |
|        |                     |            | 2: VDD/4                                                                                                  |
|        |                     |            | 3: 3*VDD/4                                                                                                |
|        |                     |            | 4: INP vs. GND                                                                                            |
|        |                     |            | 5: VDD/2                                                                                                  |
|        |                     |            | 6: VDD/4                                                                                                  |
|        |                     |            | 7: 3*VDD/4                                                                                                |
|        | ADC_AENC_WY         | u4(31:28)  | 0: INP vs. INN                                                                                            |
|        |                     |            | 1: GND vs. INN                                                                                            |
|        |                     |            | 2: VDD/4                                                                                                  |
|        |                     |            | 3: 3*VDD/4                                                                                                |
|        |                     |            | 4: INP vs. GND                                                                                            |
|        |                     |            | 5: VDD/2                                                                                                  |
|        |                     |            | 6: VDD/4                                                                                                  |
|        |                     |            | 7: 3*VDD/4                                                                                                |
| 0x0D h | AENC_0_SCALE_OFFSET |            | This register is used to set calibra- tion data for ADC channel AENC 0 (Offset and amplitude correction). |
|        | AENC_0_OFFSET       | u16(15:0)  | Offset for Analog Encoder ADC channel 0.                                                                  |
|        | AENC_0_SCALE        | s16(31:16) | Scaling factor for Analog Encoder ADC channel 0.                                                          |
| 0x0E h | AENC_1_SCALE_OFFSET |            | This register is used to set calibra- tion data for ADC channel AENC 1 (Offset and amplitude correction). |
|        | AENC_1_OFFSET       | u16(15:0)  | Offset for Analog Encoder ADC channel 1.                                                                  |
|        | AENC_1_SCALE        | s16(31:16) | Scaling factor for Analog Encoder ADC channel 1.                                                          |
| 0x0F h | AENC_2_SCALE_OFFSET |            | This register is used to set calibra- tion data for ADC channel AENC 2 (Offset and amplitude correction). |
|        | AENC_2_OFFSET       | u16(15:0)  | Offset for Analog Encoder ADC channel 2.                                                                  |
|        | AENC_2_SCALE        | s16(31:16) | Scaling factor for Analog Encoder ADC channel 2.                                                          |


0x11

AENC\_SELECT

This register is used to select cor-

| h      |               |            | rect ADC to compensate wiring twists.                                                                          |
|--------|---------------|------------|----------------------------------------------------------------------------------------------------------------|
|        | AENC_0_SELECT | u8(7:0)    | Select analog encoder ADC chan- nel for raw analog encoder signal AENC_0_RAW.                                  |
|        |               |            | 0: <AENC_UX_RAW>                                                                                               |
|        |               |            | 1: AENC_VN_RAW                                                                                                 |
|        |               |            | 2: AENC_WY_RAW                                                                                                 |
|        | AENC_1_SELECT | u8(15:8)   | Select analog encoder ADC chan- nel for raw analog encoder signal AENC_1_RAW.                                  |
|        |               |            | 0: AENC_UX_RAW                                                                                                 |
|        |               |            | 1: <AENC_VN_RAW>                                                                                               |
|        |               |            | 2: AENC_WY_RAW                                                                                                 |
|        | AENC_2_SELECT | u8(23:16)  | Select analog encoder ADC chan- nel for raw analog encoder signal AENC_2_RAW.                                  |
|        |               |            | 0: AENC_UX_RAW                                                                                                 |
|        |               |            | 1: AENC_VN_RAW                                                                                                 |
|        |               |            | 2: <AENC_WY_RAW>                                                                                               |
| 0x12 h | ADC_IWY_IUX   |            | This register can be used to monitor phase current values (offset-compensated, scaled and correctly assigned). |
|        | ADC_IUX       | s16(15:0)  | Register of scaled current ADC value including signed added off- set as input for the FOC.                     |
|        | ADC_IWY       | s16(31:16) | Register of scaled current ADC value including signed added off- set as input for the FOC.                     |
| 0x13 h | ADC_IV        |            | This register can be used to monitor phase current ADC_IV (offset-compensated, scaled and correctly assigned). |
|        | ADC_IV        | s16(15:0)  | Register of scaled current ADC value including signed added off- set as input for the FOC.                     |
| 0x15 h | AENC_WY_UX    |            | This register displays AENC in- put signals (offset-compensated, scaled and correctly assigned).               |


AENC\_UX

s16(15:0)

Register of scaled analog encoder

|        |                   |            | value including signed added off- set as input for the interpolator.                                                                                 |
|--------|-------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
|        | AENC_WY           | s16(31:16) | Register of scaled analog encoder value including signed added off- set as input for the interpolator.                                               |
| 0x16 h | AENC_VN           |            | This register displays AENC input signal AENC_VN (offset- compensated, scaled and cor- rectly assigned).                                             |
|        | AENC_VN           | s16(15:0)  | Register of scaled analog encoder value including signed added off- set as input for the interpolator.                                               |
| 0x17 h | PWM_POLARITIES    |            | This register sets the polarity of PWM output signal to match gate driver.                                                                           |
|        | PWM_POLARITIES[0] | bit(0)     | Low Side gate control 0: off                                                                                                                         |
|        | PWM_POLARITIES[1] | bit(1)     | 1: on High Side gate control 0: off 1: on                                                                                                            |
| 0x18 h | PWM_MAXCNT        |            | This register is used to configure PWMoutput frequency.                                                                                              |
|        | PWM_MAXCNT        | u12(11:0)  | PWM maximum (count-1), PWM frequency is fPWM[Hz] = 100MHz/(PWM_MAXCNT+1)                                                                             |
| 0x19 h | PWM_BBM_H_BBM_L   |            | This register sets the BBM times forPWMoutputsignals. BBMtime must be matched power stage needs to avoid cross conduction in half bridge.            |
|        | PWM_BBM_L         | u8(7:0)    | Break Before Make time tBBM_ L[10ns] for low side MOS-FET gate control                                                                               |
|        | PWM_BBM_H         | u8(15:8)   | Break Before Make time tBBM_ H[10ns] for high side MOS-FET gate control                                                                              |
| 0x1A h | PWM_SV_CHOP       |            | This register is used to enable PWM, set different PWM test modes and switch on the SVPWM feature for higher voltage utiliza- tion (BLDC/PMSM only). |
|        | PWM_CHOP          | u8(7:0)    | PWM chopper mode, defining how to chopper                                                                                                            |


0: off, free running

|        | PWM_SV                   | bit(8)    | 1: off, low side permanent = ON 2: off, high side permanent = ON 3: off, free running 4: off, free running 5: low side chopper, high side off 6: high side chopper, low side off 7: centered PWMfor FOC use Space VectorPWM 0: Space Vector PWMdisabled 1: Space Vector PWMenabled This register is used to set motor   |
|--------|--------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x1B h | MOTOR_TYPE_N_POLE_PAIRS  |           | type and number of pole pairs.                                                                                                                                                                                                                                                                                          |
|        | N_POLE_PAIRS             | u16(15:0) | Number n of pole pairs of the mo- tor for calcualtion phi_e = phi_m · N_POLE_PAIRS.                                                                                                                                                                                                                                     |
|        | MOTOR_TYPE               | u8(23:16) | 0: No motor 1: Single phase DC 2: Two phase Stepper 3: Three phase BLDC                                                                                                                                                                                                                                                 |
| 0x1C h | PHI_E_EXT                |           | This register is used to set an elec- trical angle for SWmodewhenen- coder is connected to MCU and not to TMC4671.                                                                                                                                                                                                      |
|        | PHI_E_EXT                | s16(15:0) | Electrical angle phi_e_ext for ex- ternal writing into this register.                                                                                                                                                                                                                                                   |
| 0x1F h | OPENLOOP_MODE            |           | This register is used to change di- rection of openloop angle.                                                                                                                                                                                                                                                          |
|        | OPENLOOP_PHI_DIRECTION   | bit(12)   | Open loop phi direction. 0: positive                                                                                                                                                                                                                                                                                    |
|        |                          |           | 1: negative                                                                                                                                                                                                                                                                                                             |
| 0x20 h | OPENLOOP_ACCELERATION    |           | This register is used to change ac- celeration when openloop angle velocity should change.                                                                                                                                                                                                                              |
|        | OPENLOOP_ACCELERATION    | u32(31:0) | Acceleration of open loop phi.                                                                                                                                                                                                                                                                                          |
| 0x21 h | OPENLOOP_VELOCITY_TARGET |           | This register is used to set a target velocity for openloop angle gen- erator. The velocity is ramped up and down according to OPEN- LOOP_ACCELERATION and PID_ VELOCITY_LIMIT.                                                                                                                                         |


OPENLOOP\_VELOCITY\_TARGET

s32(31:0)

Target velocity of open loop phi.

| 0x22 h   | OPENLOOP_VELOCITY_ACTUAL OPENLOOP_VELOCITY_ACTUAL   | s32(31:0)   | This register displays actual open- loop angle velocity in RPM. Actual velocity of open loop gener- ator.                         |
|----------|-----------------------------------------------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------|
| 0x23 h   | OPENLOOP_PHI                                        |             | This register displays actual out- put of openloop angle generator                                                                |
|          | OPENLOOP_PHI                                        | s16(15:0)   | Angle phi open loop (either mapped to electrical angel phi_e or mechanical angle phi_m).                                          |
| 0x24 h   | UQ_UD_EXT                                           |             | This register is used to set voltage values for openllop current con- trol mode (UQ_UD_EXT_MODE).                                 |
|          | UD_EXT                                              | s16(15:0)   | External writable parameter for open loop voltage control mode, usefull during system setup, U_D component.                       |
|          | UQ_EXT                                              | s16(31:16)  | External writable parameter for open loop voltage control mode, usefull during system setup, U_Q component.                       |
| 0x25 h   | ABN_DECODER_MODE                                    |             | This register is used to configure decoder input signals and Npulse action as well as count direction.                            |
|          | apol                                                | bit(0)      | Polarity of A pulse. 0: off 1: on                                                                                                 |
|          | bpol                                                | bit(1)      | Polarity of B pulse. 0: off 1: on                                                                                                 |
|          | npol                                                | bit(2)      | Polarity of N pulse. 0: off 1: on                                                                                                 |
|          | use_abn_as_n                                        | bit(3)      | N and A and B 0: Ignore A and B polarity with Npulse = N                                                                          |
|          | cln                                                 | bit(8)      | 1: Npulse = N and A and B Write direction at Npulse event between ABN_DECODER_COUNT_ N and ABN_DECODER_COUNT. 0: COUNT => COUNT_N |
|          |                                                     |             | 1: COUNT_N => COUNT                                                                                                               |


direction bit(12)

Decoder count direction.

|        |                                |            | 0: positive 1: negative                                                                                                                                                   |
|--------|--------------------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x26 h | ABN_DECODER_PPR                |            | This register is used to set PPR number of encoder.                                                                                                                       |
|        | ABN_DECODER_PPR                | u24(23:0)  | Decoder pulses per mechanical revolution.                                                                                                                                 |
| 0x27 h | ABN_DECODER_COUNT              |            | This register displays the actual count of encoder steps. It can be overwritten for initialization.                                                                       |
|        | ABN_DECODER_COUNT              | u24(23:0)  | Raw decoder count; the digital de- coder engine counts modulo (de- coder_ppr).                                                                                            |
| 0x28 h | ABN_DECODER_COUNT_N            |            | This register displays the count value at last N pulse event. It can also be used to overwrite Decoder count at Npulse evenet accroding to decoder mode register setting. |
|        | ABN_DECODER_COUNT_N            | u24(23:0)  | Decoder count latched onNpulse, when N pulse clears decoder_ count also decoder_count_n is 0.                                                                             |
| 0x29 h | ABN_DECODER_PHI_E_PHI_M_OFFSET |            | This register can beusedtosetoff- sets for electrical and mechanical angle calculated from decoder.                                                                       |
|        | ABN_DECODER_PHI_M_OFFSET       | s16(15:0)  | ABN_DECODER_PHI_M_OFFSET to shift (rotate) angleDECODER_PHI_ M.                                                                                                           |
|        | ABN_DECODER_PHI_E_OFFSET       | s16(31:16) | ABN_DECODER_PHI_E_OFFSET to shift (rotate) angleDECODER_PHI_ E.                                                                                                           |
| 0x2A h | ABN_DECODER_PHI_E_PHI_M        |            | This register displays actual angle values for ABN encoder.                                                                                                               |
|        | ABN_DECODER_PHI_M              | s16(15:0)  | ABN_DECODER_PHI_M = ABN_ DECODER_COUNT * 2^16 / ABN_ DECODER_PPR + ABN_DECODER_ PHI_M_OFFSET;                                                                             |
|        | ABN_DECODER_PHI_E              | s16(31:16) | ABN_DECODER_PHI_E = (ABN_ DECODER_PHI_M * N_POLE_ PAIRS_) + ABN_DECODER_PHI_E_ OFFSET                                                                                     |
| 0x2C h | ABN_2_DECODER_MODE             |            | This register is used to configure decoder input signals and Npulse action as well as count direction. A pulse.                                                           |
|        | apol                           | bit(0)     | Polarity of 0: off                                                                                                                                                        |


1: on

|        | bpol                  | bit(1)    | Polarity of B pulse. 0: off                                                                                                                                               |
|--------|-----------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|        |                       |           | 1: on                                                                                                                                                                     |
|        | npol                  | bit(2)    | Polarity of N pulse. 0: off                                                                                                                                               |
|        |                       |           | 1: on                                                                                                                                                                     |
|        | use_abn_as_n          | bit(3)    | 0: Ignore A and B polarity with Npulse = N, 1 : Npulse = N and A and B                                                                                                    |
|        |                       |           | 0: Ignore A and B polarity with Npulse = N B                                                                                                                              |
|        |                       |           | 1: Npulse = N and A and                                                                                                                                                   |
|        | cln                   | bit(8)    | Write direction at Npulse event be- tween ABN_2_DECODER_COUNT_ N and ABN_2_DECODER_COUNT.                                                                                 |
|        |                       |           | 0: COUNT => COUNT_N 1: COUNT_N => COUNT                                                                                                                                   |
|        | direction             | bit(12)   | Decoder count direction. 0: positive                                                                                                                                      |
|        |                       |           | 1: negative                                                                                                                                                               |
| 0x2D h | ABN_2_DECODER_PPR     |           | This register is used to set PPR number of encoder.                                                                                                                       |
|        | ABN_2_DECODER_PPR     | u24(23:0) | Decoder_2 pules per mechanical revolution. This 2nd ABN encoder interface is for positioning or ve- locity control but NOT for motor commutation.                         |
| 0x2E h | ABN_2_DECODER_COUNT   |           | This register displays the actual count of encoder steps. It can be overwritten for initialization.                                                                       |
|        | ABN_2_DECODER_COUNT   | u24(23:0) | Raw decoder_2 count; the digi- taldecoderenginecountsmodulo (decoder_2_ppr).                                                                                              |
| 0x2F h | ABN_2_DECODER_COUNT_N |           | This register displays the count value at last N pulse event. It can also be used to overwrite decoder count at N pulse event according to decoder mode register setting. |
|        | ABN_2_DECODER_COUNT_N | u24(23:0) | Decoder_2 count latched on N pulse, when N pulse clears de- coder_2_count also decoder_2_ count_n is 0.                                                                   |


0x30

ABN\_2\_DECODER\_PHI\_M\_OFFSET

This register can be used to set off-

| h      | ABN_2_DECODER_PHI_M_OFFSET                                           | s16(15:0)                       | sets for electrical and mechanical angle calculated from decoder. ABN_2_DECODER_PHI_M_OFFSET to shift (rotate) angle DECODER_ 2_PHI_M.                           |
|--------|----------------------------------------------------------------------|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x31 h | ABN_2_DECODER_PHI_M ABN_2_DECODER_PHI_M                              | s16(15:0)                       | This register displays actual angle values for ABN encoder. ABN_2_DECODER_PHI_M = ABN_ 2_DECODER_COUNT * 2^16 / ABN_2_DECODER_PPR + ABN_2_ DECODER_PHI_M_OFFSET; |
| 0x33 h | HALL_MODE polarity                                                   | bit(0)                          | This register is used to set basic settings for the digital Hall inter- face. polarity 0: off 1: on                                                              |
|        | synchronous PWMsampling                                              | bit(4)                          | enable sampling synchronous to PWM 0: off                                                                                                                        |
|        | interpolation                                                        | bit(8)                          | 1: on interpolation 0: off 1: on                                                                                                                                 |
|        | direction                                                            | bit(12)                         | direction 0: off 1: on                                                                                                                                           |
| 0x34 h | HALL_BLANK HALL_POSITION_060_000 HALL_POSITION_000 HALL_POSITION_060 | u12(27:16) s16(15:0) s16(31:16) | tBLANK = 10ns * HALL_BLANK This register is used to calibrate hall sensor offset. s16 hall sensor position at 0° s16 hall sensor position at 60°.                |
| 0x35 h | HALL_POSITION_180_120 HALL_POSITION_120 HALL_POSITION_180            | s16(15:0) s16(31:16)            | This register is used to calibrate hall sensor offset. s16 hall sensor position at 120°. s16 hall sensor position at 180°.                                       |
| 0x36 h | HALL_POSITION_300_240 HALL_POSITION_240                              | s16(15:0)                       | This register is used to calibrate hall sensor offset. s16 hall sensor position at 240°.                                                                         |


HALL\_POSITION\_300

s16(31:16)

s16 hall sensor position at 300°.

| 0x37 h   | HALL_PHI_E_PHI_M_OFFSET       |            | This register is used to set offsets for calculated angles from hall in- terface.                                   |
|----------|-------------------------------|------------|---------------------------------------------------------------------------------------------------------------------|
|          | HALL_PHI_M_OFFSET             | s16(15:0)  | Offset of mechanical angle hall_ phi_m of hall decoder.                                                             |
|          | HALL_PHI_E_OFFSET             | s16(31:16) | Offset for electrical angle hall_phi_ e of hall decoder.                                                            |
| 0x38 h   | HALL_DPHI_MAX                 |            | This register is used to set a maxim difference of two hall sen- sor transitions for Hall position ex- trapolation. |
|          | HALL_DPHI_MAX                 | u16(15:0)  | Maximumdxforinterpolation (de- fault for digital hall: u16/6).                                                      |
| 0x39 h   | HALL_PHI_E_INTERPOLATED_PHI_E |            | This register displays interpolated and raw angle of Hall interface.                                                |
|          | HALL_PHI_E                    | s16(15:0)  | Raw electrical angle hall_phi_e of hall decoder, selection pro- grammed via HALL_MODE control bit.                  |
|          | HALL_PHI_E_INTERPOLATED       | s16(31:16) | Interpolated electrical angle hall_ phi_e_interpolated, selection pro- grammed via HALL_MODE control bit.           |
| 0x3A h   | HALL_PHI_M                    |            | This register displays the mechan- ical angle calculated in Hall sensor interface.                                  |
|          | HALL_PHI_M                    | s16(15:0)  | Mechanical angle hall_phi_m of hall decoder.                                                                        |
| 0x3B h   | AENC_DECODER_MODE             |            | This register sets basic informa- tion for the analog encoder inter- face.                                          |
|          | AENC_DECODER_MODE[0]          | bit(0)     | 120deg_n90deg 0: 90 degree 1: 120 degree                                                                            |
|          | AENC_DECODER_MODE[12]         | bit(12)    | decoder count direction 0: positive 1: negative                                                                     |
| 0x3C h   | AENC_DECODER_N_THRESHOLD      |            | This registers sets analog encoder N pulse processing function.                                                     |


AENC\_DECODER\_N\_THRESHOLD

u16(15:0)

Threshold for

generating of N

|        |                                 |            | pulse from analog AENC_N signal (only neededfor analog SinCos en- coders with analog N signal).                                                                                                                  |
|--------|---------------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x3D h | AENC_DECODER_PHI_A_RAW          |            | Displays raw angle after ATAN2 calculation.                                                                                                                                                                      |
|        | AENC_DECODER_PHI_A_RAW          | s16(15:0)  | Raw analog angle phi calculated from analog AENC inputs (analog hall, analog SinCos, ...).                                                                                                                       |
| 0x3E h | AENC_DECODER_PHI_A_OFFSET       |            | This register sets the offset of PHI_ A for phase alignment.                                                                                                                                                     |
|        | AENC_DECODER_PHI_A_OFFSET       | s16(15:0)  | Offset for angle phi from analog decoder (analog hall, analog Sin- Cos, ...).                                                                                                                                    |
| 0x3F h | AENC_DECODER_PHI_A              |            | This register displays offset com- pensated PHI_A angle.                                                                                                                                                         |
|        | AENC_DECODER_PHI_A              | s16(15:0)  | Resulting phi available fortheFOC (phi_e might need to be calculated from this angle via aenc_decoder_ ppr, for analog hall sensors phi_a might be used directly as phi_e de- pends on analog hall signal type). |
| 0x40 h | AENC_DECODER_PPR                |            | This register sets the number of periods per revolution for analog encoder.                                                                                                                                      |
|        | AENC_DECODER_PPR                | s16(15:0)  | Number of periods per revolution also called lines per revolution (dif- ferent nomenclatur compared to digital ABN encoders).                                                                                    |
| 0x41 h | AENC_DECODER_COUNT              |            | Displays the count value of Analog encoder periods.                                                                                                                                                              |
|        | AENC_DECODER_COUNT              | s32(31:0)  | Decoder position, raw unscaled.                                                                                                                                                                                  |
| 0x42 h | AENC_DECODER_COUNT_N            |            | Displays the count value at last N pulse event. Can also be used to auto-overwrite decoder count at N pulse event.                                                                                               |
|        | AENC_DECODER_COUNT_N            | s32(31:0)  | Latched decoder position on ana- log N pulse event.                                                                                                                                                              |
| 0x45 h | AENC_DECODER_PHI_E_PHI_M_OFFSET |            | This register sets offsets for elec- trical and mechanical angle calcu- lated from AENC interface.                                                                                                               |
|        | AENC_DECODER_PHI_M_OFFSET       | s16(15:0)  | Offset for mechanical angle phi_ m.                                                                                                                                                                              |
|        | AENC_DECODER_PHI_E_OFFSET       | s16(31:16) | Offset for electrical angle phi_e.                                                                                                                                                                               |


0x46

AENC\_DECODER\_PHI\_E\_PHI\_M

Displays actual

| h      |                    |            | analog encoder interface.                                                                                                  |
|--------|--------------------|------------|----------------------------------------------------------------------------------------------------------------------------|
|        | AENC_DECODER_PHI_M | s16(15:0)  | Resulting angle phi_m.                                                                                                     |
|        | AENC_DECODER_PHI_E | s16(31:16) | Resulting angle phi_e.                                                                                                     |
| 0x4D h | CONFIG_DATA        |            | This multi-purpose register is used to set configuration param- eters of controller cascade and input signal conditioning. |
|        | biquad_x_a_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_x_a_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_x_b_0       | s32(31:0)  |                                                                                                                            |
|        | biquad_x_b_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_x_b_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_x_enable    | bit(31)    | 0: off                                                                                                                     |
|        |                    |            | 1: on                                                                                                                      |
|        | biquad_v_a_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_v_a_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_v_b_0       | s32(31:0)  |                                                                                                                            |
|        | biquad_v_b_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_v_b_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_v_enable    | bit(31)    | 0: off                                                                                                                     |
|        |                    |            | 1: on                                                                                                                      |
|        | biquad_t_a_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_t_a_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_t_b_0       | s32(31:0)  |                                                                                                                            |
|        | biquad_t_b_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_t_b_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_t_enable    | bit(31)    | 0: off                                                                                                                     |
|        |                    |            | 1: on                                                                                                                      |
|        | biquad_f_a_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_f_a_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_f_b_0       | s32(31:0)  |                                                                                                                            |
|        | biquad_f_b_1       | s32(31:0)  |                                                                                                                            |
|        | biquad_f_b_2       | s32(31:0)  |                                                                                                                            |
|        | biquad_f_enable    | bit(31)    | 0: off                                                                                                                     |
|        |                    |            | 1: on                                                                                                                      |
|        | prbs_amplitude     | s32(31:0)  |                                                                                                                            |

angle values

of


prbs\_down\_sampling\_ratio s32(31:0)

| ref_switch_config                      | u16(15:0)          |                                                                                                                                                                                                                                     |
|----------------------------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Encoder_Init_hall_Enable               | bit(0)             | 0: off 1: on                                                                                                                                                                                                                        |
| SINGLE_PIN_IF_CFG SINGLE_PIN_IF_STATUS | u8(7:0) u16(31:16) |                                                                                                                                                                                                                                     |
| SINGLE_PIN_IF_OFFSET                   | u16(15:0)          | Offset for scaling of Single pin In- terface input                                                                                                                                                                                  |
| SINGLE_PIN_IF_SCALE                    | s16(31:16)         | Gain factor of Single pin Interface input                                                                                                                                                                                           |
| CURRENT_I_nQ8.8_Q4.12                  | bit(0)             | If this bit is set Q4.12 representa- tion of I parameter for torque/flux control is used. If bit is not set Q8.8 representation is used 0: Q8.8 representation is used                                                              |
| CURRENT_P_nQ8.8_Q4.12                  | bit(1)             | 1: Q4.12 representation is used If this bit is set Q4.12 represen- tation of P for parameter for torque/flux control is used. If bit is not set Q8.8 representation is used 0: Q8.8 representation is used                          |
| VELOCITY_I_nQ8.8_Q4.12                 | bit(2)             | 1: Q4.12 representation is used If this bit is set Q4.12 represen- tation of I parameter for velocity control is used. If bit is not set Q8.8 representation is used 0: Q8.8 representation is used                                 |
| VELOCITY_P_nQ8.8_Q4.12                 | bit(3)             | 1: Q4.12 representation is used If this bit is set Q4.12 representa- tion of P for parameter for veloc- ity control is used. If bit is not set Q8.8 representation is used 0: Q8.8 representation is used                           |
| POSITION_I_nQ8.8_Q4.12                 | bit(4)             | 1: Q4.12 representation is used If this bit is set Q4.12 represen- tation of I parameter for position control is used. If bit is not set Q8.8 representation is used 0: Q8.8 representation is used 1: Q4.12 representation is used |


POSITION\_P\_nQ8.8\_Q4.12

bit(5)

If this bit is set Q4.12 representa-

|        |             |           | tion of P for parameter for posi- tion control is used. If bit is not set Q8.8 representation is used 0: Q8.8 representation is used 1: Q4.12 representation is used   |
|--------|-------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x4E h | CONFIG_ADDR |           | This register is used to select func- tion of CONFIG_DATA register.                                                                                                    |
|        | CONFIG_ADDR | u32(31:0) | 1: biquad_x_a_1 2: biquad_x_a_2                                                                                                                                        |
|        |             |           | 4: biquad_x_b_0                                                                                                                                                        |
|        |             |           | 5: biquad_x_b_1                                                                                                                                                        |
|        |             |           | 6: biquad_x_b_2                                                                                                                                                        |
|        |             |           | 7: biquad_x_enable                                                                                                                                                     |
|        |             |           | 9: biquad_v_a_1                                                                                                                                                        |
|        |             |           | 10: biquad_v_a_2                                                                                                                                                       |
|        |             |           | 12: biquad_v_b_0                                                                                                                                                       |
|        |             |           | 13: biquad_v_b_1                                                                                                                                                       |
|        |             |           | 14: biquad_v_b_2                                                                                                                                                       |
|        |             |           | 15: biquad_v_enable                                                                                                                                                    |
|        |             |           | 17: biquad_t_a_1                                                                                                                                                       |
|        |             |           | 18: biquad_t_a_2                                                                                                                                                       |
|        |             |           | 20: biquad_t_b_0                                                                                                                                                       |
|        |             |           | 21: biquad_t_b_1                                                                                                                                                       |
|        |             |           | 22: biquad_t_b_2                                                                                                                                                       |
|        |             |           | 23: biquad_t_enable                                                                                                                                                    |
|        |             |           | 25: biquad_f_a_1                                                                                                                                                       |
|        |             |           | 26: biquad_f_a_2                                                                                                                                                       |
|        |             |           | 28: biquad_f_b_0                                                                                                                                                       |
|        |             |           | 29: biquad_f_b_1                                                                                                                                                       |
|        |             |           | 30: biquad_f_b_2                                                                                                                                                       |
|        |             |           | 31: biquad_f_enable                                                                                                                                                    |
|        |             |           | 32: prbs_amplitude                                                                                                                                                     |
|        |             |           | 33: prbs_down_sampling_ratio 51: ref_switch_config                                                                                                                     |
|        |             |           | 52: Encoder_Init_hall_Enable                                                                                                                                           |
|        |             |           | 60: SINGLE_PIN_IF_STATUS_CFG                                                                                                                                           |


61: SINGLE\_PIN\_IF\_SCALE\_OFFSET

|        |                          |          | 62: ADVANCED_PI_REPRESENT.                                                                                |
|--------|--------------------------|----------|-----------------------------------------------------------------------------------------------------------|
| 0x50 h | VELOCITY_SELECTION       |          | This register is used to select an angle signal for the velocity con- trol loop and velocity calculation. |
|        | VELOCITY_SELECTION       | u8(7:0)  | Selects the source of the velocity source for velocity measurement.                                       |
|        |                          |          | 0: PHI_E_SELECTION                                                                                        |
|        |                          |          | 1: phi_e_ext                                                                                              |
|        |                          |          | 2: phi_e_openloop                                                                                         |
|        |                          |          | 3: phi_e_abn                                                                                              |
|        |                          |          | 4: reserved                                                                                               |
|        |                          |          | 5: phi_e_hal                                                                                              |
|        |                          |          | 6: phi_e_aenc                                                                                             |
|        |                          |          | 7: phi_a_aenc                                                                                             |
|        |                          |          | 8: reserved                                                                                               |
|        |                          |          | 9: phi_m_abn                                                                                              |
|        |                          |          | 10: phi_m_abn_2                                                                                           |
|        |                          |          | 11: phi_m_aenc                                                                                            |
|        |                          |          | 12: phi_m_hal                                                                                             |
|        | VELOCITY_METER_SELECTION | u8(15:8) | 0: default 1: advanced                                                                                    |
| 0x51 h | POSITION_SELECTION       |          | This register is used to select an angle signal for the position calcu- lation and control loop.          |
|        | POSITION_SELECTION       | u8(7:0)  | 0: phi_e selected via PHI_E_ SELECTION                                                                    |
|        |                          |          | 1: phi_e_ext                                                                                              |
|        |                          |          | 2: phi_e_openloop                                                                                         |
|        |                          |          | 3: phi_e_abn                                                                                              |
|        |                          |          | 4: reserved                                                                                               |
|        |                          |          | 5: phi_e_hal                                                                                              |
|        |                          |          | 6: phi_e_aenc                                                                                             |
|        |                          |          | 7: phi_a_aenc                                                                                             |
|        |                          |          | 8: reserved                                                                                               |
|        |                          |          | 9: phi_m_abn                                                                                              |
|        |                          |          | 10: phi_m_abn_2                                                                                           |
|        |                          |          | 11: phi_m_aenc                                                                                            |


12: phi\_m\_hal

| 0x52 h   | PHI_E_SELECTION           |            | This register is used to select an angle signal for FOC transforma- tion as electrical angle of the mo- tor.                                                |
|----------|---------------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
|          | PHI_E_SELECTION           | u8(7:0)    | 0: reserved 1: phi_e_ext                                                                                                                                    |
|          |                           |            | 2: phi_e_openloop                                                                                                                                           |
|          |                           |            | 3: phi_e_abn                                                                                                                                                |
|          |                           |            | 4: reserved                                                                                                                                                 |
|          |                           |            | 5: phi_e_hal                                                                                                                                                |
|          |                           |            | 6: phi_e_aenc                                                                                                                                               |
|          |                           |            | 7: phi_a_aenc                                                                                                                                               |
| 0x53 h   | PHI_E                     |            | This register displays the actual chosen electrical angle value.                                                                                            |
|          | PHI_E                     | s16(15:0)  | Angle used for the inner FOCloop.                                                                                                                           |
| 0x54 h   | PID_FLUX_P_FLUX_I         |            | This registers sets control param- eters for flux controller.                                                                                               |
|          | PID_FLUX_I                | s16(15:0)  |                                                                                                                                                             |
|          | PID_FLUX_P                | s16(31:16) |                                                                                                                                                             |
| 0x56 h   | PID_TORQUE_P_TORQUE_I     |            | This registers sets control param- eters for torque controller.                                                                                             |
|          | PID_TORQUE_I              | s16(15:0)  |                                                                                                                                                             |
|          | PID_TORQUE_P              | s16(31:16) |                                                                                                                                                             |
| 0x58 h   | PID_VELOCITY_P_VELOCITY_I |            | This registers sets control param- eters for velocity controller.                                                                                           |
|          | PID_VELOCITY_I            | s16(15:0)  |                                                                                                                                                             |
|          | PID_VELOCITY_P            | s16(31:16) |                                                                                                                                                             |
| 0x5A h   | PID_POSITION_P_POSITION_I |            | This registers sets control param- eters for position controller.                                                                                           |
|          | PID_POSITION_I            | s16(15:0)  |                                                                                                                                                             |
|          | PID_POSITION_P            | s16(31:16) |                                                                                                                                                             |
| 0x5D h   | PIDOUT_UQ_UD_LIMITS       |            | This register sets the output volt- age/duty cycle limit for the current controllers. iPARK CIRLIM block limits voltage output vector length to this value. |


PIDOUT\_UQ\_UD\_LIMITS

s16(15:0)

Two dimensional circular limiter

|        |                         |           | for inputs of iPark. HINT: The ab- solute value of the register is used (possible values: 0 ... 32767).                                          |
|--------|-------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x5E h | PID_TORQUE_FLUX_LIMITS  |           | This register is used to set target current limit for both controllers.                                                                          |
|        | PID_TORQUE_FLUX_LIMITS  | u16(15:0) | PID torque limt and PID flux limit, limits the target values coming from the target registers.                                                   |
| 0x60 h | PID_VELOCITY_LIMIT      |           | This registerisusedtosetanabso- lute velocity limit for velocity con- troller input.                                                             |
|        | PID_VELOCITY_LIMIT      | u32(31:0) | Velocity limit.                                                                                                                                  |
| 0x61 h | PID_POSITION_LIMIT_LOW  |           | This register is used to set a lower limit for position controller input.                                                                        |
|        | PID_POSITION_LIMIT_LOW  | s32(31:0) | Position limit low, programmable position barrier.                                                                                               |
| 0x62 h | PID_POSITION_LIMIT_HIGH |           | This register is usedtoset a higher limit for position controller input.                                                                         |
|        | PID_POSITION_LIMIT_HIGH | s32(31:0) | Position limit high, programmable position barrier.                                                                                              |
| 0x63 h | MODE_RAMP_MODE_MOTION   |           | This register is used to set a mo- tionmode, adownsamplingfactor for velocity and position control loop, and the PI controller struc- ture type. |
|        | MODE_MOTION             | u8(7:0)   | 0: stopped_mode 1: torque_mode                                                                                                                   |
|        |                         |           | 2: velocity_mode 3: position_mode                                                                                                                |
|        |                         |           | 4: prbs_flux_mode                                                                                                                                |
|        |                         |           | 5: prbs_torque_mode 6: prbs_velocity_mode                                                                                                        |
|        |                         |           | 7: prbs_position_mode 8: uq_ud_ext                                                                                                               |
|        |                         |           | 9: reserved 10: AGPI_A torque_mode                                                                                                               |
|        |                         |           | 11: AGPI_A velocity_mode                                                                                                                         |
|        |                         |           | 12: AGPI_A position_mode                                                                                                                         |
|        |                         |           | 13: PWM_I torque_mode                                                                                                                            |
|        |                         |           | 14: PWM_I velocity_mode                                                                                                                          |


15: PWM\_I position\_mode

|        | MODE_PID_SMPL MODE_PID_TYPE   | u7(30:24) bit(31)   | 0: parallel/classic PI                                                                                               |
|--------|-------------------------------|---------------------|----------------------------------------------------------------------------------------------------------------------|
| 0x64 h | PID_TORQUE_FLUX_TARGET        |                     | 1: sequential/advanced PI Target values for torque and flux controllers in torque mode.                              |
|        | PID_FLUX_TARGET               | s16(15:0)           |                                                                                                                      |
|        | PID_TORQUE_TARGET             | s16(31:16)          |                                                                                                                      |
| 0x65 h | PID_TORQUE_FLUX_OFFSET        |                     | Offsets for software torque and flux control loop inputs for feed- forward control.                                  |
|        | PID_FLUX_OFFSET               | s16(15:0)           | Flux offset for feed forward con- trol.                                                                              |
|        | PID_TORQUE_OFFSET             | s16(31:16)          | Torque offset for feed forward control.                                                                              |
| 0x66 h | PID_VELOCITY_TARGET           |                     | Target velocity value for velocity controller in velocity mode.                                                      |
|        | PID_VELOCITY_TARGET           | s32(31:0)           | Target velocity register (for veloc- ity mode).                                                                      |
| 0x67 h | PID_VELOCITY_OFFSET           |                     | Offset velocity value for velocity controller in velocity and position mode.                                         |
|        | PID_VELOCITY_OFFSET           | s32(31:0)           | Velocity offset for feed forward control.                                                                            |
| 0x68 h | PID_POSITION_TARGET           |                     | Target position value for position controller in position mode.                                                      |
|        | PID_POSITION_TARGET           | s32(31:0)           | Target position register (for posi- tion mode).                                                                      |
| 0x69 h | PID_TORQUE_FLUX_ACTUAL        |                     | Actual Torque and Flux value mea- sured by ADC and depending on the motor type after park and clarke transformation. |
|        | PID_FLUX_ACTUAL               | s16(15:0)           |                                                                                                                      |
|        | PID_TORQUE_ACTUAL             | s16(31:16)          |                                                                                                                      |
| 0x6A h | PID_VELOCITY_ACTUAL           |                     | Filtered actual velocity derived from chosen angle signal.                                                           |
|        | PID_VELOCITY_ACTUAL           | s32(31:0)           | Actual velocity.                                                                                                     |
| 0x6B h | PID_POSITION_ACTUAL           |                     | Actual position derived from cho- sen position signal.                                                               |


PID\_POSITION\_ACTUAL

s32(31:0)

Actual multi turn position for posi-

|        |                                           |                     | tioning. Input position differences are accumulated. Lower 16 bits display one revolution of input an- gle. Upper 16 bits display revo- lutions. WRITE on PID_POSITION_ ACTUAL writes same value into PID_POSITION_TARGET to avoid unwanted move.   |
|--------|-------------------------------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0x6C h | PID_ERROR_DATA                            |                     | Register displays control errors of controllers for testing according to selection PID_ERROR_ADDR .                                                                                                                                                 |
|        | PID_TORQUE_ERROR                          | s32(31:0)           | PID torque error.                                                                                                                                                                                                                                   |
|        | PID_FLUX_ERROR                            | s32(31:0)           | PID flux error.                                                                                                                                                                                                                                     |
|        | PID_VELOCITY_ERROR                        | s32(31:0)           | PID velocity error.                                                                                                                                                                                                                                 |
|        | PID_POSITION_ERROR                        | s32(31:0)           | PID position error.                                                                                                                                                                                                                                 |
|        | PID_TORQUE_ERROR_SUM                      | s32(31:0)           | PID torque error.                                                                                                                                                                                                                                   |
|        | PID_FLUX_ERROR_SUM                        | s32(31:0)           | PID flux error sum.                                                                                                                                                                                                                                 |
|        | PID_VELOCITY_ERROR_SUM                    | s32(31:0)           | PID velocity error sum.                                                                                                                                                                                                                             |
|        | PID_POSITION_ERROR_SUM                    | s32(31:0)           | PID position error sum.                                                                                                                                                                                                                             |
| 0x6D h | PID_ERROR_ADDR                            |                     | Register is used to set function of PID_ERROR_DATA register.                                                                                                                                                                                        |
|        | PID_ERROR_ADDR                            | u8(7:0)             | 0: PID_TORQUE_ERROR 1: PID_FLUX_ERROR 2: PID_VELOCITY_ERROR 3: PID_POSITION_ERROR 4: PID_TORQUE_ERROR_SUM 5: PID_FLUX_ERROR_SUM 6: PID_VELOCITY_ERROR_SUM 7: PID_POSITION_ERROR_SUM                                                                 |
| 0x6E h | INTERIM_DATA                              |                     | This register is used to display in- ternal signals from controller cas- cade for monitoring.                                                                                                                                                       |
|        | PIDIN_TARGET_TORQUE                       | s32(31:0)           | PIDIN target torque.                                                                                                                                                                                                                                |
|        | PIDIN_TARGET_FLUX                         | s32(31:0)           | PIDIN target flux.                                                                                                                                                                                                                                  |
|        | PIDIN_TARGET_VELOCITY                     | s32(31:0)           | PIDIN target velocity.                                                                                                                                                                                                                              |
|        | PIDIN_TARGET_POSITION                     | s32(31:0)           | PIDIN target position.                                                                                                                                                                                                                              |
|        | PIDOUT_TARGET_TORQUE                      | s32(31:0)           | PIDOUT target torque.                                                                                                                                                                                                                               |
|        | PIDOUT_TARGET_FLUX PIDOUT_TARGET_VELOCITY | s32(31:0) s32(31:0) | PIDOUT target flux. PIDOUT target velocity.                                                                                                                                                                                                         |


PIDOUT\_TARGET\_POSITION

s32(31:0)

PIDOUT target position.

| FOC_IUX                    | s16(15:0)   |
|----------------------------|-------------|
| FOC_IWY                    | s16(31:16)  |
| FOC_IV                     | s16(15:0)   |
| FOC_IA                     | s16(15:0)   |
| FOC_IB                     | s16(31:16)  |
| FOC_ID                     | s16(15:0)   |
| FOC_IQ                     | s16(31:16)  |
| FOC_UD                     | s16(15:0)   |
| FOC_UQ                     | s16(31:16)  |
| FOC_UD_LIMITED             | s16(15:0)   |
| FOC_UQ_LIMITED             | s16(31:16)  |
| FOC_UA                     | s16(15:0)   |
| FOC_UB                     | s16(31:16)  |
| FOC_UUX                    | s16(15:0)   |
| FOC_UWY                    | s16(31:16)  |
| FOC_UV                     | s16(15:0)   |
| PWM_UX                     | s16(15:0)   |
| PWM_WY                     | s16(31:16)  |
| PWM_V                      | s16(15:0)   |
| ADC_I_0                    | s16(15:0)   |
| ADC_I_1                    | s16(31:16)  |
| PID_FLUX_ACTUAL_DIV256     | s8(7:0)     |
| PID_TORQUE_ACTUAL_DIV256   | s8(15:8)    |
| PID_FLUX_TARGET_DIV256     | s8(23:16)   |
| PID_TORQUE_TARGET_DIV256   | s8(31:24)   |
| PID_TORQUE_ACTUAL          | s16(15:0)   |
| PID_TORQUE_TARGET          | s16(31:16)  |
| PID_FLUX_ACTUAL            | s16(15:0)   |
| PID_FLUX_TARGET            | s16(31:16)  |
| PID_VELOCITY_ACTUAL_DIV256 | s16(15:0)   |
| PID_VELOCITY_TARGET_DIV256 | s16(31:16)  |
| PID_VELOCITY_ACTUAL_LSB    | s16(15:0)   |
| PID_VELOCITY_TARGET_LSB    | s16(31:16)  |
| PID_POSITION_ACTUAL_DIV256 | s16(15:0)   |
| PID_POSITION_TARGET_DIV256 | s16(31:16)  |


PID\_POSITION\_ACTUAL\_LSB

s16(15:0)

| PID_POSITION_TARGET_LSB                                  | s16(31:16)           |                                               |
|----------------------------------------------------------|----------------------|-----------------------------------------------|
| FF_VELOCITY                                              | s32(31:0)            |                                               |
| FF_TORQUE                                                | s16(15:0)            |                                               |
| ACTUAL_VELOCITY_PPTM                                     | s32(31:0)            |                                               |
| REF_SWITCH_STATUS                                        | u16(15:0)            |                                               |
| HOME_POSITION                                            | s32(31:0)            |                                               |
| LEFT_POSITION                                            | s32(31:0)            |                                               |
| RIGHT_POSITION                                           | s32(31:0)            |                                               |
| ENC_INIT_HALL_STATUS                                     | u16(15:0)            |                                               |
| ENC_INIT_HALL_PHI_E_ABN_OFFSET                           | u16(15:0)            |                                               |
| ENC_INIT_HALL_PHI_E_AENC_OFFSET                          | u16(15:0)            |                                               |
| ENC_INIT_HALL_PHI_A_AENC_OFFSET                          | u16(15:0)            |                                               |
| SINGLE_PIN_IF_TARGET_TORQUE SINGLE_PIN_IF_PWM_DUTY_CYCLE | s16(15:0) s16(31:16) |                                               |
| SINGLE_PIN_IF_TARGET_VELOCITY                            | s32(31:0)            |                                               |
| SINGLE_PIN_IF_TARGET_POSITION                            |                      |                                               |
|                                                          | s32(31:0)            |                                               |
| INTERIM_ADDR                                             |                      | Sets function of register INTERIM_ DATA.      |
| INTERIM_ADDR                                             | u8(7:0)              | 0: PIDIN_TARGET_TORQUE                        |
|                                                          |                      | 1: PIDIN_TARGET_FLUX 2: PIDIN_TARGET_VELOCITY |
|                                                          |                      | 3: PIDIN_TARGET_POSITION                      |
|                                                          |                      | 4: PIDOUT_TARGET_TORQUE                       |
|                                                          |                      | 5: PIDOUT_TARGET_FLUX                         |
|                                                          |                      | 6: PIDOUT_TARGET_VELOCITY                     |
|                                                          |                      | 7: PIDOUT_TARGET_POSITION                     |
|                                                          |                      | 8: FOC_IWY_IUX                                |
|                                                          |                      | 9: FOC_IV                                     |
|                                                          |                      | 10: FOC_IB_IA                                 |
|                                                          |                      | 11: FOC_IQ_ID                                 |
|                                                          |                      | 12: FOC_UQ_UD                                 |
|                                                          |                      | 13: FOC_UQ_UD_LIMITED                         |
|                                                          |                      | 14: FOC_UB_UA                                 |
|                                                          |                      | 15: FOC_UWY_UUX                               |
|                                                          |                      | 16: FOC_UV                                    |


|        |               | 18: PWM_UV                                                           |
|--------|---------------|----------------------------------------------------------------------|
|        |               | 19: ADC_I1_I0                                                        |
|        |               | 20: PID_TORQUE_TARGET_FLUX_ TARGET_TORQUE_ACTUAL_FLUX_ ACTUAL_DIV256 |
|        |               | 21: PID_TORQUE_TARGET_ TORQUE_ACTUAL                                 |
|        |               | 22: PID_FLUX_TARGET_FLUX_ ACTUAL                                     |
|        |               | 23: PID_VELOCITY_TARGET_ VELOCITY_ACTUAL_DIV256                      |
|        |               | 24: PID_VELOCITY_TARGET_ VELOCITY_ACTUAL                             |
|        |               | 25: PID_POSITION_TARGET_ POSITION_ACTUAL_DIV256                      |
|        |               | 26: PID_POSITION_TARGET_ POSITION_ACTUAL                             |
|        |               | 27: FF_VELOCITY                                                      |
|        |               | 28: FF_TORQUE                                                        |
|        |               | 29: ACTUAL_VELOCITY_PPTM                                             |
|        |               | 30: REF_SWITCH_STATUS                                                |
|        |               | 31: HOME_POSITION                                                    |
|        |               | 32: LEFT_POSITION                                                    |
|        |               | 33: RIGHT_POSITION                                                   |
|        |               | 34: ENC_INIT_HALL_STATUS                                             |
|        |               | 35: ENC_INIT_HALL_PHI_E_ABN_ OFFSET                                  |
|        |               | 36: ENC_INIT_HALL_PHI_E_AENC_ OFFSET                                 |
|        |               | 37: ENC_INIT_HALL_PHI_A_AENC_ OFFSET                                 |
|        |               | 42: SINGLE_PIN_IF_PWM_DUTY_ CYCLE_TORQUE_TARGET                      |
|        |               | 43: SINGLE_PIN_IF_VELOCITY_ TARGET                                   |
|        |               | 44: SINGLE_PIN_IF_POSITION_ TARGET                                   |
| 0x75 h | ADC_VM_LIMITS | Sets supply voltage limits for brake chopper output action.          |


ADC\_VM\_LIMIT\_LOW

u16(15:0)

Low limit for brake chopper out-

|        |                     |            | put BRAKE_OUT.                                                             |
|--------|---------------------|------------|----------------------------------------------------------------------------|
|        | ADC_VM_LIMIT_HIGH   | u16(31:16) | High limit for brake chopper out- put BRAKE_OUT.                           |
| 0x76 h | TMC4671_INPUTS_RAW  |            | Displays actual input signals of IC for monitoring and connection testing. |
|        | A of ABN_RAW        | bit(0)     | A of ABN_RAW 0: off 1: on                                                  |
|        | B of ABN_RAW        | bit(1)     | B of ABN_RAW 0: off 1: on                                                  |
|        | N of ABN_RAW        | bit(2)     | N of ABN_RAW 0: off 1: on                                                  |
|        | -                   | bit(3)     | - 0: off 1: on                                                             |
|        | A of ABN_2_RAW      | bit(4)     | A of ABN_2_RAW 0: off 1: on                                                |
|        | B of ABN_2_RAW      | bit(5)     | B of ABN_2_RAW 0: off 1: on                                                |
|        | N of ABN_2_RAW      | bit(6)     | N of ABN_2_RAW 0: off                                                      |
|        | -                   | bit(7)     | 1: on - 0: off 1: on                                                       |
|        | HALL_UX of HALL_RAW | bit(8)     | HALL_UX of HALL_RAW 0: off 1: on                                           |
|        | HALL_V of HALL_RAW  | bit(9)     | HALL_V of HALL_RAW 0: off 1: on                                            |


HALL\_WY of HALL\_RAW

bit(10)

HALL\_WY of HALL\_RAW

|                   |         | 0: off                          |
|-------------------|---------|---------------------------------|
| -                 | bit(11) | 1: on - 0: off 1: on            |
| REF_SW_R_RAW      | bit(12) | REF_SW_R_RAW 0: off             |
| REF_SW_H_RAW      | bit(13) | 1: on REF_SW_H_RAW 0: off 1: on |
| REF_SW_L_RAW      | bit(14) | REF_SW_L_RAW 0: off 1: on       |
| ENABLE_IN_RAW     | bit(15) | ENABLE_IN_RAW 0: off 1: on      |
| STP of DIRSTP_RAW | bit(16) | STP of DIRSTP_RAW 0: off 1: on  |
| DIR of DIRSTP_RAW | bit(17) | DIR of DIRSTP_RAW 0: off 1: on  |
| PWM_IN_RAW        | bit(18) | PWM_IN_RAW 0: off 1: on         |
| -                 | bit(19) | - 0: off 1: on                  |
| HALL_UX_FILT      | bit(20) | ESI_0 of ESI_RAW 0: off 1: on   |
| HALL_V_FILT       | bit(21) | ESI_1 of ESI_RAW 0: off 1: on   |


HALL\_WY\_FILT

bit(22)

ESI\_2 of ESI\_RAW

|                                                   |         | 0: off                                                                                       |
|---------------------------------------------------|---------|----------------------------------------------------------------------------------------------|
| -                                                 | bit(23) | 1: on - 0: off                                                                               |
| -                                                 | bit(24) | 1: on CFG_0 of CFG 0: off                                                                    |
| -                                                 | bit(25) | 1: on CFG_1 of CFG 0: off 1: on                                                              |
| -                                                 | bit(26) | CFG_2 of CFG 0: off 1: on                                                                    |
| -                                                 | bit(27) | CFG_3 of CFG 0: off 1: on                                                                    |
| PWM_IDLE_L_RAW                                    | bit(28) | PWM_IDLE_L_RAW 0: off 1: on                                                                  |
| PWM_IDLE_H_RAW                                    | bit(29) | PWM_IDLE_H_RAW 0: off                                                                        |
| -                                                 | bit(30) | 1: on DRV_ERR_IN_RAW 0: off 1: on                                                            |
| -                                                 | bit(31) | - 0: off 1: on                                                                               |
| 0x77 h TMC4671_OUTPUTS_RAW TMC4671_OUTPUTS_RAW[0] | bit(0)  | Displays actual output signals of IC for monitoring and connection testing. PWM_UX1_L 0: off |


0: off

|        |                                          |           | 1: on                                                                                                                                                                                                                                                     |
|--------|------------------------------------------|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|        | TMC4671_OUTPUTS_RAW[2]                   | bit(2)    | PWM_VX2_L 0: off                                                                                                                                                                                                                                          |
|        | TMC4671_OUTPUTS_RAW[3]                   | bit(3)    | 1: on PWM_VX2_H 0: off 1: on                                                                                                                                                                                                                              |
|        | TMC4671_OUTPUTS_RAW[4]                   | bit(4)    | PWM_WY1_L 0: off 1: on                                                                                                                                                                                                                                    |
|        | TMC4671_OUTPUTS_RAW[5]                   | bit(5)    | PWM_WY1_H 0: off 1: on                                                                                                                                                                                                                                    |
|        | TMC4671_OUTPUTS_RAW[6]                   | bit(6)    | PWM_Y2_L 0: off 1: on                                                                                                                                                                                                                                     |
|        | TMC4671_OUTPUTS_RAW[7]                   | bit(7)    | PWM_Y2_H 0: off 1: on                                                                                                                                                                                                                                     |
| 0x78 h | STEP_WIDTH STEP_WIDTH                    | s32(31:0) | Sets a Step width of an acutal in- put step signal on STEP/DIR in- terface. Target position is de- creased/increased by this value according to Dir signal. STEP WIDTH = 0 => STP pulses ignored, resulting direction = DIR XOR sign(STEP_WIDTH), effects |
| 0x79 h | UART_BPS UART_BPS                        | u24(23:0) | PID_POSITION_TARGET Sets the desired UART baudrate. Must be entered as hexadecimal number (e.g baudrate 9600 is set by entering 0x00009600 h ) 0x00009600 h , 0x00115200 h , 0x00921600 h , 0x03000000 h (default=0x00009600)                             |
| 0x7B h | GPIO_dsADCI_CONFIG GPIO_dsADCI_CONFIG[0] | bit(0)    | Sets the function and controls the GPIOs if RTMI is not used. Check functional description for detailed explanation of options. SEL_nDBGSPIM_GPIO                                                                                                         |


0: off

|        |                       |                     | 1: on                                                                                               |
|--------|-----------------------|---------------------|-----------------------------------------------------------------------------------------------------|
|        | GPIO_dsADCI_CONFIG[1] | bit(1)              | SEL_nGPIO_dsADCS_A 0: off                                                                           |
|        | GPIO_dsADCI_CONFIG[2] | bit(2)              | 1: on SEL_nGPIO_dsADCS_B 0: off 1: on                                                               |
|        | GPIO_dsADCI_CONFIG[3] | bit(3)              | SEL_GPIO_GROUP_A_nIN_OUT 0: off 1: on                                                               |
|        | GPIO_dsADCI_CONFIG[4] | bit(4)              | SEL_GPIO_GROUP_B_nIN_OUT 0: off                                                                     |
|        | GPIO_dsADCI_CONFIG[5] | bit(5)              | 1: on SEL_GROUP_A_DSADCS_nCLKIN_ CLKOUT 0: off                                                      |
|        | GPIO_dsADCI_CONFIG[6] | bit(6)              | 1: on SEL_GROUP_B_DSADCS_nCLKIN_ CLKOUT 0: off                                                      |
|        | GPO GPI               | u8(23:16) u8(31:24) | 1: on                                                                                               |
| 0x7C h | STATUS_FLAGS          |                     | Displays actual status flags to set status output. The register is also used to reset status flags. |
|        | STATUS_FLAGS[0]       | bit(0)              | pid_x_target_limit 0: off                                                                           |
|        | STATUS_FLAGS[1]       | bit(1)              | 1: on pid_x_target_ddt_limit 0: off                                                                 |
|        | STATUS_FLAGS[2]       | bit(2)              | 1: on pid_x_errsum_limit 0: off 1: on                                                               |
|        | STATUS_FLAGS[3]       | bit(3)              | pid_x_output_limit                                                                                  |


0: off

|                  |         | 1: on                                      |
|------------------|---------|--------------------------------------------|
| STATUS_FLAGS[4]  | bit(4)  | pid_v_target_limit 0: off                  |
| STATUS_FLAGS[5]  | bit(5)  | 1: on pid_v_target_ddt_limit 0: off 1: on  |
| STATUS_FLAGS[6]  | bit(6)  | pid_v_errsum_limit 0: off 1: on            |
| STATUS_FLAGS[7]  | bit(7)  | pid_v_output_limit 0: off                  |
| STATUS_FLAGS[8]  | bit(8)  | 1: on pid_id_target_limit 0: off 1: on     |
| STATUS_FLAGS[9]  | bit(9)  | pid_id_target_ddt_limit 0: off 1: on       |
| STATUS_FLAGS[10] | bit(10) | pid_id_errsum_limit 0: off                 |
| STATUS_FLAGS[11] | bit(11) | 1: on pid_id_output_limit 0: off 1: on     |
| STATUS_FLAGS[12] | bit(12) | pid_iq_target_limit 0: off                 |
| STATUS_FLAGS[13] | bit(13) | 1: on pid_iq_target_ddt_limit 0: off 1: on |
| STATUS_FLAGS[14] | bit(14) | pid_iq_errsum_limit 0: off 1: on           |
| STATUS_FLAGS[15] | bit(15) | pid_iq_output_limit                        |


0: off

|                  |         | 1: on                                     |
|------------------|---------|-------------------------------------------|
| STATUS_FLAGS[16] | bit(16) | ipark_cirlim_limit_u_d 0: off             |
| STATUS_FLAGS[17] | bit(17) | 1: on ipark_cirlim_limit_u_q 0: off 1: on |
| STATUS_FLAGS[18] | bit(18) | ipark_cirlim_limit_u_r 0: off 1: on       |
| STATUS_FLAGS[19] | bit(19) | not_PLL_locked 0: off 1: on               |
| STATUS_FLAGS[20] | bit(20) | ref_sw_r 0: off 1: on                     |
| STATUS_FLAGS[21] | bit(21) | ref_sw_h 0: off                           |
| STATUS_FLAGS[22] | bit(22) | 1: on ref_sw_l 0: off                     |
| STATUS_FLAGS[23] | bit(23) | 1: on - 0: off 1: on                      |
| STATUS_FLAGS[24] | bit(24) | pwm_min 0: off 1: on                      |
| STATUS_FLAGS[25] | bit(25) | pwm_max 0: off 1: on                      |
| STATUS_FLAGS[26] | bit(26) | adc_i_clipped 0: off 1: on                |
| STATUS_FLAGS[27] | bit(27) | aenc_clipped                              |


0: off

|        |                         |           | 1: on                                                                                |
|--------|-------------------------|-----------|--------------------------------------------------------------------------------------|
|        | STATUS_FLAGS[28]        | bit(28)   | enc_n 0: off 1: on                                                                   |
|        | STATUS_FLAGS[29]        | bit(29)   | enc_2_n 0: off 1: on                                                                 |
|        | STATUS_FLAGS[30]        | bit(30)   | aenc_n 0: off 1: on                                                                  |
|        | STATUS_FLAGS[31]        | bit(31)   | reserved 0: off 1: on                                                                |
| 0x7D h | STATUS_MASK STATUS_MASK | u32(31:0) | Register is used to set a mask for STATUS_FLAGS register to set STA- TUS output pin. |


## 7.3 Register Map - Defaults, min, max

RD/WR

ADDR

NAME

| R   | 0x00 h   | CHIPINFO_DATA                     |              |             |              |
|-----|----------|-----------------------------------|--------------|-------------|--------------|
|     |          | SI_TYPE                           | 0x0 h        | 0x0 h       | 0xFFFFFFFF h |
|     |          | SI_VERSION                        | 0x0 h        | 0x0 h       | 0xFFFFFFFF h |
|     |          | SI_DATE                           | 0x0 h        | 0x0 h       | 0xFFFFFFFF h |
|     |          | SI_TIME                           | 0x0 h        | 0x0 h       | 0xFFFFFF h   |
|     |          | SI_VARIANT                        | 0x0 h        | 0x0 h       | 0xFFFFFFFF h |
|     |          | SI_BUILD                          | 0x0 h        | 0x0 h       | 0xFFFFFFFF h |
| RW  | 0x01 h   | CHIPINFO_ADDR                     |              |             |              |
|     |          | CHIP_INFO_ADDRESS                 | 0x0 h        | 0x0 h       | 0x5 h        |
| R   | 0x02 h   | ADC_RAW_DATA                      |              |             |              |
|     |          | ADC_I0_RAW                        | 0x0 h        | 0x0 h       | 0xFFFF h     |
|     |          | ADC_I1_RAW                        | 0x0 h        | 0x0 h       | 0xFFFF h     |
|     |          | ADC_VM_RAW                        | 0x0 h        | 0x0 h       | 0xFFFF h     |
|     |          | ADC_AGPI_A_RAW                    | 0x0 h        | 0x0 h       | 0xFFFF h     |
|     |          | ADC_AGPI_B_RAW                    | 0x0 h        | 0x0 h       | 0xFFFF h     |
|     |          | ADC_AENC_UX_RAW                   | 0x0 h        | 0x0 h       | 0xFFFF h     |
|     |          | ADC_AENC_VN_RAW                   | 0x0 h        | 0x0 h       | 0xFFFF h     |
|     |          | ADC_AENC_WY_RAW                   | 0x0 h        | 0x0 h       | 0xFFFF h     |
| RW  | 0x03 h   | ADC_RAW_ADDR                      |              |             |              |
|     | 0x04 h   | ADC_RAW_ADDR dsADC_MCFG_B_ MCFG_A | 0x0 h        | 0x0 h       | 0x3 h        |
| RW  |          | cfg_dsmodulator_a mclk_polarity_a | 0x0 h 0x0 h  | 0x0 h 0x0 h | 0x3 h 0x1 h  |
|     |          | mdat_polarity_a                   | 0x0 h        | 0x0 h       | 0x1 h        |
|     |          | sel_nclk_mclk_i_a                 | 0x0 h        | 0x0 h       | 0x1 h        |
|     |          | cfg_dsmodulator_b                 | 0x0 h        | 0x0 h       | 0x3 h        |
|     |          | mclk_polarity_b                   | 0x0 h        | 0x0 h       | 0x1 h        |
|     |          |                                   | 0x0          |             | 0x1 h        |
|     |          | mdat_polarity_b                   | h 0x0        | 0x0 h       |              |
|     |          | sel_nclk_mclk_i_b                 | h            | 0x0 h       | 0x1 h        |
| RW  | 0x05 h   | dsADC_MCLK_A                      |              |             |              |
|     |          | dsADC_MCLK_A                      | 0x20000000 h | 0x0 h       | 0xFFFFFFFF h |
| RW  | 0x06 h   | dsADC_MCLK_B                      |              |             |              |

MAX


DEFAULT

MIN

dsADC\_MCLK\_B

0x20000000

0x0

0xFFFFFFFF

|    |        |                            | h       | h         | h        |
|----|--------|----------------------------|---------|-----------|----------|
| RW | 0x07 h | dsADC_MDEC_B_ MDEC_A       |         |           |          |
|    |        | dsADC_MDEC_A               | 0x100 h | 0x0 h     | 0xFFFF h |
|    |        | dsADC_MDEC_B               | 0x100 h | 0x0 h     | 0xFFFF h |
| RW | 0x08 h | ADC_I1_SCALE_ OFFSET       |         |           |          |
|    |        | ADC_I1_OFFSET              | 0x0 h   | 0x0 h     | 0xFFFF h |
|    |        | ADC_I1_SCALE               | 0x100 h | -0x8000 h | 0x7FFF h |
| RW | 0x09 h | ADC_I0_SCALE_ OFFSET       |         |           |          |
|    |        | ADC_I0_OFFSET              | 0x0 h   | 0x0 h     | 0xFFFF h |
|    |        | ADC_I0_SCALE               | 0x100 h | -0x8000 h | 0x7FFF h |
| RW | 0x0A h | ADC_I_SELECT               |         |           |          |
|    |        | ADC_I0_SELECT              | 0x0 h   | 0x0 h     | 0x3 h    |
|    |        | ADC_I1_SELECT              | 0x1 h   | 0x0 h     | 0x3 h    |
|    |        | ADC_I_UX_SELECT            | 0x0 h   | 0x0 h     | 0x2 h    |
|    |        | ADC_I_V_SELECT             | 0x1 h   | 0x0 h     | 0x2 h    |
|    |        | ADC_I_WY_SELECT            | 0x2 h   | 0x0 h     | 0x2 h    |
| RW | 0x0B h | ADC_I1_I0_EXT              |         |           |          |
|    |        | ADC_I0_EXT                 | 0x0 h   | 0x0 h     | 0xFFFF h |
|    |        | ADC_I1_EXT                 | 0x0 h   | 0x0 h     | 0xFFFF h |
| RW | 0x0C h | DS_ANALOG_INPUT_ STAGE_CFG |         |           |          |
|    |        | ADC_I0                     | 0x0 h   | 0x0 h     | 0x7 h    |
|    |        | ADC_I1                     | 0x0 h   | 0x0 h     | 0x7 h    |
|    |        | ADC_VM                     | 0x0 h   | 0x0 h     | 0x7 h    |
|    |        | ADC_AGPI_A                 | 0x0 h   | 0x0 h     | 0x7 h    |
|    |        | ADC_AGPI_B                 | 0x0 h   | 0x0 h     | 0x7 h    |
|    |        | ADC_AENC_UX                | 0x0 h   | 0x0 h     | 0x7 h    |
|    |        | ADC_AENC_VN                | 0x0 h   | 0x0 h     | 0x7 h    |
|    |        | ADC_AENC_WY                | 0x0 h   | 0x0 h     | 0x7 h    |
| RW | 0x0D h | AENC_0_SCALE_ OFFSET       |         |           |          |
|    |        | AENC_0_OFFSET              | 0x0 h   | 0x0 h     | 0xFFFF h |
|    |        | AENC_0_SCALE               | 0x100 h | -0x8000 h | 0x7FFF h |
| RW | 0x0E h | AENC_1_SCALE_ OFFSET       |         |           |          |


AENC\_1\_OFFSET

0x0

0x0

0xFFFF

|    |        | AENC_1_SCALE               | h 0x100 h     | h -0x8000 h   | h 0x7FFF h   |
|----|--------|----------------------------|---------------|---------------|--------------|
| RW | 0x0F h | AENC_2_SCALE_ OFFSET       |               |               |              |
|    |        | AENC_2_OFFSET              | 0x0 h         | 0x0 h         | 0xFFFF h     |
|    |        | AENC_2_SCALE               | 0x100 h       | -0x8000 h     | 0x7FFF h     |
| RW | 0x11 h | AENC_SELECT                |               |               |              |
|    |        | AENC_0_SELECT              | 0x0 h         | 0x0 h         | 0x2 h        |
|    |        | AENC_1_SELECT              | 0x1 h         | 0x0 h         | 0x2 h        |
|    |        | AENC_2_SELECT              | 0x2 h         | 0x0 h         | 0x2 h        |
| R  | 0x12 h | ADC_IWY_IUX                |               |               |              |
|    |        | ADC_IUX                    | 0x0 h         | -0x8000 h     | 0x7FFF h     |
|    |        | ADC_IWY                    | 0x0 h         | -0x8000 h     | 0x7FFF h     |
| R  | 0x13 h | ADC_IV                     | 0x0 h         | -0x8000 h     | 0x7FFF h     |
| R  | 0x15 h | ADC_IV AENC_WY_UX          | 0x0 h         | -0x8000 h     | 0x7FFF h     |
|    |        | AENC_UX                    | 0x0 h         | -0x8000 h     | 0x7FFF       |
| R  | 0x16 h | AENC_VN AENC_VN            |               |               |              |
|    |        | AENC_WY                    |               |               | h            |
|    |        |                            | 0x0 h         | -0x8000 h     | 0x7FFF h     |
| RW | 0x17 h | PWM_POLARITIES             |               |               |              |
|    |        | PWM_POLARITIES[0]          | 0x0 h         | 0x0 h         | 0x1 h        |
|    |        | PWM_POLARITIES[1]          | 0x0 h         | 0x0 h         | 0x1 h        |
| RW | 0x18 h | PWM_MAXCNT                 |               |               |              |
|    | 0x19 h | PWM_MAXCNT PWM_BBM_H_BBM_L | 0xF9F h       | 0x0 h         | 0xFFFF h     |
| RW |        | PWM_BBM_L                  | 0x14 h 0x14 h | 0x0 h         | 0xFF h       |
|    |        | PWM_BBM_H                  |               | 0x0 h         | 0xFF h       |
| RW | 0x1A h | PWM_SV_CHOP                |               |               |              |
|    |        | PWM_CHOP                   | 0x0 h         | 0x0 h         | 0x7 h        |
|    |        | PWM_SV                     | 0x0 h         | 0x0 h         | 0x1 h        |
| RW | 0x1B h | MOTOR_TYPE_N_ POLE_PAIRS   |               |               |              |
|    |        |                            | 0x1 h         |               | 0xFFFF h     |
|    |        | MOTOR_TYPE                 | 0x0 h         | 0x0 h         | 0x3 h        |
| RW | 0x1C   | PHI_E_EXT                  |               |               |              |
|    |        | N_POLE_PAIRS               |               | 0x1 h         |              |
|    | h      |                            |               |               |              |


PHI\_E\_EXT

0x0

-0x8000

0x7FFF

|     |        |                                                     | h                       | h                                   | h                       |
|-----|--------|-----------------------------------------------------|-------------------------|-------------------------------------|-------------------------|
| RW  | 0x1F h | OPENLOOP_MODE OPENLOOP_PHI_ DIRECTION               | 0x0 h                   | 0x0 h                               | 0x1 h                   |
| RW  | 0x20 h | OPENLOOP_ ACCELERATION OPENLOOP_ ACCELERATION       | 0x0 h                   | 0x0 h                               | 0xFFFFF h               |
| RW  | 0x21 h | OPENLOOP_ VELOCITY_TARGET OPENLOOP_ VELOCITY_TARGET | 0x0 h                   | -0x80000000 h                       | 0x7FFFFFFF h            |
| RW  | 0x22 h | OPENLOOP_ VELOCITY_ACTUAL OPENLOOP_ VELOCITY_ACTUAL | 0x0 h                   | -0x80000000 h                       | 0x7FFFFFFF h            |
| RWI | 0x23 h | OPENLOOP_PHI OPENLOOP_PHI                           | 0x0 h                   | -0x8000 h                           | 0x7FFF h                |
| RW  | 0x24 h | UQ_UD_EXT UD_EXT UQ_EXT                             | 0x0 h 0x0 h             | -0x8000 h -0x8000 h                 | 0x7FFF h 0x7FFF h       |
| RW  | 0x25 h | ABN_DECODER_ MODE apol bpol npol use_abn_as_n       | 0x0 h 0x0 h 0x0 h 0x0 h | 0x0 h 0x0 h 0x0 h 0x0 h 0x0 h 0x0 h | 0x1 h 0x1 h 0x1 h 0x1 h |
| RW  |        | ABN_DECODER_PPR ABN_DECODER_ COUNT                  | 0x10000 h               | 0x0 h                               | 0xFFFFFF h              |
|     | 0x26 h | cln direction ABN_DECODER_PPR                       | 0x0 h 0x0 h             |                                     | 0x1 h 0x1 h             |
| RW  | 0x27 h | ABN_DECODER_                                        | 0x0 h                   | 0x0 h                               | 0xFFFFFF h              |
|     |        | COUNT ABN_DECODER_                                  |                         |                                     |                         |
| RW  | 0x28 h | COUNT_N                                             |                         |                                     |                         |


ABN\_DECODER\_

0x0

0x0

0xFFFFFF

|    |        | COUNT_N                         | h         | h         | h          |
|----|--------|---------------------------------|-----------|-----------|------------|
| RW | 0x29 h | ABN_DECODER_PHI_ E_PHI_M_OFFSET |           |           |            |
|    |        | ABN_DECODER_PHI_ M_OFFSET       | 0x0 h     | -0x8000 h | 0x7FFF h   |
|    |        | ABN_DECODER_PHI_ E_OFFSET       | 0x0 h     | -0x8000 h | 0x7FFF h   |
| R  | 0x2A h | ABN_DECODER_PHI_ E_PHI_M        |           |           |            |
|    |        | ABN_DECODER_PHI_ M              | 0x0 h     | -0x8000 h | 0x7FFF h   |
|    |        | ABN_DECODER_PHI_ E              | 0x0 h     | -0x8000 h | 0x7FFF h   |
| RW | 0x2C h | ABN_2_DECODER_ MODE             |           |           |            |
|    |        | apol                            | 0x0 h     | 0x0 h     | 0x1 h      |
|    |        | bpol                            | 0x0 h     | 0x0 h     | 0x1 h      |
|    |        | npol                            | 0x0 h     | 0x0 h     | 0x1 h      |
|    |        | use_abn_as_n                    | 0x0 h     | 0x0 h     | 0x1 h      |
|    |        | cln                             | 0x0 h     | 0x0 h     | 0x1 h      |
|    |        | direction                       | 0x0 h     | 0x0 h     | 0x1 h      |
| RW | 0x2D h | ABN_2_DECODER_ PPR              |           |           |            |
|    |        | ABN_2_DECODER_ PPR              | 0x10000 h | 0x1 h     | 0xFFFFFF h |
| RW | 0x2E h | ABN_2_DECODER_ COUNT            |           |           |            |
|    |        | ABN_2_DECODER_ COUNT            | 0x0 h     | 0x0 h     | 0xFFFFFF h |
| RW | 0x2F h | ABN_2_DECODER_ COUNT_N          |           |           |            |
|    |        | ABN_2_DECODER_ COUNT_N          | 0x0 h     | 0x0 h     | 0xFFFFFF h |
| RW | 0x30 h | ABN_2_DECODER_ PHI_M_OFFSET     |           |           |            |
|    |        | ABN_2_DECODER_ PHI_M_OFFSET     | 0x0 h     | -0x8000 h | 0x7FFF h   |
| R  | 0x31 h | ABN_2_DECODER_ PHI_M            |           |           |            |


ABN\_2\_DECODER\_

0x0

-0x8000

0x7FFF

|    |        | PHI_M                           | h         | h         | h        |
|----|--------|---------------------------------|-----------|-----------|----------|
| RW | 0x33 h | HALL_MODE polarity              | 0x0 h     | 0x0 h     | 0x1 h    |
|    |        | synchronous PWM sampling        | 0x0 h     | 0x0 h     | 0x1 h    |
|    |        | interpolation                   | 0x0 h     | 0x0 h     | 0x1 h    |
|    |        | direction                       | 0x0 h     | 0x0 h     | 0x1 h    |
|    |        | HALL_BLANK                      | 0x0 h     | 0x0 h     | 0xFFF h  |
| RW | 0x34 h | HALL_POSITION_ 060_000          |           |           |          |
|    |        | HALL_POSITION_000               | 0x0 h     | -0x8000 h | 0x7FFF h |
|    |        | HALL_POSITION_060               | 0x2AAA h  | -0x8000 h | 0x7FFF h |
| RW | 0x35 h | HALL_POSITION_ 180_120          |           |           |          |
|    |        | HALL_POSITION_120               | 0x5555 h  | -0x8000 h | 0x7FFF h |
|    |        | HALL_POSITION_180               | -0x8000 h | -0x8000 h | 0x7FFF h |
| RW | 0x36 h | HALL_POSITION_ 300_240          |           |           |          |
|    |        | HALL_POSITION_240               | -0x5556 h | -0x8000 h | 0x7FFF h |
|    |        | HALL_POSITION_300               | -0x2AAB h | -0x8000 h | 0x7FFF h |
| RW | 0x37 h | HALL_PHI_E_PHI_M_ OFFSET        |           |           |          |
|    |        | HALL_PHI_M_OFFSET               | 0x0 h     | -0x8000 h | 0x7FFF h |
|    |        | HALL_PHI_E_OFFSET               | 0x0 h     | -0x8000 h | 0x7FFF h |
| RW | 0x38 h | HALL_DPHI_MAX                   |           |           |          |
|    |        | HALL_DPHI_MAX                   | 0x2AAA h  | 0x0 h     | 0xFFFF h |
| R  | 0x39 h | HALL_PHI_E_ INTERPOLATED_ PHI_E |           |           |          |
|    |        | HALL_PHI_E                      | 0x0 h     | -0x8000 h | 0x7FFF h |
|    |        | HALL_PHI_E_ INTERPOLATED        | 0x0 h     | -0x8000 h | 0x7FFF h |
| R  | 0x3A h | HALL_PHI_M                      |           |           |          |
|    |        | HALL_PHI_M                      | 0x0 h     | -0x8000 h | 0x7FFF h |
| RW | 0x3B h | AENC_DECODER_ MODE              |           |           |          |
|    |        | AENC_DECODER_ MODE[0]           | 0x0 h     | 0x0 h     | 0x1 h    |


AENC\_DECODER\_

0x0

0x0

0x1

|    |        | MODE[12]                                  | h     | h             | h            |
|----|--------|-------------------------------------------|-------|---------------|--------------|
| RW | 0x3C h | AENC_DECODER_N_ THRESHOLD AENC_DECODER_N_ |       |               |              |
|    |        | THRESHOLD                                 | 0x0 h | 0x0 h         | 0xFFFF h     |
| R  | 0x3D h | AENC_DECODER_ PHI_A_RAW                   |       |               |              |
|    |        | AENC_DECODER_ PHI_A_RAW                   | 0x0 h | -0x8000 h     | 0x7FFF h     |
| RW | 0x3E h | AENC_DECODER_ PHI_A_OFFSET                |       |               |              |
|    |        | AENC_DECODER_ PHI_A_OFFSET                | 0x0 h | -0x8000 h     | 0x7FFF h     |
| R  | 0x3F h | AENC_DECODER_ PHI_A                       |       |               |              |
|    |        | AENC_DECODER_ PHI_A                       | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
| RW | 0x40 h | AENC_DECODER_PPR                          |       |               |              |
|    |        | AENC_DECODER_PPR                          | 0x1 h | -0x8000 h     | 0x7FFF h     |
| R  | 0x41 h | AENC_DECODER_ COUNT                       |       |               |              |
|    |        | AENC_DECODER_ COUNT                       | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
| RW | 0x42 h | AENC_DECODER_ COUNT_N                     |       |               |              |
|    |        | AENC_DECODER_ COUNT_N                     | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
| RW | 0x45 h | AENC_DECODER_ PHI_E_PHI_M_OFFSET          |       |               |              |
|    |        | AENC_DECODER_ PHI_M_OFFSET                | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | AENC_DECODER_ PHI_E_OFFSET                | 0x0 h | -0x8000 h     | 0x7FFF h     |
| R  | 0x46 h | AENC_DECODER_ PHI_E_PHI_M                 |       |               |              |
|    |        | AENC_DECODER_ PHI_M                       | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | AENC_DECODER_ PHI_E                       | 0x0 h | -0x8000 h     | 0x7FFF h     |


RW

0x4D

CONFIG\_DATA

| h   |                                         |       |               |              |
|-----|-----------------------------------------|-------|---------------|--------------|
|     | biquad_x_a_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_x_a_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_x_b_0                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_x_b_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_x_b_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_x_enable                         | 0x0 h | 0x0 h         | 0x1 h        |
|     | biquad_v_a_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_v_a_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_v_b_0                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_v_b_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_v_b_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_v_enable                         | 0x0 h | 0x0 h         | 0x1 h        |
|     | biquad_t_a_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_t_a_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_t_b_0                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_t_b_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_t_b_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_t_enable                         | 0x0 h | 0x0 h         | 0x1 h        |
|     | biquad_f_a_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_f_a_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_f_b_0                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_f_b_1                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_f_b_2                            | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | biquad_f_enable                         | 0x0 h | 0x0 h         | 0x1 h        |
|     | prbs_amplitude                          | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | prbs_down_ sampling_ratio               | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | feed_forward_ velocity_gain             | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | feed_forward_ velocity_filter_ constant | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | feed_forward_ torque_gain               | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|     | feed_forward_ torgue_filter_ constant   | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |


VELOCITY\_METER\_

0x0

0x0

0xFFFF

|    |        | PPTM_MIN_POS_DEV                | h     | h         | h        |
|----|--------|---------------------------------|-------|-----------|----------|
|    |        | ref_switch_config               | 0x0 h | 0x0 h     | 0xFFFF h |
|    |        | Encoder_Init_hall_ Enable       | 0x0 h | 0x0 h     | 0x1 h    |
|    |        | SINGLE_PIN_IF_CFG               | 0x0 h | 0x0 h     | 0xFF h   |
|    |        | SINGLE_PIN_IF_ STATUS           | 0x0 h | 0x0 h     | 0xFFFF h |
|    |        | SINGLE_PIN_IF_ OFFSET           | 0x0 h | 0x0 h     | 0xFFFF h |
|    |        | SINGLE_PIN_IF_ SCALE            | 0x0 h | -0x7FFF h | 0x7FFF h |
|    |        | CURRENT_P_nQ8.8_ Q4.12          | 0x0 h | 0x0 h     | 0x1 h    |
|    |        | CURRENT_I_nQ8.8_ Q4.12          | 0x0 h | 0x0 h     | 0x1 h    |
|    |        | VELOCITY_P_nQ8.8_ Q4.12         | 0x0 h | 0x0 h     | 0x1 h    |
|    |        | VELOCITY_I_nQ8.8_ Q4.12         | 0x0 h | 0x0 h     | 0x1 h    |
|    |        | POSITION_P_nQ8.8_ Q4.12         | 0x0 h | 0x0 h     | 0x1 h    |
|    |        | POSITION_I_nQ8.8_ Q4.12         | 0x0 h | 0x0 h     | 0x1 h    |
| RW | 0x4E h | CONFIG_ADDR CONFIG_ADDR         | 0x0 h | 0x1 h     | 0x3E h   |
| RW | 0x50 h | VELOCITY_ SELECTION             |       |           |          |
|    |        | VELOCITY_ SELECTION             | 0x0 h | 0x0 h     | 0xC h    |
|    |        | VELOCITY_METER_ SELECTION       | 0x0 h | 0x0 h     | 0x1 h    |
| RW | 0x51 h | POSITION_ SELECTION             |       |           |          |
|    |        | POSITION_ SELECTION             | 0x0 h | 0x0 h     | 0xC h    |
| RW | 0x52 h | PHI_E_SELECTION PHI_E_SELECTION |       |           |          |
|    |        |                                 | 0x0 h | 0x0 h     | 0x7 h    |
| R  | 0x53 h | PHI_E                           |       |           |          |
|    |        | PHI_E                           | 0x0 h | -0x8000 h | 0x7FFF h |


RW

0x54

PID\_FLUX\_P\_FLUX\_I

|    | h      |                                       |               |               |              |
|----|--------|---------------------------------------|---------------|---------------|--------------|
|    |        | PID_FLUX_I                            | 0x0 h         | 0x0 h         | 0x7FFF h     |
|    |        | PID_FLUX_P                            | 0x0 h         | 0x0 h         | 0x7FFF h     |
| RW | 0x56 h | PID_TORQUE_P_ TORQUE_I                |               |               |              |
|    |        | PID_TORQUE_I                          | 0x0 h         | 0x0 h         | 0x7FFF h     |
|    |        | PID_TORQUE_P                          | 0x0 h         | 0x0 h         | 0x7FFF h     |
| RW | 0x58 h | PID_VELOCITY_P_ VELOCITY_I            |               |               |              |
|    |        | PID_VELOCITY_I                        | 0x0 h         | 0x0 h         | 0x7FFF h     |
|    |        | PID_VELOCITY_P                        | 0x0 h         | 0x0 h         | 0x7FFF h     |
| RW | 0x5A h | PID_POSITION_P_ POSITION_I            |               |               |              |
|    |        | PID_POSITION_I                        | 0x0 h         | 0x0 h         | 0x7FFF h     |
|    |        | PID_POSITION_P                        | 0x0 h         | 0x0 h         | 0x7FFF h     |
| RW | 0x5D h | PIDOUT_UQ_UD_ LIMITS                  |               |               |              |
|    |        | PIDOUT_UQ_UD_ LIMITS                  | 0x5A81 h      | 0x0 h         | 0x7FFF h     |
| RW | 0x5E h | PID_TORQUE_FLUX_ LIMITS               |               |               |              |
|    |        | PID_TORQUE_FLUX_ LIMITS               | 0x7FFF h      | 0x0 h         | 0x7FFF h     |
| RW | 0x60 h | PID_VELOCITY_LIMIT PID_VELOCITY_LIMIT |               |               |              |
|    |        |                                       | 0x7FFFFFFF h  | 0x0 h         | 0xFFFFFFFF h |
| RW | 0x61 h | PID_POSITION_ LIMIT_LOW               |               |               |              |
|    |        | PID_POSITION_ LIMIT_LOW               | -0x7FFFFFFF h | -0x80000000 h | 0x7FFFFFFF h |
| RW | 0x62 h | PID_POSITION_ LIMIT_HIGH              |               |               |              |
|    |        | PID_POSITION_ LIMIT_HIGH              | 0x7FFFFFFF h  | -0x80000000 h | 0x7FFFFFFF h |
| RW | 0x63 h | MODE_RAMP_ MODE_MOTION                |               |               |              |
|    |        | MODE_MOTION                           | 0x0 h         | 0x0 h         | 0xF h        |
|    |        | MODE_PID_SMPL                         | 0x0 h         | 0x0 h         | 0x7F h       |
|    |        | MODE_PID_TYPE                         | 0x0 h         | 0x0 h         | 0x1 h        |


RW

0x64

PID\_TORQUE\_FLUX\_

|    | h      | TARGET                  |       |                           |                         |
|----|--------|-------------------------|-------|---------------------------|-------------------------|
|    |        | PID_FLUX_TARGET         | 0x0 h | -0x8000 h                 | 0x7FFF h                |
|    |        | PID_TORQUE_ TARGET      | 0x0 h | -0x8000 h                 | 0x7FFF h                |
| RW | 0x65 h | PID_TORQUE_FLUX_ OFFSET |       |                           |                         |
|    |        | PID_FLUX_OFFSET         | 0x0 h | -0x8000 h                 | 0x7FFF h                |
|    |        | PID_TORQUE_ OFFSET      | 0x0 h | -0x8000 h                 | 0x7FFF h                |
| RW | 0x66 h | PID_VELOCITY_ TARGET    |       |                           |                         |
|    |        | PID_VELOCITY_ TARGET    | 0x0 h | -0x80000000 h             | 0x7FFFFFFF h            |
| RW | 0x67 h | PID_VELOCITY_ OFFSET    |       |                           |                         |
|    |        | PID_VELOCITY_ OFFSET    | 0x0 h | -0x80000000 h             | 0x7FFFFFFF h            |
| RW | 0x68 h | PID_POSITION_ TARGET    |       |                           |                         |
|    |        | PID_POSITION_ TARGET    | 0x0 h | -0x80000000 h             | 0x7FFFFFFF h            |
| R  | 0x69 h | PID_TORQUE_FLUX_ ACTUAL |       |                           |                         |
|    |        | PID_FLUX_ACTUAL         | 0x0 h | -0x8000 h                 | 0x7FFF h                |
|    |        | PID_TORQUE_ ACTUAL      | 0x0 h | -0x8000 h                 | 0x7FFF h                |
| R  | 0x6A h | PID_VELOCITY_ ACTUAL    |       |                           |                         |
|    |        | PID_VELOCITY_ ACTUAL    | 0x0 h | -0x80000000 h             | 0x7FFFFFFF h            |
| RW | 0x6B h | PID_POSITION_ ACTUAL    |       |                           |                         |
|    |        | PID_POSITION_ ACTUAL    | 0x0 h | -0x80000000 h             | 0x7FFFFFFF h            |
| R  | 0x6C h | PID_ERROR_DATA          |       |                           |                         |
|    |        | PID_TORQUE_ERROR        | 0x0 h | -0x80000000 h -0x80000000 | 0x7FFFFFFF h 0x7FFFFFFF |
|    |        | PID_FLUX_ERROR          | 0x0 h | -0x80000000 h             | h 0x7FFFFFFF h          |
|    |        | PID_VELOCITY_ ERROR     | 0x0 h | h                         |                         |


PID\_POSITION\_

0x0

-0x80000000

|    |        | ERROR                         | h     | h             | h            |
|----|--------|-------------------------------|-------|---------------|--------------|
|    |        | PID_TORQUE_ ERROR_SUM         | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PID_FLUX_ERROR_ SUM           | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PID_VELOCITY_ ERROR_SUM       | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PID_POSITION_ ERROR_SUM       | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
| RW | 0x6D h | PID_ERROR_ADDR PID_ERROR_ADDR |       |               |              |
|    |        |                               | 0x0 h | 0x0 h         | 0x7 h        |
| RW | 0x6E h | INTERIM_DATA                  |       |               |              |
|    |        | PIDIN_TARGET_ TORQUE          | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PIDIN_TARGET_FLUX             | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PIDIN_TARGET_ VELOCITY        | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PIDIN_TARGET_ POSITION        | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PIDOUT_TARGET_ TORQUE         | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PIDOUT_TARGET_ FLUX           | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PIDOUT_TARGET_ VELOCITY       | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | PIDOUT_TARGET_ POSITION       | 0x0 h | -0x80000000 h | 0x7FFFFFFF h |
|    |        | FOC_IUX                       | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_IWY                       | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_IV                        | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_IA                        | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_IB                        | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_ID                        | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_IQ                        | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_UD                        | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_UQ                        | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_UD_LIMITED                | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_UQ_LIMITED                | 0x0 h | -0x8000 h     | 0x7FFF h     |
|    |        | FOC_UA                        | 0x0 h | -0x8000 h     | 0x7FFF h     |

0x7FFFFFFF


FOC\_UB

0x0

-0x8000

0x7FFF

|                             | h     | h         | h        |
|-----------------------------|-------|-----------|----------|
| FOC_UUX                     | 0x0 h | -0x8000 h | 0x7FFF h |
| FOC_UWY                     | 0x0 h | -0x8000 h | 0x7FFF h |
| FOC_UV                      | 0x0 h | -0x8000 h | 0x7FFF h |
| PWM_UX                      | 0x0 h | -0x8000 h | 0x7FFF h |
| PWM_WY                      | 0x0 h | -0x8000 h | 0x7FFF h |
| PWM_V                       | 0x0 h | -0x8000 h | 0x7FFF h |
| ADC_I_0                     | 0x0 h | -0x8000 h | 0x7FFF h |
| ADC_I_1                     | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_FLUX_ACTUAL_ DIV256     | 0x0 h | -0x80 h   | 0x7F h   |
| PID_TORQUE_ ACTUAL_DIV256   | 0x0 h | -0x80 h   | 0x7F h   |
| PID_FLUX_TARGET_ DIV256     | 0x0 h | -0x80 h   | 0x7F h   |
| PID_TORQUE_ TARGET_DIV256   | 0x0 h | -0x80 h   | 0x7F h   |
| PID_TORQUE_ ACTUAL          | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_TORQUE_ TARGET          | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_FLUX_ACTUAL             | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_FLUX_TARGET             | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_VELOCITY_ ACTUAL_DIV256 | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_VELOCITY_ TARGET_DIV256 | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_VELOCITY_ ACTUAL_LSB    | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_VELOCITY_ TARGET_LSB    | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_POSITION_ ACTUAL_DIV256 | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_POSITION_ TARGET_DIV256 | 0x0 h | -0x8000 h | 0x7FFF h |
| PID_POSITION_ ACTUAL_LSB    | 0x0 h | -0x8000 h | 0x7FFF h |


PID\_POSITION\_

0x0

-0x8000

0x7FFF

|    |        | TARGET_LSB                       | h        | h             | h                   |
|----|--------|----------------------------------|----------|---------------|---------------------|
|    |        | FF_VELOCITY                      | 0x0 h    | -0x80000000 h | 0x7FFFFFFF h 0x7FFF |
|    |        | FF_TORQUE                        | 0x0 h    | -0x8000 h     | h                   |
|    |        | ACTUAL_VELOCITY_ PPTM            | 0x0 h    | -0x80000000 h | 0x7FFFFFFF h        |
|    |        | REF_SWITCH_STATUS                | 0x0 h    | 0x0 h         | 0xFFFF h            |
|    |        | HOME_POSITION                    | 0x0 h    | -0x80000000 h | 0x7FFFFFFF h        |
|    |        | LEFT_POSITION                    | 0x0 h    | -0x80000000 h | 0x7FFFFFFF h        |
|    |        | RIGHT_POSITION                   | 0x0 h    | -0x80000000 h | 0x7FFFFFFF h        |
|    |        | ENC_INIT_HALL_ STATUS            | 0x0 h    | 0x0 h         | 0xFFFF h            |
|    |        | ENC_INIT_HALL_PHI_ E_ABN_OFFSET  | 0x0 h    | 0x0 h         | 0xFFFF h            |
|    |        | ENC_INIT_HALL_PHI_ E_AENC_OFFSET | 0x0 h    | 0x0 h         | 0xFFFF h            |
|    |        | ENC_INIT_HALL_PHI_ A_AENC_OFFSET | 0x0 h    | 0x0 h         | 0xFFFF h            |
|    |        | SINGLE_PIN_IF_ TARGET_TORQUE     | 0x0 h    | -0x8000 h     | 0x8000 h            |
|    |        | SINGLE_PIN_IF_ PWM_DUTY_CYCLE    | 0x0 h    | -0x8000 h     | 0x8000 h            |
|    |        | SINGLE_PIN_IF_ TARGET_VELOCITY   | 0x0 h    | -0x80000000 h | 0x7FFFFFFF h        |
|    |        | SINGLE_PIN_IF_ TARGET_POSITION   | 0x0 h    | -0x80000000 h | 0x7FFFFFFF h        |
| RW | 0x6F h | INTERIM_ADDR INTERIM_ADDR        | 0x0 h    | 0x0 h         | 0xD7 h              |
| RW | 0x75 h | ADC_VM_LIMITS ADC_VM_LIMIT_LOW   | 0xFFFF h | 0x0 h         | 0xFFFF h            |
|    |        | ADC_VM_LIMIT_HIGH                | 0xFFFF h | 0x0 h         | 0xFFFF h            |
| R  | 0x76 h | TMC4671_INPUTS_ RAW              |          |               |                     |
|    |        | A of ABN_RAW                     | 0x0 h    | 0x0 h         | 0x1 h               |
|    |        | B of ABN_RAW                     | 0x0 h    | 0x0 h         | 0x1 h               |
|    |        | N of ABN_RAW                     | 0x0 h    | 0x0 h         | 0x1 h               |
|    |        | -                                | 0x0 h    | 0x0 h         | 0x1 h               |
|    |        | A of ABN_2_RAW                   | 0x0 h    | 0x0 h         | 0x1 h               |


B of ABN\_2\_RAW

0x0

0x0

0x1

|    |        |                         | h     | h     | h     |
|----|--------|-------------------------|-------|-------|-------|
|    |        | N of ABN_2_RAW          | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | HALL_UX of HALL_ RAW    | 0x0 h | 0x0 h | 0x1 h |
|    |        | HALL_V of HALL_RAW      | 0x0 h | 0x0 h | 0x1 h |
|    |        | HALL_WY of HALL_ RAW    | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | REF_SW_R_RAW            | 0x0 h | 0x0 h | 0x1 h |
|    |        | REF_SW_H_RAW            | 0x0 h | 0x0 h | 0x1 h |
|    |        | REF_SW_L_RAW            | 0x0 h | 0x0 h | 0x1 h |
|    |        | ENABLE_IN_RAW           | 0x0 h | 0x0 h | 0x1 h |
|    |        | STP of DIRSTP_RAW       | 0x0 h | 0x0 h | 0x1 h |
|    |        | DIR of DIRSTP_RAW       | 0x0 h | 0x0 h | 0x1 h |
|    |        | PWM_IN_RAW              | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | HALL_UX_FILT            | 0x0 h | 0x0 h | 0x1 h |
|    |        | HALL_V_FILT             | 0x0 h | 0x0 h | 0x1 h |
|    |        | HALL_WY_FILT            | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | PWM_IDLE_L_RAW          | 0x0 h | 0x0 h | 0x1 h |
|    |        | PWM_IDLE_H_RAW          | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
|    |        | -                       | 0x0 h | 0x0 h | 0x1 h |
| R  | 0x77 h | TMC4671_OUTPUTS_ RAW    |       |       |       |
|    |        | TMC4671_OUTPUTS_ RAW[0] | 0x0 h | 0x0 h | 0x1 h |
|    |        | TMC4671_OUTPUTS_ RAW[1] | 0x0 h | 0x0 h | 0x1 h |
|    |        | TMC4671_OUTPUTS_ RAW[2] | 0x0 h | 0x0 h | 0x1 h |


TMC4671\_OUTPUTS\_

0x0

0x0

0x1

|    |        | RAW[3]                  | h            | h             | h            |
|----|--------|-------------------------|--------------|---------------|--------------|
|    |        | TMC4671_OUTPUTS_ RAW[4] | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | TMC4671_OUTPUTS_ RAW[5] | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | TMC4671_OUTPUTS_ RAW[6] | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | TMC4671_OUTPUTS_ RAW[7] | 0x0 h        | 0x0 h         | 0x1 h        |
| RW | 0x78 h | STEP_WIDTH              |              |               |              |
|    |        | STEP_WIDTH              | 0x0 h        | -0x80000000 h | 0x7FFFFFFF h |
| RW | 0x79 h | UART_BPS                |              |               |              |
|    |        | UART_BPS                | 0x00009600 h | 0x0 h         | 0xFFFFFF h   |
| RW | 0x7B h | GPIO_dsADCI_ CONFIG     |              |               |              |
|    |        | GPIO_dsADCI_ CONFIG[0]  | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | GPIO_dsADCI_ CONFIG[1]  | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | GPIO_dsADCI_ CONFIG[2]  | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | GPIO_dsADCI_ CONFIG[3]  | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | GPIO_dsADCI_ CONFIG[4]  | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | GPIO_dsADCI_ CONFIG[5]  | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | GPIO_dsADCI_ CONFIG[6]  | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | GPO                     | 0x0 h        | 0x0 h         | 0xFF h       |
|    |        | GPI                     | 0x0 h        | 0x0 h         | 0xFF h       |
| RW | 0x7C h | STATUS_FLAGS            |              |               |              |
|    |        | STATUS_FLAGS[0]         | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | STATUS_FLAGS[1]         | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | STATUS_FLAGS[2]         | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | STATUS_FLAGS[3]         | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | STATUS_FLAGS[4]         | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | STATUS_FLAGS[5]         | 0x0 h        | 0x0 h         | 0x1 h        |
|    |        | STATUS_FLAGS[6]         | 0x0 h        | 0x0 h         | 0x1 h        |


STATUS\_FLAGS[7]

0x0

0x0

0x1

|    |        |                          | h     | h     | h            |
|----|--------|--------------------------|-------|-------|--------------|
|    |        | STATUS_FLAGS[8]          | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[9]          | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[10]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[11]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[12]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[13]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[14]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[15]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[16]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[17]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[18]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[19]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[20]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[21]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[22]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[23]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[24]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[25]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[26]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[27]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[28]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[29]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[30]         | 0x0 h | 0x0 h | 0x1 h        |
|    |        | STATUS_FLAGS[31]         | 0x0 h | 0x0 h | 0x1 h        |
| RW | 0x7D h | STATUS_MASK WARNING_MASK |       |       |              |
|    |        |                          | 0x0 h | 0x0 h | 0xFFFFFFFF h |


VCCIO

VCCIO

VCCIO r

VCCIO

VCC\_CORE

ЧН

VCC\_CORE

=

SPI\_SCK

SPI MISO

SPI\_SCK

SPI\_MISO

SPI MOSI

SPI\_MOSI

UART\_RD L,

UART\_RXD

UART\_TXD

GPIO\_0 ... GPIO\_7 |+

GPIO\_0... GPIO\_1 |*

STATUS

STATUS C*

ENI

nRST |

nRST |

CLK M

+5V

+5V

V5

V5

·

·

Analog

Analog

GPIs

GPIs

Dig. Hall IF

Dig. ABN Encoders

Dig. Hall IF

$ &gt;5

Dig. ABN Encoders

HALL\_

ENCI\_N

## 8 Pinning

Control

Control

ADC Engine and Analog Frontend

AAAAA

AAAAA

0000

Sod

AENC\_VN\_POS

Analog Encoder IF

Gate Driver

·


Analog Encoder IF

Figure 39: TMC4671 Pinout with 3 phase Power stage and BLDC Motor

Figure 40: TMC4671 Pinout with Stepper Motor


PW\_!

Ref. Switches

Ref. Switches

I

PWM\_I

PWM Engine

PWM Engine

PWM\_UX1\_H

PWM\_UX1\_H

PWM\_UX1\_L

PWM UX1 L

PWM\_VX2\_H

PWM\_VX2\_H

PWM\_VX2\_L

PWMVX2L

Gate Driver

+ VM

(Б)

HE

Stepper Motor

BLDC Motor

N

-FB

mm

N FB


VCCIO

VCCIO

VCC\_CORE

SPICS FE

SPI\_SCK

SPI\_MISO

SPI MOSI

UART\_RD

UART\_TXD

GPIO\_0... GPIO\_1 De

STATUS

ENI

+5V

V5

·

Register Bank &amp; Interfacing

7

Analog

GPIs

## Info

IO

Dig. Hall IF

HALL\_

Dig. ABN Encoders

ENC1\_BR

sod

Analog Encoder IF

PWM\_UX1\_H

Figure 41: TMC4671 Pinout with DC Motor or Voice Coil


All power supply pins (VCC, VCC\_CORE) must be connected.

Analog inputs (AI) are 5V single ended or differential inputs (Input range: GNDA to V5). Use voltage dividers or operational amplifiers to scale down higher input voltages.

All ground pins (GND, GNDA, ...) must be connected.

Digital inputs (I) resp. (IO) are 3.3V single ended inputs.

Table 32: Pin Type Definition

| AI   | analog input, 3.3V                                            |
|------|---------------------------------------------------------------|
| I    | digital input, 3.3V                                           |
| IO   | digital input or digital output, direction programmable, 3.3V |
| O    | digital output, 3.3V                                          |

Description

PWM\_I

Ref. Switches

DC Motor


## 9 TMC4671 Pin Table

Name

| nRST       |   50 | I   | active low reset input                                                                  |
|------------|------|-----|-----------------------------------------------------------------------------------------|
| CLK        |   51 | I   | clock input; needs to be 25 MHzfor correct timing                                       |
| TEST       |   54 | I   | TEST input, must be connected to GND                                                    |
| ENI        |   55 | I   | enable input; If high, controllers and PWMare en- abled                                 |
| ENO        |   32 | O   | enable output; feeds through ENI when CLK is ap- plied and IC is not in reset condition |
| STATUS     |   12 | O   | output for interrupt of CPU (Warning & Status Change)                                   |
| SPI_nSCS   |    6 | I   | SPI active low chip select input                                                        |
| SPI_SCK    |    7 | I   | SPI clock input                                                                         |
| SPI_MOSI   |    8 | I   | SPI master out slave input                                                              |
| SPI_MISO   |    9 | O   | SPI master in slave output, high impedance, when SPI_nSCS = '1'                         |
| UART_RXD   |   10 | I   | UART receive data RxD for in-system-user com- munication channel                        |
| UART_TXD   |   11 | O   | UART transmit data TXD for in-system-user com- munication channel                       |
| PWM_I      |   58 | I   | PWMinput for target value generation                                                    |
| DIR        |   56 | I   | direction input of step-direction interface                                             |
| STP        |   57 | I   | step pulse input for step-direction interface                                           |
| HALL_UX    |   38 | I   | digital hall input H1 for 3-phase (U) or 2-phase (X)                                    |
| HALL_V     |   37 | I   | digital hall input H2 for 3-phase (V)                                                   |
| HALL_WY    |   36 | I   | digital hall input H3 for 3-phase (W) or 2-phase (Y)                                    |
| ENC_A      |   35 | I   | A input of incremental encoder                                                          |
| ENC_B      |   34 | I   | B input of incremental encoder                                                          |
| ENC_N      |   33 | I   | N input of incremental encoder                                                          |
| ENC2_A     |   64 | I   | A input of incremental encoder                                                          |
| ENC2_B     |   65 | I   | B input of incremental encoder                                                          |
| ENC2_N     |   66 | I   | N input of incremental encoder                                                          |
| REF_L      |   67 | I   | Left (L) reference switch                                                               |
| REF_H      |   68 | I   | Home (H) reference switch                                                               |
| REF_R      |   69 | I   | Right (R) reference switch                                                              |
| ADC_I0_POS |   16 | AI  | pos. input for phase current signal measurement I0 (I_U, I_X)                           |


Pin

IO

Description

Name

Pin

IO

Description

| ADC_I0_NEG                        |   17 | AI   | neg. input for phase current signal measurement I0 (I_U, I_X)                                                                                |
|-----------------------------------|------|------|----------------------------------------------------------------------------------------------------------------------------------------------|
| ADC_I1_POS                        |   18 | AI   | pos. input for phase current signal measurement I1 (I_V, I_W, I_Y)                                                                           |
| ADC_I1_NEG                        |   19 | AI   | neg. input for phase current signal measurement I1 (I_V, I_W, I_Y)                                                                           |
| ADC_VM                            |   20 | AI   | analog input for motorsupplyvoltage divider (VM) measurement                                                                                 |
| AGPI_A                            |   21 | AI   | analog general purpose input A (analog GPI)                                                                                                  |
| AGPI_B                            |   22 | AI   | analog general purpose input B (analog GPI)                                                                                                  |
| AENC_UX_POS                       |   25 | AI   | pos. analog input for Hall or analog encoder sig- nal, 3-phase (U) or 2-phase (X (cos))                                                      |
| AENC_UX_NEG                       |   26 | AI   | neg. analog input for Hall or analog encoder sig- nal, 3-phase (U) or 2-phase (X (cos))                                                      |
| AENC_VN_POS                       |   27 | AI   | pos. analog input for Hall or analog encoder sig- nal, 3-phase (V) or 2-phase (N)                                                            |
| AENC_VN_NEG                       |   28 | AI   | neg. analog input for Hall or analog encoder sig- nal, 3-phase (V) or 2-phase (N)                                                            |
| AENC_WY_POS                       |   29 | AI   | pos. analog input for Hall or analog encoder sig- nal, 3-phase (W) or 2-phase (Y (sin))                                                      |
| AENC_WY_NEG                       |   30 | AI   | neg. analog input for Hall or analog encoder sig- nal, 3-phase (W) or 2-phase (Y (sin))                                                      |
| GPIO0 / ADC_I0_MCD                |   70 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC output MDAC for ADC_I_0                                     |
| GPIO1 / ADC_I1_MCD                |   71 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC output MDAC for ADC_I_1                                     |
| GPIO2 / ADC_VM_MCD                |   74 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC output MDAC for ADC_VM_MCD                                  |
| GPIO3 / AGPI_A_MCD / DBGSPI_nSCS  |   75 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC output MDAC for AENC_UX_MCD, SPI debug port pin DBGSPI_nSCS |
| GPIO4 / AGPI_B_MCD / DBGSPI_SCK   |   76 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC output MDAC for AENC_VN_MCD, SPI debug port pin DBGSPI_SCK  |
| GPIO5 / AENC_UX_MCD / DBGSPI_MOSI |    1 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC output MDAC for AENC_WY_MCD, SPI debug port pin DBGSPI_MOSI |


Name

Pin

IO

Description

Table 33: Functional Pin Description

| GPIO6 / AENC_VN_MCD / DBGSPI_MISO   |   4 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC out- put MDAC for AGPI_A_MCD, SPI debug port pin DBGSPI_MISO   |
|-------------------------------------|-----|------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| GPIO7 / AENC_WY_MCD / DBGSPI_TRG    |   5 | IO   | GPIO or ∆Σ -Demodulator clock input MCLKI, clock output MCLKO, or single bit DAC out- put MDAC for AGPI_B_MCD, SPI debug port pin DBGSPI_TRG    |
| PWM_IDLE_H                          |  59 | I    | idle level of high side gate control signals (not used)                                                                                         |
| PWM_IDLE_L                          |  60 | I    | idle level of low side gate control signals (not used)                                                                                          |
| PWM_UX1_H                           |  39 | O    | high side gate control output U(3-phase) resp. X1 (2-phase)                                                                                     |
| PWM_UX1_L                           |  40 | O    | low side gate control output U (3-phase) resp. X1 (2-phase)                                                                                     |
| PWM_VX2_H                           |  41 | O    | high side gate control output V (3-phase) resp. X2 (2-phase)                                                                                    |
| PWM_VX2_L                           |  42 | O    | low side gate control output V (3-phase) resp. X2 (2-phase)                                                                                     |
| PWM_WY1_H                           |  46 | O    | high side gate control output W(3-phase) resp. Y1 (2-phase)                                                                                     |
| PWM_WY1_L                           |  47 | O    | low side gate control output W(3-phase) resp. Y1 (2-phase)                                                                                      |
| PWM_Y2_H                            |  48 | O    | high side gate control output Y2 (2-phase only)                                                                                                 |
| PWM_Y2_L                            |  49 | O    | low side gate control output Y2 (2-phase only)                                                                                                  |
| BRAKE                               |  31 | O    | brake chopper control output signal                                                                                                             |

Feedback input pins that are not needed in target application can be left open or tied to GND.


Name

Pin

IO

Description

| VCCIO1   | 2   | 3.3V   | digital IO supply voltage; use 100nF decoupling capacitor            |
|----------|-----|--------|----------------------------------------------------------------------|
| VCCIO2   | 13  | 3.3V   | digital IO supply voltage; use 100nF decoupling capacitor            |
| VCCIO3   | 43  | 3.3V   | digital IO supply voltage; use 100nF decoupling capacitor            |
| VCCIO4   | 52  | 3.3V   | digital IO supply voltage; use 100nF decoupling capacitor            |
| VCCIO5   | 61  | 3.3V   | digital IO supply voltage; use 100nF decoupling capacitor            |
| VCCIO6   | 72  | 3.3V   | digital IO supply voltage; use 100nF decoupling capacitor            |
| GNDIO1   | 3   | 0V     | digital IO ground                                                    |
| GNDIO2   | 14  | 0V     | digital IO ground                                                    |
| GNDIO3   | 44  | 0V     | digital IO ground                                                    |
| GNDIO4   | 53  | 0V     | digital IO ground                                                    |
| GNDIO5   | 62  | 0V     | digital IO ground                                                    |
| GNDIO6   | 73  | 0V     | digital IO ground                                                    |
| VCCCORE1 | 15  | 1.8V   | digital core supply voltage output; use 100nF decoupling ca- pacitor |
| VCCCORE2 | 45  | 1.8V   | digital core supply voltage output; use 100nF decoupling ca- pacitor |
| VCCCORE3 | 63  | 1.8V   | digital core supply voltage output; use 100nF decoupling ca- pacitor |
| V5       | 23  | 5V     | analog reference voltage                                             |
| GNDA     | 24  | 0V     | analog reference ground                                              |
| GNDPAD   | -   | 0V     | bottom ground pad                                                    |

Table 34: Supply Voltage Pins and Ground Pins


## 10 Electrical Characteristics

The maximum ratings may not be exceeded under any circumstances. Operating the circuit at or near more than one maximum rating at a time for extended periods shall be avoided by application design.

## 10.1 Absolute Maximum Ratings

Parameter

Table 35: Absolute Maximum Ratings

| Digital I/O supply voltage                                        | VCCIO    |     |   3.6 | V   |
|-------------------------------------------------------------------|----------|-----|-------|-----|
| Logic input voltage                                               | VI       |     |   3.6 | V   |
| Maximum current drawn on VCCIO with no load on pins               | I_IO     |     |  70   | mA  |
| Maximum current drawn on VCCIO with no load on pins and clock off | I_IO_0Hz |     |   3   | mA  |
| Maximum current drawn on V5 at fCLK = 25MHz                       | I_V5     |     |  25   | mA  |
| Maximumcurrent to / from digital pins and analog low voltage I/Os | IIO      |     |  10   | mA  |
| Junction temperature                                              | TJ       | -40 | 125   | °C  |
| Storage temperature                                               | TSTG     | -55 | 150   | °C  |
| ESD-Protection for interface pins (Human body model, HBM)         | VESDAP   |     |   2   | kV  |
| ESD-Protection for handling (Human body model, HBM)               | VESD1    |     |   2   | kV  |
| ADC input voltage                                                 | VAI      |   0 |   5   | V   |

VCCCORE is generated internally from VCCIO and shall not be overpowered by external supply.

## 10.2 Electrical Characteristics

## 10.2.1 Operational Range

Parameter

Symbol

Min

Max

Unit

Table 36: Operational Range

| Junction temperature            | TJ       |   -40 |   125 | °C   |
|---------------------------------|----------|-------|-------|------|
| Digital I/O 3.3V supply voltage | VIO3V    |  3.15 |  3.45 | V    |
| Core supply voltage             | VCC_CORE |  1.65 |  1.95 | V    |

The ∆Σ ADCs can operate in differential or single ended mode. In differential mode the differential input voltage range must be in between -2.5V and +2.5V. However, it is recommended to use the input voltage range from -1.25V to 1.25V, due to non-linearity of ∆Σ ADCs. In Single ended mode the operational input range of the positive input channel should be between 0V and 2.5V. Recommended maximum input voltage is 1.25V.


Symbol

Min

Max

Unit

## 10.2.2 DC Characteristics

DC characteristics contain the spread of values guaranteed within the specified supply voltage range unless otherwise specified. Typical values represent the average value of all parts measured at +25 °C. Temperature variation also causes stray to some values. A device with typical values will not leave Min/Max range within the full temperature range.

Parameter

Symbol

Condition

Table 37: DC Characteristics

| Input voltage low level         | VINL     | VCCIO = 3.3V   |    -0.3 |     |   0.8 | V   |
|---------------------------------|----------|----------------|---------|-----|-------|-----|
| Input voltage high level        | VINH     | VCCIO = 3.3V   |    2.3  |     |   3.6 | V   |
| Input with pull-down            |          | VIN = 3.3V     |    5    |  30 | 110   | µ A |
| Input with pull-up              |          | VIN = 0V       | -110    | -30 |  -5   | µ A |
| Input low current               |          | VIN = 0V       |  -10    |     |  10   | µ A |
| Input high current              |          | VIN = VCCIO    |  -10    |     |  10   | µ A |
| Output voltage low level        | VOUTL    | VCCIO = 3.3V   |    0.4  |     |       | V   |
| Output voltage high level       | VOUTH    | VCCIO = 3.3V   |    2.64 |     |       | V   |
| Output driver strength standard | IOUT_DRV |                |    4    |     |       | mA  |
| Input impedance of Analog Input | R_ADC    | TJ = 25°C      |   85    | 100 | 115   | k Ω |

All I/O lines include Schmitt-Trigger inputs to enhance noise margin.

Min

Typ

Max

Unit


+Vcc

+Vccio

## 11 Sample Circuits

## 11.1 Supply Pins

ENC\_A

Please consider electrical characteristics while designing electrical circuitry. Most Sample Circuits in this chapter were taken from the evalutation board for the TMC4671 (TMC4671-EVAL).

Please provide VCCIO and V5 to the TMC4671. VCC\_CORE is internally generated and needs just an external decoupling capacitor. Place one 100nF decoupling capacitor at every supply pin. Table 38 lists additional needed decoupling capacitors.

| V5      | 5V   | 4.7uF         |
|---------|------|---------------|
| VCCIO   | 3.3V | 4.7uF & 470nF |
| VCCCORE | 1.8V | none          |

Pin Name

Supply Voltage

Additional Cap.

Table 38: Additional decoupling capacitors for supply voltages

## 11.2 Clock and Reset Circuitry

## 11.3 Digital Encoder, Hall Sensor Interface and Reference Switches

The TMC4671 needs an external oscillator for correct operation at 25 MHz. Lower frequency results in respective scaling of timings. Higher frequency is not supported. The internally generated active low reset can be externally overwritten. If users want to toggle the reset, a pulse length of at least 500 ns is recommended. When not used, please apply a 10k Pull up resistor and make sure all supply voltages are stable.

Digital encoders, Hall sensors and reference switches usually operate on a supply voltage of 5V. As the TMC4671 is usually operated at a VCCIO Voltage of 3.3V, a protection circuit for the TMC4671 input pin is needed. In fig. 42 a sample circuit for the ENC\_A signal is shown, which can be reused for all encoder and Hall signals as well as for reference switch signals. Parametrization of the components is given in table 39 for different operations.


Figure 42: Sample Circuit for Interfacing of an Encoder Signal


1... 4Vo

+5V

T

+2.5V

TMC4671

AENC\_UX\_NEG

Application

Table 39: Reference Values for circuitry components

|                    | R PU   | R PD   | R LN   | C P   |
|--------------------|--------|--------|--------|-------|
| 5 V Encoder signal | 4K7    | n.c.   | 100R   | 100pF |

The raw signal (ENC\_A\_RAW) is divided by a voltage divider and filtered by a low-pass filter. A pull up resistor is applied for open collector encoder output signals. Diodes protect the input pin (ENC\_A) against over- and undervoltage. The cutoff-frequency of the low-pass is:

## 11.4 Analog Frontend

$$f _ { c } = \frac { 1 } { 2 \, \pi \, R _ { P D } C _ { P } }$$

Analog Encoders are encoding the motor position into sinusoidal signals. These signals need to be digitalized by the TMC4671 in order to determine the rotor position. The input voltage range depends on V5 input, which is usually 5V and GNDA (usually 0V). Due to nonlinearity issues of the ADC near input limits, an ADC input value from 1V to 4V is recommended. For a single ended application, the sample circuit from fig. 43 can be used. All single ended analog input pins (AGPI\_A, AGPI\_B and ADC\_VM) have their negative input value tied to GNDA internally, so this sample circuit can also be used for them.

Figure 43: Sample Circuit for Interfacing of a single ended analog signal


If the power stage and the TMC4671 share a common ground, the ADC\_VM input signal can be generated by a voltage divider to scale the voltage down to the needed range.

## 11.5 Phase Current Measurement

If the analog encoder has differential output signals, these can be used without signal conditioning (no OP AMPs), when voltage range matches. Differential analog inputs can be used to digitize differential analog input signals with high common mode voltage error suppression.

The TMC4671 requires two phase currents of a 2 or 3 phase motor to be measured. For a DC Motor only onecurrent in the phase needs to be measured (see Fig. 45). In the ADC engine mapping of current signals to motor phases can be changed. Default setting is I0 to be the current running into the motor in phase U for a 3 phase motor. Respectively the current running into the motor from half-bridge X1 of a 2 phase motor. Figs. 44 and 45 illustrates the currents to be measured and their positive direction.


Y2\_HS

Y1\_HS

X2\_HS

X2\_HS

X1\_HS

X1 HS

Y2\_LS

Y1\_LS

X2\_LS

X1 LS

X2\_LS

X1 LS

-

+ VM

+ VM

HE

W\_HS

V\_HS

BLDC Motor

Motor mm

Figure 44: Phase current measurement: Current directions for 2 and 3 phase motors


Figure 45: Phase current measurement: Current direction for DC or Voice Coil Motor


There are two main options for measuring the phase currents as described above. First option is to use a shunt resistor and a shunt amplifier like the LT1999 or the AD8418A. The other option is to use a real current sensor, which uses the Hall effect or other magnetic effects to implement an isolated current measurement. Shunt measurement might be the more cost-effective solution for low voltage applications up to 100V, while current sensors are more useful at higher voltage levels.

In general the sample circuit in fig. 46 can be used for shunt measurement circuitry. Please consider design guidelines of shunt amplifier supplier additionally. TRINAMIC also supplies power stage boards


+ VM

Rosense L

+5V

with current shunt measurement circuitry (TMC-UPS10A/70V-EVAL). For current measurement also current sensors with voltage output can be used. These could use the Hall effect or other magnetic effects. Main concerns to take about is bandwidth, accuracy and measurement range.

Figure 46: Current Shunt Amplifier Sample Circuit


## 11.6 Power Stage Interface

The TMC4671 is equipped with a configurable PWM engine for control of various gate drivers. Gate driver switch signals can be matched to power stage needs. This includes signal polarities, frequency, BBMtimes for low and high side switches, and an enable signal. Please consider gate driver circuitry, when connecting to the TMC4671.


## 12 Setup Guidelines

For easy setup of the TMC4671 on a given hardware platform like the TMC4671 Evaluation-Kit, the user should follow these general guidelines in order to safely set up the system for various modes of operation.

## Info

These guidelines fit to hardware platforms which are comparable to the TMC4671-Evaluation Kit. If system structure differs, configuration has to be adjusted.

Please also make use of the RTMI Adapter and the TMCL IDE to setup the system as it reduces commissioning time significantly.

## Step 0: Setup of SPI communication

## Step 1: Check connections

As a first step of the configuration of the TMC4671 the SPI communication should be tested by reading and writing for example to the first registers for identification of the silicon. If communication fails, please check CLK and nRST signals. For easy software setup the TMC API provided on the TRINAMIC website can be used.

The user should choose the connected motor and the number of polepairs by setting register MOTOR\_ TYPE\_N\_POLE\_PAIRS. For a DC motor the number of pole pairs should be set to one. The PWM can be configured with the corresponding registers PWM\_POLARITIES (Gate Driver Polarities), PWM\_MAXCNT (PWM Frequency), PWM\_BBM\_H\_BBM\_L (BBM times), and PWM\_SV\_CHOP (PWM mode). After setting the register PWM\_SV\_CHOP to 7 the PWM is on and ready to use. Please check PWM outputs after turning on the PWM, if you are using a new hardware design.

Register TMC4671\_INPUTS\_RAW can be accessed to see if all connected digital inputs are working correctly e.g. sensor signals can be checked by turning the motor manually. Step 2: Setup of PWM and Gatedriver configuration

Step 3: Open Loop Mode

Please setup the current measurement by choosing your applications ADC configuration. Make sure to match decimation rate of the Delta Sigma ADCs to your chosen PWM frequency.

In the Open Loop Mode the motor is turned by applying voltage to the motor. This mode is useful for test and setup of ADCs and position sensors. It is activated by setting the corresponding registers for PHI\_ E\_SELECTION, and MODE\_MOTION. With UD\_EXT the applied voltage can be regulated upwards until the motor starts to turn. Acceleration and target velocity can be changed by their respective registers. Step 4: Setup of ADC for current measurement

When the motor turns in Open Loop Mode the current measurement can be easily calibrated. Please match offset and gain of phase current signals by setting the corresponding registers. Please also make sure for a new hardware setup, that current measurements and PWM channels are matched. This can be done by matching phase voltages and phase currents. Register ADC\_I\_SELECT can be used to switch relations.

## Step 5: Setup of Feedback Systems

Please configure your application's feedback system and configure position and velocity signal switches accordingly inside the FOC. Configure controller output limits according to you needs.

In Open Loop Mode also the feedback systems can be checked for correct operation. Please configure registers related to used position sensor(s) and compare against Open Loop angles. Use encoder initialization routines to set angle offsets for relative position encoders according to application needs. Step 6: Setup of FOC Controllers

Setup PI controller parameters for used FOC controllers. Start with the current controller, followed by the velocity controller, followed by the position controller. Stop configuration at your desired cascade level. TRINAMIC recommends to set the PI controller parameters by support of the RTMI, as it supports realtime access to registers and the TMCL IDE offers tools for automated controller tuning. Controller tuning without realtime access might lead to poor performance. Please choose afterwards your desired Motion Mode and feed in reference values.


PIN 1 CORNER

76

## Step 7: Advanced Functions

## 13 Package Dimensions

1ccc/c

SEATING PLANE

For performance improvements Biquad filters and feed forward control can be applied.

Package: QFN76, 0.4 mm pitch, size 11.5 mm x 6.5 mm.

r 68x L

Ш000U

52

[* eee C|A|B]

1 397

8x L11

M

A1

(A3)


aannndnnnnnnnnnnoв

e -

Figure 47: QFN76 Package Outline

QFN76 Package Dimensions in mm

| Description     | Dimension[mm]   | min.      | typ.      | max.      |
|-----------------|-----------------|-----------|-----------|-----------|
| Total Thickness | A               | 0.80      | 0.85      | 0.90      |
| Stand Off       | A1              | 0.00      | 0.035     | 0.05      |
| Mold Thickness  | A2              | -         | 0.65      | -         |
| L/F Thickness   | A3              | 0.203 REF | 0.203 REF | 0.203 REF |
| Lead Width      | b               | 0.15      | 0.2       | 0.25      |
| Body Width      | D               | 10.5 BSC  | 10.5 BSC  | 10.5 BSC  |


38

D- c/2 - 1

// bbb|C]

QFN76 Package Dimensions in mm

Table 40: Package Outline Dimensions

| Body Length            | E   | 6.5 BSC   |      |
|------------------------|-----|-----------|------|
| Lead Pitch             | e   | 0.4 BSC   |      |
| EP Size                | J   | 9         | 9.1  |
| EP Size                | K   | 5         | 5.1  |
| Lead Length            | L   | 0.40      | 0.45 |
| Lead Length            | L1  | 0.35      | 0.4  |
| Package Edge Tolerance | aaa | 0.1       |      |
| Mold Flatness          | bbb | 0.1       |      |
| Coplanarity            | ccc | 0.08      |      |
| Lead Offset            | ddd | 0.1       |      |
| Exposed Pad Offset     | eee | 0.1       |      |

Figure 48 shows the package from top view. Decals for some CAD programs are available on the product's website.


|GPIO7/AENC\_WY\_MCD/

\_GPI06/AENC\_VN\_MCD/

TOBGSPI\_MISO

VCCI01

GNDI01

SPI\_nSCS

SPI\_SCK

SPI\_MOSI

SPI\_MISO

UART\_RXD

UART\_TXD

STATUS

VCCI02

GNDI02

TDBGSPI\_TRG

STP

DIR

ENI

TEST

GNDI04


Figure 48: Pinout of TMC4671 (Top View)


## 14 Supplemental Directives

## 14.2 Copyright

## 14.1 Producer Information

TRINAMIC owns the content of this user manual in its entirety, including but not limited to pictures, logos, trademarks, and resources. © Copyright 2022 TRINAMIC. All rights reserved. Electronically published by TRINAMIC, Germany.

## 14.3 Trademark Designations and Symbols

Redistribution of sources or derived formats (for example, Portable Document Format or Hypertext Markup Language) must retain the above copyright notice, and the complete data sheet, user manual, and documentation of this product including associated application notes; and a reference to other available product-related documentation.

Trademark designations and symbols used in this documentation indicate that a product or feature is owned and registered as trademark and/or patent either by TRINAMIC or by other manufacturers, whose products are used or referred to in combination with TRINAMIC's products and TRINAMIC's product documentation.

## 14.4 Target User

This Datasheet is a non-commercial publication that seeks to provide concise scientific and technical user information to the target user. Thus, trademark designations and symbols are only entered in the Short Spec of this document that introduces the product at a quick glance. The trademark designation /symbol is also entered when the product or feature name occurs for the first time in the document. All trademarks and brand names used are property of their respective owners.

The documentation provided here, is for programmers and engineers only, who are equipped with the necessary skills and have been trained to work with this type of product.

## 14.5 Disclaimer: Life Support Systems

The Target User knows how to responsibly make use of this product without causing harm to himself or others, and without causing damage to systems or devices, in which the user incorporates the product.

TRINAMIC Motion Control GmbH &amp; Co. KG does not authorize or warrant any of its products for use in life support systems, without the specific written consent of TRINAMIC Motion Control GmbH &amp; Co. KG.

Information given in this document is believed to be accurate and reliable. However, no responsibility is assumed for the consequences of its use nor for any infringement of patents or other rights of third parties which may result from its use. Specifications are subject to change without notice.

Life support systems are equipment intended to support or sustain life, and whose failure to perform, when properly used in accordance with instructions provided, can be reasonably expected to result in personal injury or death.

## 14.6 Disclaimer: Intended Use

The data specified in this user manual is intended solely for the purpose of product description. No representations or warranties, either express or implied, of merchantability, fitness for a particular purpose


or of any other nature are made hereunder with respect to information/specification or the products to which information refers and no guarantee with respect to compliance to the intended use is given.

TRINAMIC products are not designed nor intended for use in military or aerospace applications or environments or in automotive applications unless specifically designated for such use by TRINAMIC. TRINAMIC conveys no patent, copyright, mask work right or other trade mark right to this product. TRINAMIC assumes no liability for any patent and/or other trade mark rights of a third party resulting from processing or handling of the product and/or any other use of the product.

In particular, this also applies to the stated possible applications or areas of applications of the product. TRINAMIC products are not designed for and must not be used in connection with any applications where the failure of such products would reasonably be expected to result in significant personal injury or death (safety-Critical Applications) without TRINAMIC's specific written consent.

## 14.7 Collateral Documents &amp; Tools

This product documentation is related and/or associated with additional tool kits, firmware and other items, as provided on the product page at: www.trinamic.com.


## 15 Errata of TMC4671-LA/-ES2/-ES

## PID\_POSITION\_ACTUAL glitches when calculated from Hall sensor angle and Hall Interpolation is activated

## 15.1 Errata of TMC4671-LA

Hall interpolation is not intended for positioning applications, especially not with changes of direction. In the following register configuration glitches on PID\_POSITION\_ACTUAL 0x6B can occur:

Register

## Workaround

Value (descr.)

Table 41: Registersettings susceptible to glitches

| 0x51 POSITION_SELECTION   | 5 (PHI_E_HALL selected) 6 (PHI_M_HALL selected) 0 (Use selection in register 0x52)   | Here PID_POSITION_ACTUAL is calculated from PHI_E_HALL or PHI_M_HALL.   |
|---------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| 0x52 PHI_E_SELECTION      | 5 (PHI_E_HALL selected)                                                              | Here PID_POSITION_ACTUAL is calculated from PHI_E_HALL or PHI_M_HALL.   |
| 0x33 HALL_MODE            | bit 8 = 1 (Hall interpolation enabled)                                               | Here PID_POSITION_ACTUAL is calculated from PHI_E_HALL or PHI_M_HALL.   |

In this configuration PID\_POSITION\_ACTUAL might not be able to count full revolutions correctly as the interpolated PHI\_E\_HALL might glitch when motor stops. As a result a full revolution is counted where there was not one completed. If the user does not rely on correct position information in register PID\_ POSITION\_ACTUAL the silicon error does not affect the application.

The hall sensor interpolation needs to be switched off.

## 15.2 Fixes of TMC4671-LA/-ES2 vs. Errata of TMC4671-ES

#

TMC4671-ES Erratum

TMC4671-LA Fix

Description

|   1 | SPI slave MSB read error       | SPI slave correction                               | read via SPI slave now works correct                                                                                                    |
|-----|--------------------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
|   2 | RTMI critical timing           | RTMI enhanced                                      | RTMI works with isolated RTMI-USB IF                                                                                                    |
|   3 | PI advanced controller         | PI scaling updated                                 | scaling selectable available                                                                                                            |
|   4 | ADC group clock cross talk     | ADC clocks corrected                               | crosstalk eliminated                                                                                                                    |
|   5 | PWM_IDLE_L/_H un-used          | PWMoutputs are at high impedance until ENI is high | User can configure PWMsignal polar- ity and afterwards enable PWM sig- nals. Idle state can be set with PD or PU resistor on PWMoutputs |
|   6 | Space VectorPWM                | SVPWM scaling cor- rected                          | SVPWM gives +12% effective voltage. With Space Vector PWMenabled volt- age scaling is modified.                                         |
|   7 | step direction target position | processing corrected                               | step direction as target position                                                                                                       |
|   8 | ABN encoder register access    | access corrected                                   | ABN counter over-writeable                                                                                                              |


Note

9

ENI and ENO

function updated

ENI and ENO act as enable signals

Table 42: TMC4671-ES Errata vs. TMC4671-ES2/-LA Fixes

|   10 | -                             | Hall sync PWMsample                          | optional Hall sampling at PWM cen- ter                                |
|------|-------------------------------|----------------------------------------------|-----------------------------------------------------------------------|
|   11 | -                             | PWM_POLARITIES regis- ter initialized to 0x0 | Active high PWMsignalpolarity is pre- ferred                          |
|   12 | -                             | Registers PHI_M_EXT and POSITION_EXT removed | Registers were not used                                               |
|   13 | Watchdog not properly working | Watchdog removed                             | Watchdog was intended to monitor CLK. Watchdog flag can not be reset. |

## 15.3 Errata of TMC4671-ES Engineering Samples as Reference

1. SPI Slave Interface
2. Realtime Monitoring Interface

The SPI Slave Interface in the TMC4671-ES might show corrupted MSB of read data.

The RTMI of TMC4671-ES could not be used with galvanic isolation due to timing issue.

The P Factor of the TMC4671-ES in the advanced position controller was not properly scaled and the integrator in the advanced PI controller was not reset when P or I parameters are set to zero.

3. PI Controllers
4. Integrated ADCs
5. Pins PWM\_IDLE\_H and PWM\_IDLE\_L without function Pins PWM\_IDLE\_H and PWM\_IDLE\_L of TMC4671-ES were proposed to set gate driver control polarity.

The Delta Sigma ADCs of TMC4671-ES showed signal cross talk caused by ADC clock cross talk.

6. Space Vector PWM does not allow higher voltage utilization
7. Step Direction Counter not used as Target Position The step direction counter of the TMC4671-ES correctly counts but is not available as target position.

The Space vector PWM of the TMC4671-ES does not allow higher voltage utilization.

8. Register write access to ABN encoder count register and N pulse status bits Write access to count registers of TMC4671-ES cleared theses to zero and encoder N pulse input signals were not available within the status register.

ENI (ENable Input) and ENO (ENable Output) of TMC4671-ES did partially work as intended (incomplete reset assignment, missing error sum clear on disable).


9. ENO and ENI

## 15.4 Actions to Avoid Trouble

- update P and I parameter for the advanced PI controller in case of switching numerical representation from Q8.8 to Q4.12 (classical PI controller is un-changed)

What should be taken into account when moving from TMC4671-ES to TMC4671-LA?

- mount pull-up resistors if required for gate driver control signals during power-on reset
- check setting of additional hall\_sync\_pwm\_enable bit for high speed application with usage of Hall signals (power-on default is disable)
- check setting of SVPWM control bit to avoid un-wanted speed-up by SVPWM in torque mode (poweron default is disable without speed-up)

## 15.5 Recommendations

- TMC4671-LA (TMC4671-ES2) is drop-in compatible to the TMC4671-ES. Nevertheless, the TMC4671LA needs to be functional qualified as replacement to avoid un-wanted behavior caused by corrections of errata of TMC4671-ES.

For example: The space vector PWM /SVPWM) control bit does not have an effect for the TMC4671-ES in torque mode. The space vector PWM is corrected for the TMC4671-LA. So, if the SVPWM control bit is un-wanted enabled for the TMC4671-ES, the TMC4671-LA would run approximately +12% faster in torque mode with the same settings.


## 16 Figures Index

|       |                                                                                                                     |       |       | with                                                                                                                                 |                |
|-------|---------------------------------------------------------------------------------------------------------------------|-------|-------|--------------------------------------------------------------------------------------------------------------------------------------|----------------|
| 2 3   | PID Architectures and Motion Modes                                                                                  | 10    |       | to electromagnetic interference cleaned                                                                                              |                |
| 4     | Orientations UVW(FOC3) and XY (FOC2)                                                                                | 15    |       | PWM switching and noise                                                                                                              |                |
|       | Compass Motor Model w/ 3 Phases UVW (FOC3) and Compass Motor Model w/ 2 Phases (FOC2) . . . . . . . .               | 15    |       | Hall signals (right) by PWM center synced sampling of Hall signal vector (H1 H2 H3) . . . . . . . . . . . . . . . on                 | 47             |
| 5     | Hardware FOC Application Diagram Hardware FOC Block Diagram . . . .                                                 | 16    | 25    | Hall Signal PWM Center Sampling PWM_CENTER . . . . . . . . . . . .                                                                   | 47             |
| 6     | . SPI Datagram Structure . . . . . .                                                                                | 16    | 26    | . Signal                                                                                                                             |                |
| 7 8   | . . . . . . . . .                                                                                                   | 17    |       | Hall Blanking                                                                                                                        | 48             |
|       | SPI Timing                                                                                                          | 18    | 27    | . . . . . . . . . . Analog Encoder (AENC) signal wave-                                                                               | 48             |
| 9     | . . . . . . . . . SPI Timing of Write Access without pause with fSCK up to 8MHz . . . .                             | 19    |       | forms . . . . . . . . . . . . . . . . . . Analog Encoder (AENC) Selector                                                             |                |
| 10    | . SPI Timing of Read Access with pause (tPAUSE) of 500 ns with fSCK up to                                           |       | 28    | & Scaler w/ Offset Correction . . . . . Classic PI Controller Structure . . . .                                                      | 49 54          |
|       | 8MHz. .                                                                                                             | 19    | 29    |                                                                                                                                      |                |
|       | . . . . . . . . . . . . . . . . . .                                                                                 |       | 30    | Advanced PI Controller Structure . .                                                                                                 | 55             |
| 11    | Connector for Real-Time Monitoring                                                                                  |       | 31    | PI Controllers for position, velocity and current . . . . . . . . . . . . . . . . . . .                                              | 57             |
|       | Interface (Connector Type: Hirose DF20F-10DP-1V) . . . . . . . . . . . . .                                          | 20    | 32    | . Inner FOC Control Loop .                                                                                                           | 58             |
| 12    |                                                                                                                     | 22    | 33 34 | FOC Transformations . . . . . . . . . Motion Modes . . . . . . . . .                                                                 | 59             |
|       | UART Read Datagram (TMC4671 reg- ister read via UART) . . . . . . . . . . .                                         |       | 35    | .                                                                                                                                    | 59 62          |
| 13    | UART Write Datagram (TMC4671 reg- ister write via UART) . . . . . . . . . .                                         |       |       | . . . Biquad Filters in Control Structure                                                                                            | 63             |
|       |                                                                                                                     | 22    | 36    | . PWMGate Driver Control Polarities                                                                                                  |                |
| 14    | N_POLE_PAIRS - Number of Pole Pairs (Number of Poles) . . . . . . . . . . . .                                       | 26    | 37    | FOC3 (three phase motor), FOC2 (two phase stepper motor), FOC1 (single phase DC motor) . . . . . . . . . . . . . . . . . . . . . . . | 64             |
| 15    | Integer Representation of Angles as 16 bit signed (s16) resp. 16 bit un- signed (u16) . . . . . . . . . . . . . . . | 27    | 38 39 | BBM Timing . . TMC4671 Pinout                                                                                                        | 65             |
| 16    | Input Voltage Ranges of internaql Delta Sigma ADC Channels . . . . . .                                              |       |       | with 3 phase Power stage and BLDC Motor . . . . . . . . TMC4671 Pinout with Stepper Motor                                            | 128 128        |
| 17    | Delta Sigma ADC Configurations                                                                                      | 31    | 40 41 |                                                                                                                                      |                |
|       | dsADC_CONFIG (ANALOG (internal), MCLKO, MCLKI, MDAC) . . . . . . . . .                                              |       |       | TMC4671 Pinout with DC Motor or Voice Coil . . . . . . . . . . . . . . . .                                                           | 129            |
| 18    | ∆Σ ADC Configurations - MDAC (Comparator-R-C-R as ∆Σ -Modulator)                                                    | 33    | 42    | SampleCircuit for InterfacingofanEn- coder Signal . . . . . . . . . . . . . . a sin-                                                 | 136            |
| 19    | ADC Selector and Scaler with Offset Correction . . . . . . . . . . . . . . . .                                      | 37 41 | 43    | Sample Circuit for Interfacing of gle ended analog signal . . . . .                                                                  | 137            |
| 20    | NumberofPolePairsnppvs. mechan-                                                                                     |       | 44    | . . Phase current measurement: Current directions for 2 and 3 phase motors                                                           | 138            |
|       | ical angle phi_m and electrical angle phi_e . . . . . . . . . . . . . . . . . . . .                                 | 43 44 | 45    | Phase current measurement: Current direction for DC or Voice Coil Motor                                                              | 138            |
| 21    | ABN Incremental Encoder N Pulse . Timing . . . . . . . . .                                                          |       | 46    | Current Shunt Amplifier Sample . . . . . .                                                                                           | Circuit139 141 |
| 22 23 | Encoder ABN . Hall Sensor Angles . . . . . . . . . . .                                                              | 45 46 | 47 48 | QFN76 Package Outline . Pinout of TMC4671 (Top View) . . .                                                                           | 143            |

Outline of noisy Hall signals (left) due


1

FOC Basic Principle

.

.

.

.

.

.

.

.

.

.

.

9

24

## 17 Tables Index

| 2     | .                                                                                                                               | 18    |       | classical PID controllers for currents, velocity, and position . . . . . . . . . . . . . . .                                                                           |             |
|-------|---------------------------------------------------------------------------------------------------------------------------------|-------|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| 3     | SPI Timing Parameter                                                                                                            |       |       | .                                                                                                                                                                      | 53 53       |
|       | . . . . . . . . Possible baudrates and correspond- ing values for register 0x79 . . . . . . Single Pin Interface Motion Modes . | 21    | 21 22 | Motion Modes . .                                                                                                                                                       | 55          |
| 4     | .                                                                                                                               | 23    | 23    | . . . . . . PI normalization overview . . . . . . . . . . . . . . . . . . .                                                                                            | 60          |
| 5     | GPIO Configuration Overview with 'x' as don't care . . . . . . . . . . . . . . . .                                              | 24    | 24    | Motion Modes . . TABSTatusFlags .                                                                                                                                      | 63          |
| 6 7   | Numerical Representations . . . . . Examples of u16, s16, q8.8, q4.12 . Examples of u16, s16, q8.8 . . . .                      | 24 25 | 25    | . . . . . . . . . . . . FOC321 Gate Control Signal Configu- rations . . . . . . . . . . . . . . . . . .                                                                | 64          |
| 8     | . .                                                                                                                             | 27    | 26    | Factors for integer to real conversion                                                                                                                                 | 66          |
| 9     | . Delta Sigma ∆Σ ADC Input Stage Con- figurations . . . . . . . . . . . . . . . .                                               | 30    | 27 28 | Factors for real to integer conversion . . . . . . .                                                                                                                   | 67          |
| 10    | Delta Sigma ∆Σ ADC Input Stage Con-                                                                                             | 31 33 | 29 32 | TABSTatusFlags . . . . . . TMC4671 Registers . . . . . . . . . . . . . . .                                                                                             | 68 76       |
|       | figurations . . . . . . . . . . . . . . . . ADC Configurations . . . . . . . . Registers for Delta Sigma Configuration          |       |       | Pin Type Definition . . . . . . . Functional Pin                                                                                                                       | 129 132     |
| 11    | ∆Σ                                                                                                                              | 34    | 33    | Description . .                                                                                                                                                        |             |
| 12 13 | Delta Sigma MCLK Configurations . .                                                                                             | 34    | 34    | . . . . . Supply Voltage Pins and Ground Pins . . . .                                                                                                                  | 133         |
| 14    | Recommended Decimation Parame-                                                                                                  |       | 35 36 | Absolute Maximum Ratings . . Operational Range . . . . . . . . . . . . . . . . . .                                                                                     | 134 134     |
|       | ter MDEC . . . . . . . . . . . . . . . . . Recommended input voltage range                                                      | 35    | 37    | .                                                                                                                                                                      | 135         |
| 15    | from V_MIN25%[V] to V_MAX75%[V]                                                                                                 |       | 38    | DC Characteristics                                                                                                                                                     |             |
|       | for internal Delta Sigma Modulators; V_SUPPLY[V] = 5V is recommended for the analog part of the TMC4671. .                      |       | 39    | . . . Additional decoupling capacitors for supply voltages . . . . . . . . . . . . . Reference Values for circuitry compo- nents . . . . . . . . . . . . . . . . . . . | 136         |
| 16    | Delta Sigma input voltage mapping of internal Delta Sigma Modulators . . .                                                      | 36    | 40 41 | Package Outline Dimensions . . . . . Registersettings susceptible to glitches                                                                                          | 137 142 146 |
| 17    | Delta Sigma R-C-R-CMP Configurations                                                                                            | 36 37 | 42    | TMC4671-ES Errata vs. TMC4671- . .                                                                                                                                     | 147         |
|       | Delta Sigma input voltage mapping of                                                                                            | 38    | 43    | ES2/-LS Fixes . . . . . . . . . . . . . IC Revision . . . . . . . . . . . . . . . . . . . . . . .                                                                      | 151         |
| 18 19 | external comparator (CMP) . . . . . . Example Parameters for ADC_GAIN .                                                         | 39    | 44    | Document Revision . . . .                                                                                                                                              | 153         |

Scalings and Change Rate Timings of


1

Order codes

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

6

20

## 18 Revision History

## 18.1 IC Revision

Version

Date

Author

## 18.2 Document Revision

Version

Date

Author

| V0.9   | 2017-SEP-29   | LL,OM   | Pre-liminary TMC4671-ES datasheet.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|--------|---------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| V0.91  | 2018-JAN-30   | OM      | Changed some typos and added some notes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| V0.92  | 2018-FEB-28   | OM      | Changed register descriptions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| V0.93  | 2018-MAR-07   | OM      | Changed some typos and bugs in graphics.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| V0.94  | 2018-MAR-14   | OM      | Added Errata Section.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| V0.95  | 2018-MAY-08   | OM      | Preparations for launch.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| V1.00  | 2018-JUN-28   | LL      | Errata Section updated concerning Step/Dir.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| V1.01  | 2018-JUL-19   | OM      | Added Description for Status Flags                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| V1.02  | 2018-JUL-31   | OM      | Added Description for Feed Forward Control Structure                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| V1.03  | 2018-SEP-06   | OM      | Description of single pin interface and motion modes added                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| V1.04  | 2018-DEC-11   | OM      | Register map and pictures of PI controllers corrected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| V1.05  | 2019-JAN-02   | OM      | Figure 9 corrected, order codes for eval kits added.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| V1.06  | 2019-FEB-06   | OM      | Reference switch processing explained.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| V1.07  | 2019-MAR-22   | LL      | errata updated concerning encoder N pulse, ENI and ENO; figure il- lustrating PPR, NPP, phi_m, phi_e added; PWM polarities and Hall signal blanking expained in more detail together with drawings.                                                                                                                                                                                                                                                                                                                                                                                                                   |
| V1.99  | 2019-SEP-12   | LL      | register map structure with enhanced readability, minimal move PI controller section of TMC4671-ES removed for TMC4671-LA; SPI timing with tPAUSE added; figure of Hall signal PWM synced sam- pling option added; section ADC Gain Factors added; section ADC engine updated; sense amplifier type corrected to AD8418; LM319 removed as dsMOD example; ADC engine section updated; PWM Engine FOC321 with associated motor connectors added; PID T_N (Nachstellzeit = Reset Time) dsADC input stage configuration, ADC real world scaling (IgainADC [ A/LSB ] , UgainADC [ V/LSB ] ) added, errata section updated; |


| V1.0   | 2017-JUL-03   | LL,OM   | Engineering samples TMC4671-ES (1v0 2017-07-03-19:43)   |
|--------|---------------|---------|---------------------------------------------------------|
| V1.3   | 2019-APR-30   | LL,OM   | Release version TMC4671-LA (1v3 2019-04-30-12:55)       |

Description

Table 43: IC Revision

Description

Version

Date

Author

Description

| V1.99   | 2019-DEC-06   | LL   | functional summary updated for TMC4671-LA, FOC basics updated, functional description updated, SPIreadwriteaccesstimingupdated for TMC4671-LA, ADC Engine section updated w/ voltage scalings, step direction interface correction updated, order codes updated, section 'Calculative PI Controller Setup - Classic Structure' added; TMC4671-ES Erratum vs. TMC4671-LA fixes added, PWMcenter Hall vector sampling added; section watchdog updated; section fixes vs. errata updated concerning actions to avoid trouble with recommen- dations; section How to Turn a Motor updated; entry (signal of max. of q4.12) in table (6) corrected,   |
|---------|---------------|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| V1.99   | 2019-DEC-20   | LL   | watchdog section updated, order codes updated, 1st page block di- agram updated, DS_ANALOG_INPUT_STAGE_CFG updated                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| V1.99   | 2020-FEB-10   | LL   | Encoder Engine section: mechanical position (phi_m) corrected, sec- tion Safety Functions: hint according to status bit write added,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| V2.00   | 2020-APR-16   | OM   | feedforward control and PI control section updated; ENO/ENI pin functionality added; Register map updated                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| V2.01   | 2020-JUL-13   | KK   | Register map updated (added missing registers, removed unused registers), added section for controller sampling rates, added ta- ble for real2int and int2real conversions, added section for GPIO- usage, updated controller q8.8 and q4.12 representation, fixed num_representation for angles                                                                                                                                                                                                                                                                                                                                                 |
| V2.02   | 2020-SEP-22   | OM   | Register map updated (removed feed forward control registers), added descriptions for register usage and register function, fixed exponents in tables for real/integer pwm conversion, updated feed- foward, updated AENC_DECODER_MODE register info and infobox in Analog Hall and Analog Encoder Interface                                                                                                                                                                                                                                                                                                                                     |
| V2.03   | 2020-OCT-08   | KK   | Fixed several typos, added missing information about UART bau- drate in 4.2.3, fixed default values for UART_BPS register and added hint in registermap about baudrate settings.                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| V2.04   | 2021-JAN-06   | KK   | Removed obsolete register AENC_DECODER_N_MASK from register 0x3C in 7.2 and 7.3, added errata on hall interpolation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| V2.05   | 2021-JAN-06   | KK   | updated errata section                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| V2.06   | 2021-APR-12   | KK   | corrected names of "Phase Current Measurement" on graphics 39, 40 and 41 so they match the pin table, removed registers PIDIN_ VELOCITY_TARGET and PID_IN_POSITION_TARGET from registermap as they are not connected, updated order codes, removed note on ES2                                                                                                                                                                                                                                                                                                                                                                                   |


Version

Date

Author

Description

| V2.07   | 2022-JAN-07   | KK   | Table 2: removed double SCK low time, changed MISO data valid time after falling edge of SCK to 20ns Typ; removed mentioning of negative voltages in section 4.4.15, fixed description error in reg- ister 0x69 from target position to flux torque actual, removed un- used mode_ramp and mode_ff from register 0x63, removed an un- finished sentence from 10.2.1, corrected formula for register 0x05 and 0x06 in section 7.2; replaced TMC_INPUTS_RAW by TMC4671_ INPUTS_RAW; Added info on UART-write response; added a table on PI-representations for the advanced control structure; Removed un- used comment section in section 7.3   |
|---------|---------------|------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| V2.08   | 2022-JUL-26   | KK   | corrected register description 0x1B N_POLE_PAIRS; Add limits with respective registeraddress to 4.7.5; remove unused PID_ ACCELERATION_LIMIT register from 7.3; removed blanking_a and blanking_b from register 0x04 dsADC_MCFG_B_MCFG_A as it is not used;                                                                                                                                                                                                                                                                                                                                                                                    |

Table 44: Document Revision

