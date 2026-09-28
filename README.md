# u-blox-sho-OpenCPU
Repository with reference code for u-blox Open CPU modules.

## Quick Start Guide
Choose your product or SDK:

- **[NORA-W50/W51 (TI CC35x1E + FreeRTOS)](#nora-w5051---getting-started-sdk)** — Wi-Fi 6 + Bluetooth LE with automated build tools
- **[nRF5 SDK](#nrf5-sdk)** — Bluetooth & Wi-Fi for ANNA, NINA, NORA-B, BMD series
- **[Zephyr RTOS](#zephyr-rtos)** — BMD, MINI-NORA, EVK boards
- **[MCUxpresso](#mcuxpresso)** — IRIS EVK examples
- **[RF Tools](#nina-w10-otp-and-rf-calibration)** — NINA-W10 OTP & RF calibration
- **[Output Power References](#output-power-calibration)** — Compliance data for NORA-W1/W30/W40

## NORA-W50/W51 - Getting Started SDK
Complete cross-platform build driver and comprehensive getting-started guide for NORA-W50/W51 Open CPU modules (based on TI CC35x1E SoC with Wi-Fi 6 and Bluetooth LE 5.4).

**What's included:**
- **ti_w5_build.py**: Automated build orchestration (clone → configure → build SDK → build examples) for Windows, WSL2, and Linux
- **README.md**: Full getting-started guide with prerequisites, build instructions, and example reference
- Verified working with TI SimpleLink Wi-Fi SDK 10.20.00.39 and toolchains: SysConfig 1.28.0, TI Arm Clang, Arm GNU Toolchain, CMake, and GNU Make

📖 **See [NORA-W50-W51-GettingStartedSDK/README.md](NORA-W50-W51-GettingStartedSDK/README.md) for complete setup instructions.**

## nRF5 SDK
Bluetooth and Wi-Fi enabled modules with Nordic nRF5 SDK support.

**Supported modules:** ANNA-B4, NINA-W1, NORA-B2, BMD-300/330/340/360/380, EVK-based boards

**Getting Help:**
- Refer to the **System Integration Manual** for your product (datasheet)
- See **EVK User Guide** for specific board pinouts and features
- More info: https://www.u-blox.com/

## Zephyr RTOS

### Mainline Zephyr
The following boards have been merged into the Zephyr project mainline repository:
https://github.com/zephyrproject-rtos/zephyr

**Mainline Boards:**

| EVK board    | Mainline Support |
|--------------|------------------|
| BMD-300-EVAL | u-blox/ubx_bmd300eval |
| BMD-301-EVAL | u-blox/ubx_bmd300eval |
| BMD-330-EVAL | u-blox/ubx_bmd330eval |
| BMD-340-EVAL | u-blox/ubx_bmd340eval |
| BMD-341-EVAL | u-blox/ubx_bmd340eval |
| BMD-345-EVAL | u-blox/ubx_bmd345eval |
| BMD-350-EVAL | u-blox/ubx_bmd350eval |
| BMD-360-EVAL | u-blox/ubx_bmd360eval |
| BMD-380-EVAL | u-blox/ubx_bmd380eval |
| EVK-ANNA-B1  | u-blox/ubx_evkannab1 |
| EVK-IRIS-W1  | u-blox/ubx_evk_iris_w1 |
| EVK-NINA-B1  | u-blox/ubx_evkninab1 |
| EVK-NINA-B3  | u-blox/ubx_evkninab3 |
| EVK-NINA-B4  | u-blox/ubx_evkninab4 |
| EVK-NINA-B5  | u-blox/ubx_evkninab5 |
| EVK-NORA-B2  | u-blox/ubx_evknorab2 |

### u-blox Repository Boards
Board support packages available here (not in mainline Zephyr):

| EVK board                    | Folder                        | Status |
|------------------------------|-------------------------------|--------|
| EVK-ANNA-B4                  | arm/ubx_evkannab4_nrf52833    | Active (NCS v2.5.0) |
| MINI-NORA-B10 Rev C+         | arm/ubx_mininorab10_nrf5340   | Active (NCS v2.6.0) |
| MINI-NORA-B12 Rev C+         | arm/ubx_mininorab12_nrf5340   | Active (NCS v2.6.0) |
| XPLR-IOT-1                   | arm/ubx_xplriot1_nrf5340      | Active (NCS v1.9.1) |
| EVK-NORA-B10                 | u-blox/ubx_evknorab10         | Active (NCS v3.2.1) |
| EVK-NORA-B12                 | u-blox/ubx_evknorab12         | Active (NCS v3.2.1) |
| R41Z-EVAL                    | ubx_r41zeval_kw41z            | Archive (Zephyr v2.6-rc1) |

### Archived Board Support
The following board support packages have been moved to archive (older Zephyr versions):

| EVK board                      | Folder                             | Version |
|--------------------------------|------------------------------------|---------| 
| EVK-NORA-B10                   | ubx_evknorab10_nrf5340_ncs220      | NCS v2.2.x / Zephyr 3.2.99 |
| EVK-NORA-B12                   | ubx_evknorab12_nrf5340_ncs220      | NCS v2.2.x / Zephyr 3.2.99 |
| EVK-NORA-B10                   | arm/ubx_evknorab10_nrf5340_ncs250  | NCS v2.5.0 |
| EVK-NORA-B12                   | arm/ubx_evknorab12_nrf5340_ncs250  | NCS v2.5.0 |
| MINI-NORA-B10 Rev B or earlier | ubx_mininorab10_nrf5340revb_ncs161 | NCS v1.6.1 / Zephyr 2.6-rc1 |

**Installation:**
Store the board configuration directory in:
```
<install directory>/zephyr/boards/arm
  or
<install directory>/zephyr/boards/u-blox  (for HW model v2)
```

Then build your code for that board. Each folder contains documentation.

> **_NOTE:_** NCS = Nordic Semiconductor [nRF Connect SDK](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/index.html), based on Zephyr RTOS. NCS lags mainline Zephyr by ~3 months.

**Planned Submissions:** EVK-ANNA-B4, EVK-NORA-B10, EVK-NORA-B12 (pending mainline review)

## MCUxpresso
Examples and start-up software for IRIS EVK and USB IRIS EVK using MCUxpresso IDE.

- Folder: `MCUXpresso/`
- IDE-based development with graphical configuration tools

## NINA-W10 OTP and RF Calibration
Tools and examples for NINA-W10 series modules:
- Read OTP (One-Time Programmable) memory
- Apply RF calibration
- Limit TX power for regulatory compliance

- Folder: `NINA-W1-OTP/`

## Output Power Calibration
Reference firmware and calibration data for RF output power compliance:

| Module | Folder | Purpose |
|--------|--------|---------|
| NORA-W1 | `NORA-W1-OutputPower/` | Output power calibration reference |
| NORA-W30 | `NORA-W30-OutputPower/` | Channel plan & compliance (ACMA, etc.) |
| NORA-W40 | `NORA-W40-OutputPower/` | Latest tested firmware & calibration |

## Additional Resources
- **u-blox Website:** https://www.u-blox.com/
- **Product Datasheets:** Available on u-blox product pages
- **EVK User Guides:** Board-specific documentation and pinouts
- **Integration Manuals:** System integration for each product

# Disclaimer
Copyright © u-blox

u-blox reserves all rights in this deliverable (documentation, software, etc.,
hereafter "Deliverable").

u-blox grants you the right to use, copy, modify and distribute the
Deliverable provided hereunder for any purpose without fee.

THIS DELIVERABLE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
WARRANTY. IN PARTICULAR, NEITHER THE AUTHOR NOR U-BLOX MAKES ANY
REPRESENTATION OR WARRANTY OF ANY KIND CONCERNING THE MERCHANTABILITY OF THIS
DELIVERABLE OR ITS FITNESS FOR ANY PARTICULAR PURPOSE.

In case you provide us a feedback or make a contribution in the form of a
further development of the Deliverable ("Contribution"), u-blox will have the
same rights as granted to you, namely to use, copy, modify and distribute the
Contribution provided to us for any purpose without fee.
