# Building NORA-W50-W51, W30, W40, IRIS-W10, NORA-B20-B21-B22 and ALMA-B20-B21 From Scratch

Complete examples showing how to build firmware for all four u-blox Open CPU module families from initial setup to working examples.

---

## 1. NORA-W50-W51 (TI SimpleLink WiFi SDK) — Windows/WSL2/Linux

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
# Runs: configure -> build-sdk -> build in sequence

# Step 10: Clean if build fails
python nora_w50_w51_build.py build-sdk --clean  # Clean SDK rebuild
python nora_w50_w51_build.py build --clean      # Clean example rebuild
```

### Result
[OK] Firmware image ready for flashing to NORA-W50-W51 via XDS110 or serial bootloader

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
# Step 1: Navigate to getting-started-sdk workspace
cd getting-started-sdk

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
# Output: sdks/ameba-rtos-d/main/.../project_hp/asdk/image/

# Step 7: Or use full pipeline
python3 nora_w30_build.py all hello_world
# Runs: clone -> build in sequence

# Step 8: Build another example
python3 nora_w30_build.py build wifi_sta
# Output: sdks/ameba-rtos-d/main/.../project_hp/asdk/image/

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
# Step 1: Navigate to getting-started-sdk workspace
cd getting-started-sdk

# Step 2: Activate shared virtual environment
source .venv/bin/activate              # Linux/WSL2
# or on Windows: .venv\Scripts\activate

# Step 3: Check environment
python scripts/nora_w40_build.py doctor
# Output: Python [OK], Git [OK], CMake [OK], Make [OK], ESP-IDF [FAIL] (not cloned yet)

# Step 4: Clone ESP-IDF v6.2 (first time only, ~200MB)
python scripts/nora_w40_build.py clone
# Clones: https://github.com/espressif/esp-idf.git (v6.2)
# Creates: sdks/esp-idf/master/ (add --revision v5.5.1 for a release)
# Saves: config in modules/nora-w40/config/build.{platform}.json

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
- Arm GNU Toolchain (`arm-none-eabi-gcc`); found automatically, `ARMGCC_DIR` overrides it
- ~2 GB free disk space (board-targeted workspace)

> On Windows the [MCUXpresso Installer](https://github.com/nxp-mcuxpresso/vscode-for-mcux/wiki/Dependency-Installation)
> installs CMake, Ninja and Arm GCC in one step.

### Complete Build Workflow

```bash
# Step 1: Navigate to workspace
cd getting-started-sdk

# Step 2: Check environment
python scripts/iris_w10_build.py doctor
# Output: Python [OK], Git [OK], West [OK], CMake [OK], Ninja [OK], Arm GCC [OK], workspace [FAIL] (not yet)
# Also reports which Arm GNU toolchain it will use as ARMGCC_DIR

# Step 3: Install west and check remaining toolchain
python scripts/iris_w10_build.py install
# Runs: pip install -U west
# Reports: anything still missing

# Step 4: Initialise the SDK workspace (~2 GB, first time only)
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
# Output: sdks/mcuxpresso-sdk/main/build/

# Bare names work too when unambiguous:
python scripts/iris_w10_build.py build hello_world

# Step 8: Release build / pristine rebuild
python scripts/iris_w10_build.py build hello_world --config release
python scripts/iris_w10_build.py build hello_world -p

# Step 9: Or use the full pipeline
python scripts/iris_w10_build.py all demo_apps/hello_world
# Runs: install -> clone -> build in sequence

# Step 10: Clean if needed
python scripts/iris_w10_build.py clean          # Remove build directory
python scripts/iris_w10_build.py clean --all    # Remove entire workspace (~2 GB)
```

### Result
[OK] Firmware ready for flashing to IRIS-W10 via MCU-Link, J-Link/J-Flash Lite
(`west flash -r linkserver`), or blhost for recovery. See
[iris_w10_README.md](iris_w10_README.md) for u-blox board files, calibration
data and flash addresses.

---

## 5. NORA-B20-B21-B22 (Nordic nRF54L / nRF Connect SDK) — Windows/WSL2/Linux/macOS

### Prerequisites
- Python 3.10+, Git 2.25+
- CMake 3.20+, Ninja
- `west`, and a Zephyr SDK or Arm GNU toolchain
- `nrfutil` for flashing (J-Link also works)
- ~10 GB free disk space for the NCS workspace

> The quickest route on every platform is
> [nRF Connect for Desktop](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop)
> and its Toolchain Manager, which installs all of the above in one step.

### Complete Build Workflow

```bash
cd getting-started-sdk

