# IRIS-W1 Open CPU — Getting started with the NXP MCUXpresso SDK

Build your own firmware on the module's own Cortex-M33 (Open CPU) using NXP's MCUXpresso SDK
and NXP's example applications. Covers Windows, Linux and WSL2.

---

## 1. What you are targeting

| Item | Value |
|---|---|
| Modules | IRIS-W1 series (EVK-IRIS-W1, USB-IRIS-W1) |
| SoC | NXP **RW612** (part `RW612ETA2I`) |
| MCU | Arm Cortex-M33 |
| Radio | Wi-Fi 6, Bluetooth LE, 802.15.4 |
| SDK | **MCUXpresso SDK** (GitHub multi-repo, managed with `west`) |
| SDK board target | `rdrw612bga` |
| J-Link device name | `RW610` |

> The SDK ships board files for NXP's `RD-RW612-BGA` reference design. For a u-blox EVK you keep
> the same device but use the u-blox board files, flash config and calibration data in
> [MCUXpresso/IRIS-W1/sw_config](../MCUXpresso/IRIS-W1/sw_config/README.md).

There are two ways to build:

- **Track A — `west` command line.** What this script automates. Reproducible, CI-friendly.
- **Track B — MCUXpresso IDE.** GUI flow, documented in
  [MCUXpresso/IRIS-W1/EVK-IRIS-W1](../MCUXpresso/IRIS-W1/EVK-IRIS-W1/README.md).

---

## 2. Prerequisites

| Tool | Minimum version | Where |
|---|---|---|
| Python | 3.10 | <https://www.python.org/downloads/> |
| Git | 2.25 | <https://git-scm.com/> |
| west | 1.2.0 | `pip install -U west` |
| CMake | 3.30 | <https://cmake.org/download/> |
| Ninja | 1.12.1 | <https://ninja-build.org/> |
| Arm GNU Toolchain | — | <https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads> |
| J-Link software (flashing) | — | <https://www.segger.com/downloads/jlink/> |

On Windows the **MCUXpresso Installer** can install all of the above in one step:
<https://github.com/nxp-mcuxpresso/vscode-for-mcux/wiki/Dependency-Installation>

### ARMGCC_DIR

The MCUXpresso build system locates the compiler through the `ARMGCC_DIR` environment variable.
It must point at the toolchain root — the directory *containing* `bin/`, not `bin/` itself.

```powershell
# Windows
setx ARMGCC_DIR "C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1"
```

```bash
# Linux / WSL2 (distro package)
export ARMGCC_DIR="/usr"
```

---

## 3. Automated build

[iris_w1_build.py](iris_w1_build.py) automates the flow below on Windows, WSL2 and Linux.

```bash
python iris_w1_build.py doctor                        # what is installed, what is missing
python iris_w1_build.py install                       # install west, report toolchain status
python iris_w1_build.py clone                         # init workspace, fetch RW612 repos
python iris_w1_build.py list                          # show available examples
python iris_w1_build.py build demo_apps/hello_world   # build one example
```

Or the whole pipeline in one go:

```bash
python iris_w1_build.py all demo_apps/hello_world
```

Settings are cached in `.iris_w1_build.<host>.json`, one file per host type so the same
folder can be shared between Windows and WSL2.

### Commands

| Command | What it does |
|---|---|
| `doctor` | Report Python, Git, west, CMake, Ninja, Arm GCC, `ARMGCC_DIR` and workspace status |
| `install` | `pip install -U west`, then report what still needs installing manually |
| `clone` | `west init` + fetch only the repositories `rdrw612bga` needs |
| `list` | List examples found in the workspace |
| `build` | `west build` for the given example |
| `clean` | Remove the build directory, or `--all` to remove the whole workspace |
| `all` | `install` → `clone` → `build` |

### Useful options

```bash
python iris_w1_build.py clone --full               # fetch the complete SDK (~7 GB, not just RW612)
python iris_w1_build.py clone --revision v25.09.00 # pin to a manifest release tag
python iris_w1_build.py build hello_world --config release
python iris_w1_build.py build hello_world -p       # pristine (clean) rebuild
python iris_w1_build.py --board rdrw612bga list    # override the board target
```

