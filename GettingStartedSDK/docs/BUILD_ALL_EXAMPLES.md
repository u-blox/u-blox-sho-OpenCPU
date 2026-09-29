# Building NORA-W50/W51, W30, W40 and IRIS-W10 From Scratch

Complete examples showing how to build firmware for all four u-blox Open CPU module families from initial setup to working examples.

---

## 1. NORA-W50/W51 (TI SimpleLink WiFi SDK) — Windows/WSL2/Linux

### Prerequisites
- TI SimpleLink WiFi SDK (installed or cloned)
- SysConfig 1.28.0+
- TI Arm Clang OR Arm GNU Toolchain
- CMake 3.16+
- GNU Make
- Python 3.8+

### Complete Build Workflow

```bash
# Step 1: Navigate to workspace
cd ~/nora-w50-w51    # or ./workspace on Windows/WSL2

# Step 2: Check environment
python nora_w50_w51_build.py doctor
# Output: Shows all tools (SysConfig, TI Clang, Arm GNU, CMake, Make, Python)

# Step 3: Clone TI example repos (if no SDK installed)
python nora_w50_w51_build.py clone
# Clones: https://github.com/TexasInstruments/simplelink-wifi-examples.git
#         + SDK as git submodule

# Step 4: Install/show tool information
python nora_w50_w51_build.py install
# Displays: Download links for SysConfig, toolchains, SDK

# Step 5: Configure tool paths
python nora_w50_w51_build.py configure
# Creates: imports.mak with detected tool paths
# Backs up: imports.mak.orig

# Step 6: Build SDK libraries (slow, one-time)
python nora_w50_w51_build.py build-sdk --toolchain ticlang
# Builds: 141 TI SimpleLink SDK libraries
# Takes: ~10-15 minutes

# Step 7: List available examples
python nora_w50_w51_build.py list
# Shows: uart2echo, network_terminal, ble_wifi_provisioning, etc.

# Step 8: Build an example
python nora_w50_w51_build.py build network_terminal --toolchain ticlang
# Output: ~/nora-w50-w51/wifi-examples/network_terminal/ticlang/Release/network_terminal.out (17 MB)

# Step 9: Or do entire pipeline in one command
python nora_w50_w51_build.py all network_terminal --toolchain ticlang
# Runs: configure → build-sdk → build in sequence

# Step 10: Clean if build fails
python nora_w50_w51_build.py build-sdk --clean  # Clean SDK rebuild
python nora_w50_w51_build.py build --clean      # Clean example rebuild
```

### Result
[OK] Firmware image ready for flashing to NORA-W50/W51 via XDS110 or serial bootloader

---

## 2. NORA-W30 (Realtek RTL872x RTOS) — Linux/WSL2 Only

### Prerequisites
- Linux (native) OR WSL2 (Ubuntu recommended)
- arm-none-eabi-gcc
- GNU Make
- Git
- Python 3.8+
- Virtual environment with build dependencies

**Note:** Windows native/Cygwin not recommended

### Complete Build Workflow

```bash
# Step 1: Navigate to GettingStartedSDK workspace
cd GettingStartedSDK

# Step 2: Activate virtual environment (Linux/WSL2)
source .venv/bin/activate
# Confirm: prompt shows (.venv) prefix

# Step 3: Check environment
python scripts/nora_w30_build.py doctor
# Output: Python [OK], Git [OK], Make [OK], Arm GCC [OK]

# Step 4: Clone Ameba-D SDK
python scripts/nora_w30_build.py clone
# Clones: https://github.com/ambiot/ameba-rtos-d.git into ameba-rtos-d/
# Detects checked-in ameba-rtos-d/ at workspace root first

# Step 5: List available example sources
python scripts/nora_w30_build.py list
# Shows: ADC, Audio, BOD, CRYPTO, FLASH, GPIO, I2C, I2S, KEY, LCDC,
#        PMC, RTC, SDIO, SPI, TIMER, UART, gdma, ir, rdp, watchdog, wlan
# Note: These are example sources, not separate build targets

# Step 6: Build KM4 Firmware (project_hp, default)
python scripts/nora_w30_build.py build
# Output: km4_boot_all.bin, km4_km0_image2.bin, ram_1.bin
# Location: ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp/asdk/image/

# Step 7: Or build KM0 Firmware (project_lp)
python scripts/nora_w30_build.py build project_lp
# Output: km0_boot_all.bin, km0_image2_all.bin, ram_1.bin
# Location: ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE/project_lp/asdk/image/

# Step 8: Clean build artifacts
python scripts/nora_w30_build.py clean
# Removes: build/ directories from both project_hp and project_lp

# Step 9: Clean entire SDK
python scripts/nora_w30_build.py clean --all
# Removes: ameba-rtos-d/ directory entirely
```