# Step 1: Check environment
./ubx-sdk.sh nora-b20-b21-b22 --doctor
# Reports git, cmake, ninja, west, toolchain, nrfutil and the NCS workspace
# Lists every NCS workspace found and which one will be used

# Step 2: Fetch the nRF Connect SDK (v3.4.1, ~15 GB, first time only)
./ubx-sdk.sh nora-b20-b21-b22 --clone
# Checks free space, then runs: west init -m https://github.com/nrfconnect/sdk-nrf --mr v3.4.1
#                               west update
# Lands in C:\ncs\v3.4.1 (Windows) or ~/ncs/v3.4.1 (Linux)

# Step 3: Install the Zephyr Python requirements
./ubx-sdk.sh nora-b20-b21-b22 --install

# Step 4: List available samples
./ubx-sdk.sh nora-b20-b21-b22 --list
# Searches nrf/samples, nrf/applications and zephyr/samples

# Step 5: Build
./ubx-sdk.sh nora-b20-b21-b22 --build hello_world
# Runs: west build -b ubx_evknorab2/nrf54l15/cpuapp <sample>
# Output: <ncs workspace>/build/hello_world/zephyr/zephyr.{elf,hex,bin}

# Step 6: Target a different module variant
./ubx-sdk.sh nora-b20-b21-b22 --build hello_world -- --board ubx_evknorab2/nrf54l10/cpuapp

# Step 7: Flash and watch the output
./ubx-sdk.sh nora-b20-b21-b22 --flash --log
# Both EVKs carry a SEGGER J-LINK-OB, so no external probe is needed

# Step 8: Clean
./ubx-sdk.sh nora-b20-b21-b22 --clean
./ubx-sdk.sh nora-b20-b21-b22 --clean-all    # remove the NCS workspace entirely
```

### Matter
Matter ships inside the nRF Connect SDK, so `--clone` fetches the same NCS
workspace as the plain SDK flow and nothing extra is downloaded:

```bash
./ubx-matter.sh nora-b20-b21-b22 --list                      # the nrf/samples/matter apps
./ubx-matter.sh nora-b20-b21-b22 --build light_bulb --flash --log
```

NCS builds natively on Windows, so these never hop into WSL2. `ubx-sdk` can
still build the same sample by its full path (`--build matter/light_bulb`).

### Result
[OK] Zephyr firmware ready for NORA-B20x/B21x/B22x. See
[nora_b20_b21_b22_README.md](nora_b20_b21_b22_README.md) for the full variant and board-target
matrix.

---

## 6. ALMA-B20-B21 (Nordic nRF54LM20 / nRF Connect SDK) — Windows/WSL2/Linux/macOS

Same toolchain and driver as NORA-B20-B21-B22. Two differences matter:

- ALMA-B20-B21 is **under development**. There is no `ubx_evkalmab2` board
  definition in Zephyr or NCS yet, so builds target Nordic's nRF54LM20 DK.
  Pinout, antenna path and power rails will not match a real ALMA-B20-B21 design.
- The nRF54LM20B variant (ALMA-B211/B216) carries the Axon NPU. Its toolchain
  is distributed separately by Nordic and is not driven by this SDK.

```bash
cd getting-started-sdk

./ubx-sdk.sh alma-b20-b21 --doctor
./ubx-sdk.sh alma-b20-b21 --clone --install
./ubx-sdk.sh alma-b20-b21 --list

# Default board: nrf54lm20dk/nrf54lm20a/cpuapp (ALMA-B201/B206)
./ubx-sdk.sh alma-b20-b21 --build hello_world

# B-variant with the Axon NPU (ALMA-B211/B216)
./ubx-sdk.sh alma-b20-b21 --build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp

