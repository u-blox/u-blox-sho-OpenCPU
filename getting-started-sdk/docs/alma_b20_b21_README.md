# ALMA-B20-B21 Getting Started Guide

> **Status:** ALMA-B20-B21 is under development at u-blox. There is no
> `ubx_evkalmab2` board definition in Zephyr or the nRF Connect SDK yet, so
> this target builds against Nordic's nRF54LM20 DK board. Treat it as a
> bring-up path, not a production configuration.

## Overview

ALMA-B20-B21 modules are based on the **Nordic nRF54LM20** SoC and are built with the
**nRF Connect SDK** (NCS), exactly like NORA-B20-B21-B22. The nRF54LM20B variant adds the
Nordic **Axon NPU**, an edge-AI accelerator that is substantially more energy
efficient than running the same inference on the MCU.

**Key features:**
- Arm Cortex-M33 @ 128 MHz plus a 128 MHz RISC-V coprocessor
- Axon NPU for edge AI (nRF54LM20B variants)
- 2 MB NVM, 512 KB RAM
- Bluetooth Core 6.0 with Channel Sounding
- IEEE 802.15.4 for Thread, Matter and Zigbee
- +8 dBm conducted / +10 dBm EIRP; RX sensitivity -95.5 dBm @ 1 Mbit/s,
  -101 dBm @ 250 kbit/s (802.15.4)
- Throughput 1.4 Mbit/s, range up to 1400 m
- 66 GPIO, 7x serial, USB HS, HS-SPI + 6x SPI, 6x I2C, sQSPI, NFC, PDM,
  3x PWM, 2x QDEC, 7x timers, SAADC, GRTC

**SDK:** nRF Connect SDK v3.4.1
**Platforms:** Windows, WSL2, Linux, macOS
**Build system:** west + CMake + Ninja

---

## Module variants

| Part | SoC | Antenna | Size (mm) |
|------|-----|---------|-----------|
| ALMA-B201 | nRF54LM20A | Antenna pin | 10.4 x 11.2 x 1.9 |
| ALMA-B206 | nRF54LM20A | Internal PCB | 10.4 x 14.3 x 1.9 |
| ALMA-B211 | nRF54LM20B (NPU) | Antenna pin | 10.4 x 11.2 x 1.9 |
| ALMA-B216 | nRF54LM20B (NPU) | Internal PCB | 10.4 x 14.3 x 1.9 |

---

## Board targets

No u-blox board definition exists yet. Builds use Nordic's DK board, which
carries the same SoC:

| Board target | Matches |
|--------------|---------|
| `nrf54lm20dk/nrf54lm20a/cpuapp` | ALMA-B201 / B206 (default) |
| `nrf54lm20dk/nrf54lm20a/cpuapp/ns` | ALMA-B20x, TF-M non-secure |
| `nrf54lm20dk/nrf54lm20b/cpuapp` | ALMA-B211 / B216 |
| `nrf54lm20dk/nrf54lm20b/cpuapp/ns` | ALMA-B21x, TF-M non-secure |
| `nrf54lm20dk/nrf54lm20a/cpuflpr` | RISC-V coprocessor |

Nordic's DK (PCA10184) physically carries an nRF54LM20B; the `nrf54lm20a`
target is an emulation configuration on the same hardware.

Select the B-variant with:

```bash
./ubx-sdk.sh alma-b20-b21 --build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp
```

Because the board is a DK rather than the module, pin assignments, the antenna
path and power rails will not match a real ALMA-B20-B21 design. Expect to supply a
devicetree overlay for anything beyond CPU-level bring-up.

---

## Prerequisites

Identical to NORA-B20-B21-B22 - see [nora_b20_b21_b22_README.md](nora_b20_b21_b22_README.md#prerequisites).
The quickest route is nRF Connect for Desktop and its Toolchain Manager.

```bash
./ubx-sdk.sh alma-b20-b21 --doctor
```

---

## Quick start

```bash
./ubx-sdk.sh alma-b20-b21 --clone
./ubx-sdk.sh alma-b20-b21 --install
./ubx-sdk.sh alma-b20-b21 --list
./ubx-sdk.sh alma-b20-b21 --build hello_world --flash --log
```

NORA-B20-B21-B22 and ALMA-B20-B21 share one NCS workspace: `--clone` puts it in
`C:\ncs\v3.4.1` (Windows) or `~/ncs/v3.4.1` (Linux) after checking for about
15 GB free, and both targets detect it. Select a different workspace with
`python scripts/nordic_ncs_build.py alma-b20-b21 use <path>`; see
[nora_b20_b21_b22_README.md](nora_b20_b21_b22_README.md#where-the-sdk-lives).

---

## Matter

Matter support ships inside the nRF Connect SDK, so there is no separate Matter
SDK to fetch — `--clone` pulls the same NCS workspace the plain SDK flow uses:

```bash
./ubx-matter.sh alma-b20-b21 --list                      # the nrf/samples/matter apps
./ubx-matter.sh alma-b20-b21 --build light_bulb --flash --log
```

A bare app name is scoped to `matter/`, so `light_bulb` cannot collide with a
same-named sample elsewhere in the tree. Because NCS builds natively on
Windows, this target never hops into WSL2. `ubx-sdk` builds the same sample if
you give the full path (`--build matter/light_bulb`).

Matter runs over Thread here, since the nRF54LM20 has no Wi-Fi radio.

---

## Build output

```
<ncs workspace>/build/<sample>/zephyr/
    zephyr.elf
    zephyr.hex
    zephyr.bin
```

---

## Flashing

```bash
./ubx-sdk.sh alma-b20-b21 --flash hello_world
```

`nrfutil` is the default runner. J-Link device names:

| Core | Device |
|------|--------|
| nRF54LM20 application core | `nRF54LM20A_M33` |
| nRF54LM20 FLPR coprocessor | `nRF54LM20A_RV32` |

Note that the `A` device name is used for both SoC variants.

---

## Known limitations

- No `ubx_evkalmab2` board definition; the Nordic DK stands in.
- The module is not in general production, so part availability, pinout and
  documentation may still change.
- The Axon NPU toolchain is distributed separately by Nordic and is not driven
  by this SDK.

---

## References

- ALMA-B20-B21 product page: https://www.u-blox.com/en/product/alma-b2-series
- nRF Connect SDK documentation: https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/index.html
- NORA-B20-B21-B22 guide (same toolchain): [nora_b20_b21_b22_README.md](nora_b20_b21_b22_README.md)
