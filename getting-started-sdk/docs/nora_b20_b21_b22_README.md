# NORA-B20-B21-B22 Getting Started Guide

## Overview

NORA-B20-B21-B22 modules are based on the **Nordic nRF54L** SoC family and are built with
the **nRF Connect SDK** (NCS) - Nordic's Zephyr RTOS distribution. The modules
ship with no pre-flashed software: you own the whole application.

**Key features:**
- Arm Cortex-M33 @ 128 MHz with FPU, DSP, TrustZone and CryptoCell-312
- Separate 128 MHz RISC-V coprocessor (FLPR) for low-latency peripheral work
- Bluetooth Core 6.0 qualified, including Channel Sounding and LE Audio
- IEEE 802.15.4-2020 for Thread, Matter and Zigbee
- Nordic proprietary 2.4 GHz, up to 4 Mbps
- +7.0 dBm conducted / +10 dBm EIRP output power
- NFC tag, 31 GPIO, 5x serial (UART/I2C/SPI), 7x timers, 2x QDEC, SWD

**SDK:** nRF Connect SDK v3.4.1 (Zephyr RTOS + MCUboot + nrfxlib)
**Platforms:** Windows, WSL2, Linux, macOS
**Build system:** west + CMake + Ninja
**Debug probe:** on-board SEGGER J-LINK-OB on both EVKs

---

## Module variants

| Part | SoC | NVM | RAM | Antenna |
|------|-----|-----|-----|---------|
| NORA-B201 | nRF54L15 | 1.5 MB | 256 KB | Antenna pin |
| NORA-B206 | nRF54L15 | 1.5 MB | 256 KB | Internal PCB |
| NORA-B211 | nRF54L10 | 1.0 MB | 192 KB | Antenna pin |
| NORA-B216 | nRF54L10 | 1.0 MB | 192 KB | Internal PCB |
| NORA-B221 | nRF54L05 | 0.5 MB | 96 KB | Antenna pin |
| NORA-B226 | nRF54L05 | 0.5 MB | 96 KB | Internal PCB |

NORA-B26x and NORA-B27x are **u-connectXpress** modules: they ship with
AT-command firmware pre-flashed and are not built from this Open CPU SDK.

**Evaluation kits:** EVK-NORA-B201 (external antenna, U.FL) and
EVK-NORA-B206 (internal antenna).

---

## Board targets

The `ubx_evknorab2` board is upstream in both mainline Zephyr and the nRF
Connect SDK, so no out-of-tree board definition is needed.

| Board target | Module |
|--------------|--------|
| `ubx_evknorab2/nrf54l15/cpuapp` | NORA-B20x (default) |
| `ubx_evknorab2/nrf54l15/cpuapp/ns` | NORA-B20x, TF-M non-secure |
| `ubx_evknorab2/nrf54l10/cpuapp` | NORA-B21x |
| `ubx_evknorab2/nrf54l10/cpuapp/ns` | NORA-B21x, TF-M non-secure |
| `ubx_evknorab2/nrf54l05/cpuapp` | NORA-B22x |
| `ubx_evknorab2/nrf54l15/cpuflpr` | RISC-V coprocessor |

Override the default with `--board`:

```bash
./ubx-sdk.sh nora-b20-b21-b22 --build hello_world -- --board ubx_evknorab2/nrf54l10/cpuapp
```

---

## Prerequisites

The simplest route on every platform is **nRF Connect for Desktop** and its
Toolchain Manager, which installs the Zephyr SDK, CMake, Ninja, west and
nrfutil in one step: https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop

Manual setup needs:

- Python 3.10+
- Git
- CMake 3.20+ and Ninja
- `west` (`pip install west`)
- Zephyr SDK (sets `ZEPHYR_SDK_INSTALL_DIR`), or an Arm GNU toolchain
- `nrfutil` for flashing (J-Link also works)

Check what is present:

```bash
./ubx-sdk.sh nora-b20-b21-b22 --doctor
```

### Linux serial and probe access

```bash
sudo usermod -a -G dialout $USER
# Log out and back in to apply
```

---

## Quick start

```bash
# Fetch the nRF Connect SDK (several GB, once)
./ubx-sdk.sh nora-b20-b21-b22 --clone

# Install the Zephyr Python requirements
./ubx-sdk.sh nora-b20-b21-b22 --install

# See what you can build
./ubx-sdk.sh nora-b20-b21-b22 --list

# Build, flash and watch the output
./ubx-sdk.sh nora-b20-b21-b22 --build hello_world --flash --log
```