### Build Architecture

Ameba-D is a **dual-core SoC** with:
- **KM0 Project** (Low-power core): Bootloader, power management
- **KM4 Project** (High-performance core): Main application, WiFi stack

Build outputs:
- `km4_boot_all.bin` — KM4 bootloader (4 KB)
- `km4_km0_image2.bin` — Dual-core application firmware
- `ram_1.bin` — RAM overlay image
- `xip_boot.bin` — Execute-in-place boot image

### Result
[OK] Ameba-D firmware images ready for flashing to NORA-W30 via UART ImageTool
# Shows: hello_world, wifi_sta, ota, gpio_blink, etc.

# Step 6: Build an example
python3 nora_w30_build.py build hello_world
# Output: realtek-rtos-sdk/examples/hello_world/build/hello_world.axf

# Step 7: Or use full pipeline
python3 nora_w30_build.py all hello_world
# Runs: clone → build in sequence

# Step 8: Build another example
python3 nora_w30_build.py build wifi_sta
# Output: realtek-rtos-sdk/examples/wifi_sta/build/wifi_sta.axf

# Step 9: Clean if needed
python3 nora_w30_build.py clean hello_world     # Clean hello_world build
python3 nora_w30_build.py clean --all           # Remove entire SDK (~500MB)
```

### Result
[OK] Firmware ELF ready for flashing to NORA-W30 via UART with Realtek flash tool

---

## 3. NORA-W40 (ESP32-C6 + ESP-IDF v6.2) — Windows/WSL2/Linux

### Prerequisites
- Python 3.9+
- Git 2.20+
- CMake 3.16+
- GNU Make
- Virtual environment with build dependencies
- Windows: MSYS2 or use WSL2 (recommended)
- Linux/WSL2: standard build tools

### Complete Build Workflow

```bash
# Step 1: Navigate to GettingStartedSDK workspace
cd GettingStartedSDK

# Step 2: Activate shared virtual environment
source .venv/bin/activate              # Linux/WSL2
# or on Windows: .venv\Scripts\activate

# Step 3: Check environment
python scripts/nora_w40_build.py doctor
# Output: Python [OK], Git [OK], CMake [OK], Make [OK], ESP-IDF [FAIL] (not cloned yet)

# Step 4: Clone ESP-IDF v6.2 (first time only, ~200MB)
python scripts/nora_w40_build.py clone
# Clones: https://github.com/espressif/esp-idf.git (v6.2)
# Creates: esp-idf/ folder
# Saves: config in targets/NORA-W40/config/build.{platform}.json

# Step 5: Install ESP-IDF environment (downloads ~600MB toolchain)
python scripts/nora_w40_build.py install
# Creates: ~/.espressif/python_env/idf6.2_py3.14_env/
# Downloads: riscv32-esp-elf-16.1.0_20260609 toolchain
# Takes: 10-15 minutes on first run

# Step 6: List available examples
python scripts/nora_w40_build.py list
# Shows: get-started/hello_world, get-started/blink, 
#        network/http_server, bluetooth/ble_provisioning, etc.

# Step 7: Build hello_world example (RISC-V ESP32-C6)
python scripts/nora_w40_build.py build hello_world
# Auto-detects: ESP-IDF Python environment, RISC-V toolchain
# Sets target: IDF_TARGET=esp32c6 (critical for correct CPU architecture)
# Output: esp-idf/examples/get-started/hello_world/build/hello_world.elf, .bin (128 KB)

# Step 8: Build another example
python scripts/nora_w40_build.py build network/http_server
# Output: esp-idf/examples/network/http_server/build/http_server.bin

# Step 9: Clean example build
python scripts/nora_w40_build.py clean hello_world
# Removes: build/ directory for that example

