# PROJECT KNOWLEDGE BASE

## OVERVIEW
- **Project**: Kalico 3D Printer Firmware Plugin.
- **Purpose**: Implements a driver for the Trinamic TMC 4671 closed-loop field-oriented-control (FOC) motor driver chip.
- **Reference Datasheet**: TMC 4671 Datasheet Version **2.08**. All register mapping, bitfields, and chip behaviors MUST align with this specific datasheet revision.

## STRUCTURE
```text
tmc-4671/
├── __init__.py      # Plugin entry point for Kalico
├── tmc4671.py       # Core driver implementation (SPI registers, PID tuning, calibration, biquad filters)
├── pyproject.toml   # Project configuration defining the "kalico.plugins" entry-point
└── README.md        # Hardware setup, wiring, moonraker configuration, and PID tuning instructions
```

## WHERE TO LOOK
- **Register Map & SPI Communication**: Located in [tmc4671.py](file:///home/amcgregor/tmc-4671/tmc4671.py). This file defines register addresses, sub-registers, and helper classes (e.g. `MotionMode`, `BiquadFilter`).
- **Autotuning & Homing**: Also implemented in [tmc4671.py](file:///home/amcgregor/tmc-4671/tmc4671.py).

## CONVENTIONS & CRITICAL INSTRUCTIONS
- **Datasheet Revision**: The correct version of the TMC 4671 datasheet to use is **version 2.08**. Do not use older or newer versions unless explicitly instructed, as register addresses or features can vary.
- **Firmware Context**: This repository is a plugin for the **Kalico** 3d printer firmware (and is structured to integrate with Kalico/Klipper).