### Where the SDK lives

`--clone` creates the workspace in `C:\ncs\v3.4.1` on Windows (the same
layout nRF Connect for Desktop uses) and `~/ncs/v3.4.1` on Linux, never on the
repository's drive. It checks free space first: NCS needs about 15 GB.

Existing workspaces are detected: `C:\ncs\*`, `~/ncs`, `~/ncs/*`, `~/ncs-*`
and `ZEPHYR_BASE`. The one that has the board, preferably at v3.4.1, is used.
`--doctor` lists them all. To pick one explicitly:

```bash
python scripts/nordic_ncs_build.py nora-b20-b21-b22 use                    # list
python scripts/nordic_ncs_build.py nora-b20-b21-b22 use C:\ncs\v3.4.1      # select
# or for one shell: set UBX_NCS_WORKSPACE=C:\ncs\v3.4.1
```

---

## Samples

Samples are searched for in `nrf/samples/`, `nrf/applications/` and
`zephyr/samples/`. Useful starting points:

| Sample | What it does |
|--------|--------------|
| `hello_world` | Minimal Zephyr application |
| `blinky` | LED toggle, verifies the board definition |
| `peripheral_uart` | Nordic UART Service over Bluetooth LE |
| `peripheral_hr` | Bluetooth LE heart rate sensor |
| `channel_sounding_ras_initiator` | Bluetooth 6.0 Channel Sounding |
| `matter/light_bulb` | Matter over Thread |

A name is enough when it is unique; otherwise pass the path shown by `--list`.

---

## Matter

Matter support ships inside the nRF Connect SDK, so there is no separate Matter
SDK to fetch — `--clone` pulls the same NCS workspace the plain SDK flow uses:

```bash
./ubx-matter.sh nora-b20-b21-b22 --list                      # the nrf/samples/matter apps
./ubx-matter.sh nora-b20-b21-b22 --build light_bulb --flash --log
```

A bare app name is scoped to `matter/`, so `light_bulb` cannot collide with a
same-named sample elsewhere in the tree. Because NCS builds natively on
Windows, this target never hops into WSL2. `ubx-sdk` builds the same sample if
you give the full path (`--build matter/light_bulb`).

---

## Build output

```
<ncs workspace>/build/<sample>/zephyr/
    zephyr.elf      full image with symbols
    zephyr.hex      flashable image
    zephyr.bin      raw binary
```

---

## Flashing

```bash
./ubx-sdk.sh nora-b20-b21-b22 --flash hello_world
```

Both EVKs carry a SEGGER J-LINK-OB, so no external probe is needed. `nrfutil`
is the default runner; pass `-- --runner jlink` to use J-Link instead. With
several probes attached, select one with `--flash <SERIAL>`.

J-Link device names, for manual invocations:

| Core | Device |
|------|--------|
| nRF54L15/L10/L05 application core | `nRF54L15_M33` |
| nRF54L15 FLPR coprocessor | `nRF54L15_RV32` |

---

## Troubleshooting

**`--doctor` reports no toolchain**
Install the Zephyr SDK, or set `ZEPHYR_SDK_INSTALL_DIR` /
`GNUARMEMB_TOOLCHAIN_PATH` to an existing one.

**Board target not found**
The `ubx_evknorab2` board needs NCS v3.x. `--doctor` shows the version of the
workspace in use. An older workspace (for example an NCS v2.9 install at
`~/ncs`) does not contain the board; clone a current one with
`./ubx-sdk.sh nora-b20-b21-b22 --clone`, or select another with `use` (see above).

**`west update` fails or is interrupted**
Re-run `./ubx-sdk.sh nora-b20-b21-b22 --clone`. It skips `west init` when the workspace
already exists and resumes the update.

**No serial output after flashing**
The EVK exposes several COM ports. Pass the right one explicitly:
`./ubx-sdk.sh nora-b20-b21-b22 --log COM12`.

---

## References

- NORA-B20-B21-B22 product page: https://www.u-blox.com/en/product/nora-b2-series
- nRF Connect SDK documentation: https://docs.nordicsemi.com/bundle/ncs-latest/page/nrf/index.html
- Zephyr board documentation: `<ncs workspace>/zephyr/boards/u-blox/ubx_evknorab2/`
