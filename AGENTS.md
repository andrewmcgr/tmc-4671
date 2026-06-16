# PROJECT KNOWLEDGE BASE

## OVERVIEW
- **Project**: Kalico 3D Printer Firmware Plugin.
- **Purpose**: Implements a driver for the Trinamic TMC 4671 closed-loop field-oriented-control (FOC) motor driver chip.
- **Reference Datasheet**: TMC 4671 Datasheet Version **2.08**. All register mapping, bitfields, and chip behaviors MUST align with this specific datasheet revision.

## STRUCTURE
```text
tmc-4671/
├── __init__.py         # Plugin entry point for Kalico
├── tmc4671_regs.py     # SPI registers
├── tmc4671_biquad.py   # Biquad filter design utilities (BiquadFilter, design functions, TMC normalisation)
├── tmc4671.py          # Core driver implementation (PID tuning, calibration, SPI, G-code commands)
├── pyproject.toml      # Project configuration defining the "kalico.plugins" entry-point
└── README.md           # Hardware setup, wiring, moonraker configuration, and PID tuning instructions
```

## WHERE TO LOOK
- **Chip Datasheet**: [TMC 4671 LA Datasheet version 2.08](datasheet/TMC4671-LA_datasheet_rev2.08.noimages.md).
- **Register Map**: Located in [tmc4671_regs.py](tmc4671_regs.py). This file defines register addresses, sub-registers.
- **Biquad filter design**: Located in [tmc4671_biquad.py](tmc4671_biquad.py). Contains `BiquadFilter`, filter type/target constants, and all `biquad_*` design/normalisation functions.
- **Everything else**: Implemented in [tmc4671.py](tmc4671.py).

## CONVENTIONS & CRITICAL INSTRUCTIONS
- **Datasheet Revision**: The correct version of the TMC 4671 datasheet to use is **version 2.08**. Do not use older or newer versions unless explicitly instructed, as register addresses or features can vary.
- **Firmware Context**: This repository is a plugin for the **Kalico** 3d printer firmware (and is structured to integrate with Kalico/Klipper).
- **Refactoring**: When extracting code into new files, ensure this file is updated.
- **Installer**: `install.sh` symlinks each Python module file into Klipper's `extras/` directory. When adding a new module file, add a corresponding `ln -srfn` line to `link_extension` in `install.sh` and run the script (or create the symlink manually) on the target machine, otherwise Klipper will fail to import the module.
- **Commit style**: Plain English, no conventional-commit prefixes (e.g. "Add motor inductance measurement", not "feat: add motor inductance measurement").
- **G-code commands**: When adding or changing a G-code command, update the "G-code command reference" section at the end of `README.md` to reflect the new or changed command, its parameters, and their defaults.