`build` accepts either a full path (`demo_apps/hello_world`) or a bare example name
(`hello_world`). A bare name that matches more than one example lists the candidates instead
of guessing.

---

## 4. Manual build

If you would rather drive `west` yourself:

```bash
pip install -U west

west init -m https://github.com/nxp-mcuxpresso/mcuxsdk-manifests.git mcuxpresso-sdk
cd mcuxpresso-sdk

# Fetch only what rdrw612bga needs (~2 GB instead of ~7 GB)
west update_board --set board rdrw612bga

# Check which configurations an example supports
west list_project -p examples/demo_apps/hello_world -t armgcc

# Build
west build -b rdrw612bga examples/demo_apps/hello_world --toolchain armgcc --config debug
```

Disk space: roughly **2 GB** for a board-targeted workspace, **7–8 GB** for the full SDK.

---

## 5. Flashing

| Board | Method |
|---|---|
| EVK-IRIS-W1 | Onboard **MCU-Link** debugger (enabled by default) |
| USB-IRIS-W1 | External debugger via the **J4** 10-pin JTAG header |
| Either | **J-Flash Lite** or **J-Link Commander**, J-Link device name `RW610` |
| Recovery | **blhost** — see [recovery_tool/blhost](../MCUXpresso/IRIS-W1/recovery_tool/blhost/) |

From a west workspace:

```bash
west flash -r linkserver
```

Radio firmware blobs are flashed separately:

| Image | Address |
|---|---|
| Wi-Fi (`rw610_sb_wifi_aXX.bin`) | `0x08400000` |
| Bluetooth (`rw61x_sb_ble_aXX.bin`) | `0x08540000` |

---

## 6. u-blox specific configuration

This script sets up the stock NXP SDK. For u-blox hardware you will also want the board files,
linker scripts, flash configuration and calibration data from the existing
[MCUXpresso/IRIS-W1](../MCUXpresso/IRIS-W1/README.md) folder:

| Folder | Contents |
|---|---|
| [`sw_config/board_files`](../MCUXpresso/IRIS-W1/sw_config/) | EVK-IRIS-W1 board definitions (LEDs, switches) |
| [`sw_config/flash_config`](../MCUXpresso/IRIS-W1/sw_config/) | Flash memory configuration |
| [`sw_config/Linker_Scripts`](../MCUXpresso/IRIS-W1/sw_config/) | `RW612_flash.ld` for ARMGCC, `.ldt` for MCUXpresso IDE |
| [`sw_config/wifi_Calibration`](../MCUXpresso/IRIS-W1/sw_config/) | Wi-Fi calibration data |
| [`sw_config/BT_802_15_4_Calibration_Files`](../MCUXpresso/IRIS-W1/sw_config/) | BLE / 802.15.4 calibration |
| [`compiled_binaries`](../MCUXpresso/IRIS-W1/compiled_binaries/) | Prebuilt images for quick bring-up |
| [`example_code`](../MCUXpresso/IRIS-W1/example_code/README.md) | Read serial number, module type, Wi-Fi MAC |

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `west: command not found` | `pip install -U west`, or run `python iris_w1_build.py install` |
| Build cannot find the compiler | `ARMGCC_DIR` unset or pointing at `bin/` instead of the toolchain root |
| `Repository '...' not found in manifest` during `clone` | Harmless — optional middleware not in this manifest revision |
| Example not found | Run `list`; not every example supports every board |
| Build fails after changing config | `python iris_w1_build.py build <example> -p` for a pristine rebuild |
| Workspace in a bad state | `python iris_w1_build.py clean --all`, then `clone` again |
| Module unresponsive / bad flash | Recover with [blhost](../MCUXpresso/IRIS-W1/recovery_tool/blhost/) |

---

## 8. Related

- [NORA-W50/W51 Getting Started](../NORA-W50-W51-GettingStartedSDK/README.md) — TI SimpleLink
- [NORA-W30 Getting Started](../NORA-W30-GettingStartedSDK/README.md) — Realtek
- [NORA-W40 Getting Started](../NORA-W40-GettingStartedSDK/README.md) — ESP-IDF
- [MCUXpresso SDK documentation](https://mcuxpresso.nxp.com/mcuxsdk/latest/html/index.html)
- [MCUXpresso SDK Portal](https://mcuxpresso.nxp.com/en/welcome)