# Step 10: Clean entire ESP-IDF
python scripts/nora_w40_build.py clean --all
# Removes: esp-idf/ directory (~600MB)
```

### Critical NORA-W40 Details

**CPU Architecture:** ESP32-C6 is **RISC-V** (not Xtensa like ESP32-S3)
- **Toolchain:** riscv32-esp-elf (not xtensa-esp32s3-elf)
- **Environment:** IDF_TARGET must be "esp32c6"
- **Python Env:** Separate ESP-IDF Python (~/.espressif/python_env/idf6.2_py3.14_env/)

**Build Output:**
- hello_world.elf (512 KB) — Loadable image
- hello_world.bin (128 KB) — Firmware image
- Location: esp-idf/examples/get-started/hello_world/build/

### Result
[OK] ESP32-C6 (RISC-V) firmware image ready for flashing to NORA-W40 via esptool.py

---

## 4. IRIS-W10 (NXP RW612/RW610 / MCUXpresso SDK) — Windows/WSL2/Linux

### Prerequisites
- Python 3.10+, Git 2.25+
- CMake 3.30+, Ninja 1.12.1+
- Arm GNU Toolchain (`arm-none-eabi-gcc`)
- `ARMGCC_DIR` environment variable pointing at the toolchain root
- ~2 GB free disk space (board-targeted workspace)

> On Windows the [MCUXpresso Installer](https://github.com/nxp-mcuxpresso/vscode-for-mcux/wiki/Dependency-Installation)
> installs CMake, Ninja and Arm GCC in one step.

### Complete Build Workflow

```bash
# Step 1: Navigate to workspace
cd GettingStartedSDK

# Step 2: Check environment
python scripts/iris_w10_build.py doctor
# Output: Python [OK], Git [OK], West [OK], CMake [OK], Ninja [OK], Arm GCC [OK], workspace [FAIL] (not yet)
# Also reports whether ARMGCC_DIR is set

# Step 3: Install west and check remaining toolchain
python scripts/iris_w10_build.py install
# Runs: pip install -U west
# Reports: anything still missing + how to set ARMGCC_DIR

# Step 4: Set ARMGCC_DIR (one time, then reopen the terminal)
# Windows: setx ARMGCC_DIR "C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1"
# Linux:   export ARMGCC_DIR="/usr"

# Step 5: Initialise the SDK workspace (~2 GB, first time only)
python scripts/iris_w10_build.py clone
# Runs: west init -m https://github.com/nxp-mcuxpresso/mcuxsdk-manifests.git mcuxpresso-sdk
#       west update_board --set board rdrw612bga
# Fetches only the 63 repositories rdrw612bga needs, not the full ~7 GB SDK
# Use --full for the complete SDK, or --revision v25.09.00 to pin a release

# Step 6: List available examples
python scripts/iris_w10_build.py list
# Shows: demo_apps/hello_world, wifi_examples/wifi_cli, etc.

# Step 7: Build an example
python scripts/iris_w10_build.py build demo_apps/hello_world
# Runs: west build -b rdrw612bga examples/demo_apps/hello_world --toolchain armgcc --config debug
# Output: mcuxpresso-sdk/build/

# Bare names work too when unambiguous:
python scripts/iris_w10_build.py build hello_world

# Step 8: Release build / pristine rebuild
python scripts/iris_w10_build.py build hello_world --config release
python scripts/iris_w10_build.py build hello_world -p

# Step 9: Or use the full pipeline
python scripts/iris_w10_build.py all demo_apps/hello_world
# Runs: install → clone → build in sequence

# Step 10: Clean if needed
python iris_w1_build.py clean          # Remove build directory
python iris_w1_build.py clean --all    # Remove entire workspace (~2 GB)
```

### Result
[OK] Firmware ready for flashing to IRIS-W1 via MCU-Link, J-Link/J-Flash Lite (`west flash -r linkserver`),
or blhost for recovery. See [IRIS-W1-GettingStartedSDK/README.md](IRIS-W1-GettingStartedSDK/README.md)
for u-blox board files, calibration data and flash addresses.

---

## 5. IRIS-W10 (NXP RW612/RW610 / MCUXpresso SDK) — Windows/WSL2/Linux

### Prerequisites
- Python 3.10+, Git 2.25+
- CMake 3.30+, Ninja 1.12.1+
- Arm GNU Toolchain (`arm-none-eabi-gcc`)
- `ARMGCC_DIR` environment variable pointing at the toolchain root
- ~2 GB free disk space (board-targeted workspace)

> On Windows the [MCUXpresso Installer](https://github.com/nxp-mcuxpresso/vscode-for-mcux/wiki/Dependency-Installation)
> installs CMake, Ninja and Arm GCC in one step.

### Complete Build Workflow

```bash
# Step 1: Navigate to workspace
cd IRIS-W10-GettingStartedSDK