./ubx-sdk.sh alma-b20-b21 --flash --log
```

NORA-B20-B21-B22 and ALMA-B20-B21 share `scripts/nordic_ncs_build.py`, so one NCS workspace
can serve both.

### Result
[OK] Zephyr firmware for bring-up on the Nordic DK. See
[alma_b20_b21_README.md](alma_b20_b21_README.md) for known limitations.

---

## Side-by-Side Comparison

All targets share the same launcher flags; the table shows what each flag
actually does per target.

| Step | nora-w50-w51 (TI) | nora-w30 (Realtek) | nora-w40 (ESP-IDF) | iris-w10 (NXP) | nora-b20-b21-b22 / alma-b20-b21 (Nordic) |
|------|--------------|--------------------|--------------------|----------------|----------------------------|
| `--clone` | examples + SDK | ameba-rtos-d | esp-idf | west workspace | NCS west workspace |
| `--install` | info only | info only | real (toolchain) | real (west) | Zephyr requirements |
| Configure | automatic | automatic | automatic | automatic (Arm GNU detected) | Zephyr SDK autodetect |
| `--build-sdk` | required once | n/a | n/a | n/a | n/a |
| `--build` | `<name>` | `<name>` | `<category>/<name>` | `<category>/<name>` | `<name>` or path |
| `--flash` | yes | n/a | yes | yes | yes |
| Output | `.out` (ELF) | `.bin` | `.elf` / `.bin` | `.elf` / `.bin` | `zephyr.elf/.hex/.bin` |
| Platform | Win/WSL2/Linux | Linux/WSL2 only | Win/WSL2/Linux | Win/WSL2/Linux | Win/WSL2/Linux/macOS |
| Build system | CMake + Make | Make | CMake + idf.py | west + CMake + Ninja | west + CMake + Ninja |

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

Assuming the host tools are already installed (`--doctor` tells you), each
target is one line from the `getting-started-sdk` folder:

```bash
./ubx-sdk.sh nora-w50-w51   --clone --build-sdk --build network_terminal
./ubx-sdk.sh nora-w30  --clone --build project_hp
./ubx-sdk.sh nora-w40  --clone --install --build hello_world --flash --log
./ubx-sdk.sh iris-w10  --clone --install --build demo_apps/hello_world --flash --log
./ubx-sdk.sh nora-b20-b21-b22   --clone --install --build hello_world --flash --log
./ubx-sdk.sh alma-b20-b21   --clone --install --build hello_world
```

NORA-W30 is Linux-only; run it from Windows anyway and the launcher hops
into WSL2 by itself.

---

## Expected Time Estimates

| Task | NORA-W50-W51 | NORA-W30 | NORA-W40 | IRIS-W10 | NORA-B20-B21-B22 / ALMA-B20-B21 |
|------|---------|----------|----------|----------|-------------------|
| Clone SDK | 2-3 min | 1-2 min | 3-5 min | 10-15 min | 15-25 min |
| Install environment | (info only) | (info only) | 5-10 min | 1 min | 2-5 min |
| Build SDK/libraries | 10-15 min | (auto) | (auto) | (auto) | (auto) |
| Build first example | 2-3 min | 5 min | 2-3 min | 3-5 min | 2-4 min |
| Build second example | 2-3 min | 5 min | 2-3 min | 1-2 min | 1-2 min |
| **Total from scratch** | ~20-25 min | ~10-15 min | ~15-20 min | ~20 min | ~25-35 min |

Times assume a reasonable connection. An existing NCS v3.x workspace (for
example from nRF Connect for Desktop in `C:\ncs`) removes the clone step
entirely for the Nordic targets.

---

## File Locations

### After Building

**W50/W51:**
```
~/nora-w50-w51/
├── wifi-examples/
│   ├── network_terminal/ticlang/Release/network_terminal.out   <- Firmware
│   └── ...
├── simplelink-wifi-sdk/
│   └── (SDK libraries)
└── imports.mak
```

**W30:**
```
getting-started-sdk/
├── sdks/ameba-rtos-d/main/
│   └── project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp/asdk/image/   <- Firmware
└── modules/nora-w30/config/build.{wsl|linux}.json
```

**W40:**
```
getting-started-sdk/
├── sdks/esp-idf/master/
│   ├── examples/get-started/hello_world/build/hello_world.bin  <- Firmware
│   ├── examples/network/static_ip/build/static_ip.bin          <- Firmware
│   └── ...
└── modules/nora-w40/config/build.{windows|wsl|linux}.json
```

---

## Next Steps: Flashing

### W50/W51 -> XDS110 Debug Connector or UART Bootloader
```bash
# Using Code Composer Studio or CCS command-line tools
# See: docs/nora_w50_w51_README.md
```

### W30 -> UART with Realtek Flash Tool
```bash
# Using Realtek's flash tool (ameba_image_tool or ImageTool.exe)
# See: docs/nora_w30_README.md
```

### W40 -> USB JTAG or UART Bootloader
```bash
# Using esptool.py
esptool.py -p /dev/ttyUSB0 write_flash 0x0 hello_world.bin
# Or: esptool.py -p COM5 write_flash 0x0 hello_world.bin (Windows)
# See: docs/nora_w40_README.md
```
