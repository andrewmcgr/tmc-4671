# tmc-4671
TMC 4671 driver for Klipper

The TMC 4671 is a closed-loop field-oriented-control servo driver for brushed and brushless DC motors and stepper motors.

This driver allows use of TMC 4671 driver boards with Klipper, in closed-loop mode.

Supported hardware:
* Driver boards:
  * TMC4671+TMC6100-BOB
    * This board can only drive brushless and brushed motors, not stepper motors.
    * 10 A 50 V limits
  * OpenFFBoard TMC 4671 driver kit
    * This board can drive all kinds of motors, including steppers.
    * 20 A 60 V limits
    * On-board thermistor for output MOSFET temnperature monitoring
* Encoders
  * ABZ and AB encoders, voltages as supported by the driver board (most common types work)
    * 6-wire AB encoders with differential outputs work if wired correctly to the driver board. Integrated encoders in LDO motors are of this type, and are tested.
  * Digital Hall encoders
  * Analogue Hall encoders (note: untested, support may be incomplete)
* Motors
  * 3-phase Brushless DC motors
  * 2-phase stepper motors (if supported by the driver board)
  * DC motors (note: untested, but should work)

Klipper driver features:
* PID autotuning for the current and torque control loops
* PID configuration for the velocity and position loops (manual tuning required, for now)
* ADC autocalibration
* Encoder autoinitialisation for relative encoders, or absolute encoders not indexed to the electrical phase of the motor
* Sensorless homing (not currently working) by setting a low homing current and detecting failure to track the commanded position within the driver
* On-driver limit switch pin support
* Optional TMC6100 output driver initialisation support (requred for the eval board, not used for OpenFFBoard)
* Virtual steps-per-revolution and microsteps. Klipper treats the TMC 4671 as if it were a conventional stepper driver, all servo activity takes place in hardware. Thus the steps and microsteps in the configuration have no particular relation to the motor, and instead are translated to position angle targets within the TMC 4671.

## How to use this driver:

First, note that the driver is under active development, and thus will change rapidly.

Wiring:
* Connect the driver board to an SPI bus (SCK, MOSI, MISO), an SPI chip select line, and the STEP/DIR/ENABLE signals of a stepper port (or equivalent GPIOs). If intending to use sensorless homing, add an input GPIO for the status pin. The SPI bus *MUST* support hardware mode. Note that none of these signals on the 4671 are 5V tolerant, so they *MUST* be 3.3V IO.
* Connect the motor's phase lines to the requisite number of phases. For 3 phase motors, make certain that you use two phases with current sensing. For 2 phase (i.e. stepper) motors, make sure that there is a current sense channel for each phase of the motor.
* Connect the encoder you are using. Note that digital Hall sensors, while they sort of work, will not give good results with Klipper.
* Configure the driver's variables appropriately. This will basically require reading the datasheet for the 4671 and the schematic for your driver board very carefully. The work to make this more user-friendly has not yet been done.
* `current_scale_ma_lsb` is 1.155 for the OpenFFBoard with ACS724T-30AB current sensors, and 1.272 for the EVAL-BOB
* `run_current` should be total peak current, which means 2.8 times the rated current for a stepper motor, maximum. For BLDC, calculate this from the peak power dissipation, if no rated current is given, then multiply by 3.4. Yes, this gives some very large-seeming current values, but the 4671 will not use them except very briefly.
* Configure the matching stepper section with appropriate full_steps_per_rotation and microsteps. Both must be powers of two, and their product must be less than 65536. 256 steps and 8 microsteps works well in most cases.
* Note that there is currently a bug where the automatic enabling of drivers when homing will crash Klipper, so you must `set_stepper_enable stepper=stepper_x`, or `manual_stepper stepper=foo enable=1` to manually enable them before homing.

The following is a working example for driving an LDO 2504-E1000 with OpenFFBoard drivers. Sensorless homing is commented out because it currently does not work, but is shown as an example:
```ini
[stepper_x]
step_pin: tmc:gpio16
dir_pin: !tmc:gpio17
enable_pin: tmc:gpio18
rotation_distance: 40
microsteps: 8
full_steps_per_rotation: 256 # STEP/DIR interface resolution 
#endstop_pin: tmc4671_stepper_y:virtual_endstop
endstop_pin: ^toolhead:gpio22
homing_speed: 40

[tmc4671 stepper_x]
cs_pin: tmc:gpio25
#drv_cs_pin: tmc:gpio26
spi_bus: spi1d
#spi_software_sclk_pin: gpio14
#spi_software_mosi_pin: gpio15
#spi_software_miso_pin: gpio8
spi_speed: 2000000
#diag_pin: tmc:gpio5
run_current: 6.5
current_scale_ma_lsb: 1.155
adc_temp_reg: AGPI_B
foc_MOTOR_TYPE: 2
foc_N_POLE_PAIRS: 50
foc_PWM_SV: 0
foc_ADC_I_UX_SELECT: 0
foc_ADC_I_V_SELECT: 2
foc_ADC_I_WY_SELECT: 1
foc_ABN_DECODER_PPR: 4000
foc_ABN_DIRECTION: 1
```