# Step 2: Check environment
python iris_w10_build.py doctor
# Output: Python [OK], Git [OK], West [OK], CMake [OK], Ninja [OK], Arm GCC [OK], workspace [FAIL] (not yet)
# Also reports whether ARMGCC_DIR is set

# Step 3: Install west and check remaining toolchain
python iris_w10_build.py install
# Runs: pip install -U west
# Reports: anything still missing + how to set ARMGCC_DIR

# Step 4: Set ARMGCC_DIR (one time, then reopen the terminal)
# Windows: setx ARMGCC_DIR "C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1"
# Linux:   export ARMGCC_DIR="/usr"

# Step 5: Initialise the SDK workspace (~2 GB, first time only)
python iris_w10_build.py clone
# Runs: west init -m https://github.com/nxp-mcuxpresso/mcuxsdk-manifests.git mcuxpresso-sdk
#       west update_board --set board rdrw612bga
# Fetches only the 63 repositories rdrw612bga needs, not the full ~7 GB SDK
# Use --full for the complete SDK, or --revision v25.09.00 to pin a release

# Step 6: List available examples
python iris_w10_build.py list
# Shows: demo_apps/hello_world, wifi_examples/wifi_cli, etc.

# Step 7: Build an example
python iris_w10_build.py build demo_apps/hello_world
# Runs: west build -b rdrw612bga examples/demo_apps/hello_world --toolchain armgcc --config debug
# Output: mcuxpresso-sdk/build/

# Bare names work too when unambiguous:
python iris_w10_build.py build hello_world

# Step 8: Release build / pristine rebuild
python iris_w10_build.py build hello_world --config release
python iris_w10_build.py build hello_world -p

# Step 9: Or use the full pipeline
python iris_w10_build.py all demo_apps/hello_world
# Runs: install → clone → build in sequence

# Step 10: Clean if needed
python iris_w10_build.py clean          # Remove build directory
python iris_w10_build.py clean --all    # Remove entire workspace (~2 GB)
```

### Result
[OK] Firmware ready for flashing to IRIS-W10 via MCU-Link, J-Link/J-Flash Lite (`west flash -r linkserver`),
or blhost for recovery. See [IRIS-W10-GettingStartedSDK/README.md](IRIS-W10-GettingStartedSDK/README.md)
for u-blox board files, calibration data and flash addresses.

---

## Side-by-Side Comparison

| Step | W50/W51 (TI) | W30 (Realtek) | W40 (ESP-IDF) | IRIS-W10 (NXP) |
|------|--------------|---------------|---------------|----------------|
| Clone | `clone` | `clone` | `clone` | `clone` |
| Install | `install` (info) | `install` (info) | `install` (real) | `install` (real) |
| Configure | `configure` | (automatic) | (automatic) | `ARMGCC_DIR` env var |
| Library Setup | `build-sdk` | (auto) | (auto) | (auto) |
| List | `list` | `list` | `list` | `list` |
| Build | `build <name>` | `build <name>` | `build <category>/<name>` | `build <category>/<name>` |
| Time | ~10-15 min (SDK) | ~5 min (example) | ~3 min (example) | ~5 min (example) |
| Output | `.out` (ELF) | `.axf` (ELF) | `.bin` (image) | `.elf` / `.bin` |
| Platform | Windows/WSL2/Linux | Linux/WSL2 only | Windows/WSL2/Linux | Windows/WSL2/Linux |
| Build system | CMake + Make | Make | CMake + idf.py | west + CMake + Ninja |

---

## Troubleshooting: What to Clean if Something Fails

### W50/W51
```bash
# Clean just the example
python nora_w50_w51_build.py build network_terminal --clean

