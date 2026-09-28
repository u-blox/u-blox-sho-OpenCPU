# Building NORA-W50/W51, W30, and W40 From Scratch

Complete examples showing how to build firmware for all three u-blox NORA modules from initial setup to working examples.

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
cd ~/ti-w5    # or ./workspace on Windows/WSL2

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
# Output: ~/ti-w5/wifi-examples/network_terminal/ticlang/Release/network_terminal.out (17 MB)

# Step 9: Or do entire pipeline in one command
python nora_w50_w51_build.py all network_terminal --toolchain ticlang
# Runs: configure → build-sdk → build in sequence

# Step 10: Clean if build fails
python nora_w50_w51_build.py build-sdk --clean  # Clean SDK rebuild
python nora_w50_w51_build.py build --clean      # Clean example rebuild
```

### Result
✅ Firmware image ready for flashing to NORA-W50/W51 via XDS110 or serial bootloader

---

## 2. NORA-W30 (Realtek RTL872x RTOS) — Linux/WSL2 Only

### Prerequisites
- Linux (native) OR WSL2 (Ubuntu recommended)
- arm-none-eabi-gcc (sudo apt install arm-none-eabi-gcc)
- GNU Make
- Git
- Python 3.8+

**Note:** Windows native/Cygwin not recommended

### Complete Build Workflow

```bash
# Step 1: Navigate to workspace (Linux/WSL2 only)
cd ~/nora-w30-workspace
# or on WSL2: ~/nora-w30 (keep in Linux filesystem for speed!)

# Step 2: Check environment
python3 nora_w30_build.py doctor
# Output: Python ✅, Git ✅, Make ✅, Arm GCC ✅

# Step 3: If tools missing, install them
python3 nora_w30_build.py install
# Displays: sudo apt install arm-none-eabi-gcc make git python3

# Step 4: Clone Realtek RTOS SDK
python3 nora_w30_build.py clone
# Clones: https://github.com/ambiot/ameba-rtos.git (Ameba-RTOS)
# Creates: realtek-rtos-sdk/ folder

# Step 5: List available examples
python3 nora_w30_build.py list
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
✅ Firmware ELF ready for flashing to NORA-W30 via UART with Realtek flash tool

---

## 3. NORA-W40 (ESP32-S3 + ESP-IDF) — Windows/WSL2/Linux

### Prerequisites
- Python 3.9+ (or bundled with ESP-IDF)
- Git
- CMake 3.16+
- GNU Make
- Windows: MSYS2, Visual Studio Build Tools, or use WSL2
- Linux/WSL2: standard build tools

### Complete Build Workflow

```bash
# Step 1: Navigate to workspace
cd ~/nora-w40-workspace
# or anywhere with ~600MB free space for ESP-IDF

# Step 2: Check environment
python nora_w40_build.py doctor
# Output: Python ✅, Git ✅, CMake ✅, Make ✅, ESP-IDF ❌ (not yet)

# Step 3: Clone ESP-IDF (first time only, ~200MB)
python nora_w40_build.py clone
# Clones: https://github.com/espressif/esp-idf.git (full v5.x)
# Creates: esp-idf/ folder
# Saves: esp-idf path to .nora_w40_build.{windows|wsl|linux}.json

# Step 4: Install ESP-IDF environment
python nora_w40_build.py install
# Windows: Runs esp-idf/install.bat
#   - Sets up Python venv
#   - Downloads ESP32-S3 toolchain (~600MB)
#   - Installs build dependencies
# 
# Linux/WSL2: Runs esp-idf/install.sh
#   - Same setup as Windows

# Step 5: List available examples
python nora_w40_build.py list
# Shows: get-started/hello_world, get-started/blink, network/http_server,
#        bluetooth/ble_provisioning, storage/nvs_rw_value, etc.

# Step 6: Build an example (MUST source environment first!)
# Windows:
#   In PowerShell at esp-idf/: .\export.ps1
#   Then: cd NORA-W40-GettingStartedSDK && python nora_w40_build.py build get-started/hello_world
#
# Linux/WSL2:
#   source esp-idf/export.sh
#   cd NORA-W40-GettingStartedSDK && python nora_w40_build.py build get-started/hello_world

# Output: esp-idf/examples/get-started/hello_world/build/hello_world.elf (~500KB)
#         Also: hello_world.bin (firmware image)

# Step 7: Build another example
python nora_w40_build.py build network/static_ip
# Output: esp-idf/examples/network/static_ip/build/static_ip.bin

# Step 8: Or use full pipeline (after environment sourced)
python nora_w40_build.py all get-started/hello_world
# Runs: clone → install → build in sequence
# (Note: Must be in ESP-IDF environment first)

# Step 9: Clean if needed
python nora_w40_build.py clean get-started/hello_world   # Clean example build
python nora_w40_build.py clean --all                      # Remove entire ESP-IDF (~1.2GB)
```

### Result
✅ Firmware BIN ready for flashing to NORA-W40 via esptool.py or USB JTAG

---

## Side-by-Side Comparison

| Step | W50/W51 (TI) | W30 (Realtek) | W40 (ESP-IDF) |
|------|--------------|---------------|---------------|
| Clone | `clone` | `clone` | `clone` |
| Install | `install` (info) | `install` (info) | `install` (real) |
| Configure | `configure` | (automatic) | (automatic) |
| Library Setup | `build-sdk` | (auto) | (auto) |
| List | `list` | `list` | `list` |
| Build | `build <name>` | `build <name>` | `build <category>/<name>` |
| Time | ~10-15 min (SDK) | ~5 min (example) | ~3 min (example) |
| Output | `.out` (ELF) | `.axf` (ELF) | `.bin` (image) |
| Platform | Windows/WSL2/Linux | Linux/WSL2 only | Windows/WSL2/Linux |

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

---

## Quick Start Commands (Fastest Path)

### W50/W51 – Assume SDK already installed
```bash
cd ~/ti-w5
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
~/ti-w5/
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
