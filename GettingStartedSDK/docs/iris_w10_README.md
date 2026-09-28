# u-blox IRIS-W10 Module (NXP RW612/RW610)

This repository contains setup information, configuration files, and example binaries for the u-blox IRIS-W10 module.

## Quick Start

Build and flash a Wi-Fi example in 3 commands:

```bash
python iris_w10_build.py install          # Install west + report toolchain status
python iris_w10_build.py clone            # Fetch MCUXpresso SDK (~2 GB, RW612 only)
python iris_w10_build.py build demo_apps/hello_world  # Build example
```

## Features

| Feature | IRIS-W10 |
|---------|---------|
| **SoC** | NXP RW612 (with Thread) or RW610 (Wi-Fi + BLE only) |
| **MCU** | Arm Cortex-M33 @ 260 MHz |
| **Memory** | 1.2 MB SRAM, 8 or 16 MB QSPI Flash |
| **Radio** | Wi-Fi 6 (2.4/5 GHz), Bluetooth LE 5.4, optional Thread/802.15.4 |
| **Security** | Secure boot, TrustZone-M, hardware crypto accelerator |
| **Open CPU** | Embedded MCU for custom applications |
| **SDK** | NXP MCUXpresso (west/CMake/Ninja) |
| **Variants** | IRIS-W101 (external antenna), IRIS-W106 (PCB antenna); 8 MB or 16 MB flash |
| **Evaluation Boards** | EVK-IRIS-W10, USB-IRIS-W10 |

## Prerequisites

### Minimum

| Tool | Version | Windows | WSL2 | Linux |
|------|---------|---------|------|-------|
| Python | 3.10+ | ✅ | ✅ | ✅ |
| Git | 2.25+ | ✅ | ✅ | ✅ |
| west | 1.2.0+ | (pip) | (pip) | (pip) |
| CMake | 3.30+ | ✅ | ✅ | ✅ |
| Ninja | 1.12.1+ | ✅ | ✅ | ✅ |
| **Arm GNU Toolchain** | 13.2.0+ | ✅ | ✅ | ✅ |

### Environment Variables

**Required:** Set `ARMGCC_DIR` to the root directory of the Arm GNU Toolchain (NOT the `bin/` subdirectory).

**Windows:**
```batch
setx ARMGCC_DIR "C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\13.2.0"
REM (then open a new terminal)
```

**Linux/WSL2:**
```bash
export ARMGCC_DIR=/usr
# Or wherever your Arm GNU is installed (e.g., /opt/arm-gnu-toolchain-13.2.0)
# Add to ~/.bashrc to make permanent
```

**Verify:**
```bash
python iris_w10_build.py doctor
```

## Installation & Setup

### 0. (Recommended) Setup Shared Virtual Environment

All u-blox build scripts share the same Python dependencies. Set up a shared virtual environment at the repo root (one-time setup):

```bash
cd ../..  # Go to repo root
python setup_venv.py
```

Then activate it in your current terminal:

**Windows CMD:**
```batch
.venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS/WSL2:**
```bash
source .venv/bin/activate
```

To deactivate later: `deactivate`

**Note:** This is recommended but optional. The scripts will warn if running outside a venv and still work with system Python.

### 1. Install Build Dependencies

```bash
python iris_w10_build.py install
```

This will:
- ✅ Install `west` via pip
- ⚠️ Report on any missing tools (CMake, Ninja, Arm GCC)

**Missing tools?** Install manually:

**Windows:**
- [CMake 3.30+](https://cmake.org/download)
- [Ninja 1.12.1+](https://ninja-build.org)
- [Arm GNU Toolchain](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)

Or use the MCUXpresso Installer:
- [MCUXpresso Dependency Installation](https://github.com/nxp-mcuxpresso/vscode-for-mcux/wiki/Dependency-Installation)

**Linux/WSL2:**
```bash
sudo apt update && sudo apt install -y cmake ninja-build gcc-arm-none-eabi
```

### 2. Clone SDK & Workspace

```bash
python iris_w10_build.py clone
```

**Options:**
- `--full` — Fetch entire SDK (~7 GB instead of targeted ~2 GB)
- `--revision v25.09.00` — Specify SDK version (default: latest)

This creates:
```
./mcuxpresso-sdk/
  ├── .west/
  ├── mcuxsdk/
  │   ├── boards/rdrw612bga/  (board definitions)
  │   └── examples/           (100+ examples)
  └── manifests/
```

### 3. List & Build Examples

**List available examples:**
```bash
python iris_w10_build.py list
```

**Build an example:**
```bash
python iris_w10_build.py build demo_apps/hello_world
python iris_w10_build.py build wifi_cli --config release
python iris_w10_build.py build ble_peripheral -p  # pristine (clean) build
```

**Build output:**
```
./mcuxpresso-sdk/build/
  ├── zephyr.bin         (firmware image)
  ├── zephyr.elf
  ├── zephyr.map
  └── ...
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `python iris_w10_build.py doctor` | Verify environment & tools |
| `python iris_w10_build.py install` | Install west + show tool requirements |
| `python iris_w10_build.py clone` | Initialize west workspace (2 GB, RW612 board only) |
| `python iris_w10_build.py clone --full` | Fetch complete SDK (7 GB) |
| `python iris_w10_build.py list` | Show available examples |
| `python iris_w10_build.py build <example>` | Build an example |
| `python iris_w10_build.py build <example> --config release` | Release build (optimized) |
| `python iris_w10_build.py build <example> -p` | Pristine (force clean) build |
| `python iris_w10_build.py clean` | Remove build artifacts |
| `python iris_w10_build.py clean --all` | Remove entire SDK workspace |
| `python iris_w10_build.py all demo_apps/hello_world` | Full pipeline (install → clone → build) |