# Rebuild SDK from scratch
python nora_w50_w51_build.py build-sdk --clean --toolchain ticlang

# Force reconfigure
rm imports.mak
python nora_w50_w51_build.py configure
```

### W30
```bash
# Clean just the example
python nora_w30_build.py clean hello_world

# Remove entire SDK and restart
python nora_w30_build.py clean --all
# Then: python nora_w30_build.py clone
```

### W40
```bash
# Clean just the example
python nora_w40_build.py clean get-started/hello_world

# Remove entire ESP-IDF and restart
python nora_w40_build.py clean --all
# Then: python nora_w40_build.py clone && python nora_w40_build.py install
```

### IRIS-W10
```bash
# Pristine rebuild of one example
python iris_w10_build.py build demo_apps/hello_world -p

# Remove the build directory
python iris_w10_build.py clean

# Remove entire west workspace and restart
python iris_w10_build.py clean --all
# Then: python iris_w10_build.py clone
```

---

## Quick Start Commands (Fastest Path)

### W50/W51 – Assume SDK already installed
```bash
cd ~/nora-w50-w51
python nora_w50_w51_build.py configure
python nora_w50_w51_build.py build-sdk --toolchain ticlang
python nora_w50_w51_build.py build network_terminal --toolchain ticlang
```

### W30 – Assume tools installed (apt)
```bash
cd ~/nora-w30
python3 nora_w30_build.py clone
python3 nora_w30_build.py build hello_world
```

### W40 – Assume tools installed (cmake, git, python)
```bash
cd ~/nora-w40
python nora_w40_build.py clone
python nora_w40_build.py install
# On Windows: .\esp-idf\export.ps1
# On Linux:   source esp-idf/export.sh
python nora_w40_build.py build get-started/hello_world
```

### IRIS-W10 – Assume ARMGCC_DIR set, tools installed
```bash
cd IRIS-W10-GettingStartedSDK
python iris_w10_build.py install
python iris_w10_build.py clone
python iris_w10_build.py build demo_apps/hello_world
```

---

## Expected Time Estimates

| Task | W50/W51 | W30 | W40 |
|------|---------|-----|-----|
| Clone SDK | 2-3 min | 1-2 min | 3-5 min |
| Install environment | (info only) | (info only) | 5-10 min |
| Build SDK/libraries | 10-15 min | (auto) | (auto) |
| Build first example | 2-3 min | 1-2 min | 2-3 min |
| Build second example | 2-3 min | 1-2 min | 2-3 min |
| **Total from scratch** | ~20-25 min | ~5-10 min | ~15-20 min |

---

## File Locations

### After Building

**W50/W51:**
```
~/nora-w50-w51/
├── wifi-examples/
│   ├── network_terminal/ticlang/Release/network_terminal.out   ← Firmware
│   └── ...
├── simplelink-wifi-sdk/
│   └── (SDK libraries)
└── imports.mak
```

**W30:**
```
~/nora-w30/
├── realtek-rtos-sdk/
│   ├── examples/hello_world/build/hello_world.axf              ← Firmware
│   ├── examples/wifi_sta/build/wifi_sta.axf                    ← Firmware
│   └── ...
└── .nora_w30_build.linux.json
```

**W40:**
```
~/nora-w40/
├── esp-idf/
│   ├── examples/get-started/hello_world/build/hello_world.bin  ← Firmware
│   ├── examples/network/static_ip/build/static_ip.bin          ← Firmware
│   └── ...
└── .nora_w40_build.{windows|wsl|linux}.json
```

---

## Next Steps: Flashing

### W50/W51 → XDS110 Debug Connector or UART Bootloader
```bash
# Using Code Composer Studio or CCS command-line tools
# See: README.md in NORA-W50-W51-GettingStartedSDK
```

### W30 → UART with Realtek Flash Tool
```bash
# Using Realtek's flash tool (ameba_image_tool or ImageTool.exe)
# See: README.md in NORA-W30-GettingStartedSDK
```

### W40 → USB JTAG or UART Bootloader
```bash
# Using esptool.py
esptool.py -p /dev/ttyUSB0 write_flash 0x0 hello_world.bin
# Or: esptool.py -p COM5 write_flash 0x0 hello_world.bin (Windows)
# See: README.md in NORA-W40-GettingStartedSDK
```