## Flashing & Debugging

### Onboard Debugger (EVK-IRIS-W10)

EVK boards include an **MCU-Link** onboard debugger. To program:

```bash
cd mcuxpresso-sdk
west flash -r linkserver
```

Or use the MCUXpresso IDE's Debug feature.

### External Debugger (USB-IRIS-W10)

Connect a J-Link or MCU-Link Pro via the JTAG/SWD header, then:

```bash
cd mcuxpresso-sdk
west flash -r jlink
```

### Manual Flashing (blhost)

Use NXP's `blhost` utility for low-level programming or recovery:

```bash
blhost -p <COM-PORT> fill-memory 0 4 0xc0403050
blhost -p <COM-PORT> write-memory 0 <firmware.bin>
```

Refer to the [u-blox Short Range OpenCPU repository](https://github.com/u-blox/u-blox-sho-OpenCPU/tree/master/MCUXpresso/IRIS-W1/recovery_tool) for recovery tools.

## Board Files & Calibration Data

To add u-blox specific features (RF calibration, GPIO pinmux, linker scripts), copy files from the [u-blox OpenCPU repository](https://github.com/u-blox/u-blox-sho-OpenCPU):

```bash
# Copy board-specific configurations
cp -r MCUXpresso/IRIS-W1/sw_config/* ./mcuxpresso-sdk/mcuxsdk/boards/rdrw612bga/
```

Key files:
- **`pin_mux.c/h`** — GPIO/LED/switch configuration
- **`wifi_Calibration/`** — Wi-Fi TX power calibration data
- **`BT_802_15_4_Calibration_Files/`** — Bluetooth & Thread calibration
- **`Linker_Scripts/`** — u-blox-specific linker script variants

## Troubleshooting

### west not found
```
❌ west not found. Run 'python iris_w10_build.py install' first.
```
**Fix:** Run `python -m pip install -U west`

### ARMGCC_DIR not set
```
⚠️ ARMGCC_DIR is not set; the build will likely fail.
```
**Fix:** Set the environment variable and open a new terminal:
```bash
# Windows
setx ARMGCC_DIR "C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\13.2.0"

# Linux/WSL2
export ARMGCC_DIR=/usr
```

### Build fails with "CMake not found"
**Fix:** Install CMake 3.30+:
```bash
# Windows: https://cmake.org/download
# Linux/WSL2:
sudo apt install cmake
```

### build/ directory exists (force rebuild)
Use the `-p` (pristine) flag:
```bash
python iris_w10_build.py build demo_apps/hello_world -p
```

### Need a specific SDK version
```bash
python iris_w10_build.py clone --revision v25.03.00
```

### Partial download (only RW612)?
Default behavior fetches ~2 GB (RW612 only). For full SDK (~7 GB):
```bash
python iris_w10_build.py clone --full
```

## Performance & Disk Space

| Operation | Typical Time | Disk Space |
|-----------|------|------|
| `install` | 2-5 min | < 500 MB (pip packages) |
| `clone` (targeted) | 5-15 min | ~2 GB (RW612 + examples) |
| `clone --full` | 15-30 min | ~7 GB (complete SDK) |
| First `build` | 5-10 min | ~300 MB (build artifacts) |
| Incremental `build` | 1-3 min | — |

## Platform Support

| Platform | Support | Notes |
|----------|---------|-------|
| Windows 11 | ✅ | Requires ARMGCC_DIR env var |
| WSL2 | ✅ | Recommended for Windows users |
| Ubuntu 22.04 LTS | ✅ | `sudo apt install gcc-arm-none-eabi` |
| macOS | ⚠️ | Not tested; Arm GNU Toolchain may require Homebrew |

## Resources

- **u-blox OpenCPU GitHub:** https://github.com/u-blox/u-blox-sho-OpenCPU
- **NXP MCUXpresso SDK:** https://mcuxpresso.nxp.com
- **MCUXpresso SDK Documentation:** https://mcuxpresso.nxp.com/mcuxsdk/latest/html/
- **IRIS-W10 Datasheet:** https://content.u-blox.com/sites/default/files/documents/IRIS-W10_DataSheet_UBX-23002331.pdf
- **EVK-IRIS-W10 User Guide:** https://content.u-blox.com/sites/default/files/documents/EVK-IRIS-W10_UserGuide_UBX-23007837.pdf
- **Arm GNU Toolchain:** https://developer.arm.com/Tools%20and%20Software/GNU%20Toolchain

## See Also

- [IRIS-W1 Getting Started](../IRIS-W1-GettingStartedSDK/README.md) — Alternative RW612 variant
- [BUILD_ALL_EXAMPLES.md](../BUILD_ALL_EXAMPLES.md) — Cross-variant build guide
- [QUICK_BUILD_REFERENCE.md](../QUICK_BUILD_REFERENCE.md) — Command cheatsheet for all variants
