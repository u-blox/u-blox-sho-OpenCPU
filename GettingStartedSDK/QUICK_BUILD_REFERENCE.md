# Quick Build Cheatsheet — All Variants

Visual quick reference for building NORA-W50/W51, W30, W40, IRIS-W10 firmware.

**Status:** ✅ IRIS-W10 & NORA-W50/W51 verified working (2026-09-28)

---

## Fastest Path: 3 Commands Each

### **IRIS-W10** ✅ VERIFIED (NXP RW612/RW610)
```bash
cd GettingStartedSDK
export ARMGCC_DIR="/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
python scripts/iris_w10_build.py build demo_apps/hello_world
# Result: hello_world.elf (258 KB), hello_world.bin (29 KB) ✅ VERIFIED
# Time: ~3 min (if SDK already cloned)
# Platform: Windows (Git Bash), WSL2, Linux
```

### **NORA-W50/W51** ✅ VERIFIED (TI CC35XX)
```bash
cd GettingStartedSDK
python scripts/nora_w50_w51_build.py doctor
python scripts/nora_w50_w51_build.py build ble_wifi_provisioning
# Result: ble_wifi_provisioning.out ✅ VERIFIED
# Time: ~2-3 min
# Platform: Windows (Git Bash), WSL2, Linux
```

### **NORA-W40** 🟡 READY (Espressif ESP32-C6)
```bash
cd GettingStartedSDK
python scripts/nora_w40_build.py all hello_world
# Result: hello_world.elf / hello_world.bin
# Time: ~15-20 min (includes ESP-IDF install)
# Platform: Windows, WSL2, Linux
# Status: ESP-IDF clone present, needs install
```

### **NORA-W30** 🟡 READY (Realtek RTL872x - requires WSL2)
```bash
cd GettingStartedSDK
wsl -d Ubuntu-24.04 bash -c "cd /mnt/e/u-blox/u-blox-sho-OpenCPU/GettingStartedSDK && \
  python scripts/nora_w30_build.py all wlan_sample"
# Result: wlan_sample.bin
# Time: ~10 min (includes SDK clone)
# Platform: Windows (via WSL2), Linux, macOS (via WSL2)
# Status: Requires SDK clone from GitHub
```

---

## Command Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              BUILD COMMAND REFERENCE                                                │
├──────────────┬──────────────┬──────────────┬────────────────┬────────────────────────────────────────┤
│ Operation    │ W50/W51 (TI) │ W30 (Realtek)│ W40 (ESP-IDF)  │ IRIS-W10 (NXP)                        │
├──────────────┼──────────────┼──────────────┼────────────────┼────────────────────────────────────────┤
│ Check env    │ doctor       │ doctor       │ doctor         │ doctor                                │
│ Get SDK      │ (auto)       │ clone        │ clone          │ clone (if needed)                     │
│ Setup env    │ (auto)       │ (auto)       │ install        │ ARMGCC_DIR env var                    │
│ List examples│ list         │ list         │ list           │ list                                  │
│ Build one    │ build NAME   │ build NAME   │ build NAME     │ build CATEGORY/NAME                   │
│ Clean one    │ clean NAME   │ clean NAME   │ clean NAME     │ clean NAME                            │
│ Clean all    │ clean --all  │ clean --all  │ clean --all    │ clean --all                           │
│ All-in-one   │ all NAME     │ all NAME     │ all NAME       │ all CATEGORY/NAME                     │
└──────────────┴──────────────┴──────────────┴────────────────┴────────────────────────────────────────┘
```

---

## Platform Support & Status

```
✅ IRIS-W10 (NXP RW612/RW610)
   Status: VERIFIED BUILD (2026-09-28)
   Build time: 3 min (hello_world.elf 258 KB, hello_world.bin 29 KB)
   Platforms: Windows ✅, WSL2 ✅, Linux ✅
   
✅ NORA-W50/W51 (TI CC35XX)
   Status: VERIFIED BUILD (2026-09-28)
   Build time: 2-3 min (ble_wifi_provisioning.out generated)
   Platforms: Windows ✅, WSL2 ✅, Linux ✅
   
🟡 NORA-W40 (Espressif ESP32-C6)
   Status: READY (needs ESP-IDF install)
   Build time: 15-20 min (includes install)
   Platforms: Windows ✅, WSL2 ✅, Linux ✅
   
🟡 NORA-W30 (Realtek RTL872x)
   Status: READY (needs WSL2 SDK clone)
   Build time: 10 min (includes clone)
   Platforms: Windows (via WSL2) ✅, Linux ✅

┌─────────────────────┬──────────────────────────────────────────────────┐
│ IRIS-W10 (NXP)      │ Setup: 10-15 min  │  Build: ~5 min each   │ 20 min total
│ Platforms: Win/WSL2/Linux                                           │
│ Status: ✅ Tooling + workspace init verified on Windows 11, Ubuntu. │
└─────────────────────┴──────────────────────────────────────────────────┘


```

---

## Workspace Layout

Create one folder per variant (recommended):

```
~/dev/
├── nora-w50-w51/              # NORA-W50/W51 (TI)
│   ├── nora_w50_w51_build.py
│   ├── simplelink-wifi-sdk/
│   ├── wifi-examples/
│   └── imports.mak
│
├── nora-w30/                  # NORA-W30 (Realtek) — Linux/WSL2 only
│   ├── nora_w30_build.py
│   ├── realtek-rtos-sdk/
│   └── .nora_w30_build.linux.json
│
├── nora-w40/                  # NORA-W40 (ESP-IDF)
│   ├── nora_w40_build.py
│   ├── esp-idf/
│   └── .nora_w40_build.windows.json  (or .wsl/.linux)
│
└── iris-w10/                  # IRIS-W10 (NXP RW612/RW610)
    ├── iris_w10_build.py
    ├── mcuxpresso-sdk/        # west workspace (manifests/ + mcuxsdk/)
    └── .iris_w10_build.windows.json  (or .wsl/.linux)
```

---

## Example: Building Same App on All Three Platforms

### "Hello World" on Each Platform

**W50/W51:**
```bash
cd ~/dev/nora-w50-w51
python nora_w50_w51_build.py build uart2echo --toolchain ticlang
# Output: uart2echo.out (354 KB) — sends "Hello World" on UART
```

**W30:**
```bash
cd ~/dev/nora-w30
python3 nora_w30_build.py build hello_world
# Output: hello_world.axf — prints "Hello World" via UART
```

**W40:**
```bash
cd ~/dev/nora-w40
source esp-idf/export.sh  # or .\esp-idf\export.ps1 on Windows
python nora_w40_build.py build get-started/hello_world
# Output: hello_world.bin — prints "Hello World" via UART
```

---

## Troubleshooting Quick Fixes

| Problem | W50/W51 | W30 | W40 |
|---------|---------|-----|-----|
| Tool not found | `doctor` → see README | `doctor` → see README | `doctor` → see README |
| Build fails | `--clean` flag | `clean NAME` | `clean NAME` |
| Start over | Manual clean | `clean --all` | `clean --all` |
| Wrong paths | `configure` | (auto) | (auto) |
| SDK too old | `clone --update` | Re-clone | Re-clone |
| Environment stale | Restart shell | Restart shell | Re-source export.sh/ps1 |

---

## File Output Locations

After building:

**W50/W51:**
```
wi-fi-examples/network_terminal/ticlang/Release/
├── network_terminal.out        ← Firmware ELF (main output)
├── network_terminal.map        ← Symbol map
└── ... (object files)
```

**W30:**
```
realtek-rtos-sdk/examples/hello_world/build/
├── hello_world.axf             ← Firmware ELF (main output)
├── hello_world.map
└── ... (object files)
```

**W40:**
```
esp-idf/examples/get-started/hello_world/build/
├── hello_world.bin             ← Firmware image (main output)
├── hello_world.elf             ← ELF with debug symbols
├── hello_world.map
└── ... (build artifacts)
```

---

## Next: Flashing to Hardware

### NORA-W50/W51
```bash
# Using Code Composer Studio, CCS command-line, or XDS110 Emulation Tool
# USB XDS110 debugger connection required
# See: NORA-W50-W51-GettingStartedSDK/README.md
```

### NORA-W30
```bash
# Using Realtek Flash Tool (Windows) or command-line equivalent
# UART connection required (3.3V, 38400/115200 baud)
# See: NORA-W30-GettingStartedSDK/README.md
```

### NORA-W40
```bash
# Using esptool.py (Python tool)
python -m esptool write_flash 0x0 hello_world.bin

# Or on Windows:
python -m esptool -p COM5 write_flash 0x0 hello_world.bin

# See: NORA-W40-GettingStartedSDK/README.md
```

---

## Performance Comparison

```
                 First Build    Rebuild    Clean
W50/W51 (TI)     15-20 min      2-3 min    0.5 min
W30 (Realtek)    5 min          1-2 min    <0.1 min
W40 (ESP-IDF)    15 min         2-3 min    0.5 min

Total from scratch (all 3):  ~40 minutes  (parallel: ~20 min)
Total rebuild (all 3):        ~7 minutes  (parallel: ~3 min)
```

---

## Environment Variables (When Needed)

**W50/W51:**
```bash
# If configure fails, set explicitly:
export SYSCONFIG_TOOL=/opt/ti/sysconfig/bin/sysconfig_cli.sh
export TICLANG_ARMCOMPILER=/opt/ti/arm_compiler
export GCC_ARMCOMPILER=/opt/gcc-arm-none-eabi
export CMAKE=/usr/bin/cmake
```

**W30:**
```bash
# Realtek SDK uses environment detection — usually automatic
# If issues, set:
export SDK_ROOT=/path/to/realtek-rtos-sdk
export ARM_TOOLCHAIN_PATH=/usr  # where arm-none-eabi-gcc lives
```

**W40:**
```bash
# ESP-IDF setup is self-contained in export.sh / export.ps1
# Source that, then build
source esp-idf/export.sh  # Linux/WSL2
.\esp-idf\export.ps1      # Windows PowerShell
```

**IRIS-W10:**
```bash
# Required — the MCUXpresso build system locates the compiler through this.
# Point at the toolchain ROOT (the folder containing bin/), not bin/ itself.
export ARMGCC_DIR=/usr                                    # Linux/WSL2
setx ARMGCC_DIR "C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1"   # Windows
# (Then restart terminal)
```
```

---

## Disk Space Requirements

| Variant | SDK Size | Build Size | Total |
|---------|----------|-----------|-------|
| W50/W51 | 500 MB | 200 MB | ~700 MB |
| W30 | 100 MB | 50 MB | ~150 MB |
| W40 | 1.2 GB | 500 MB | ~1.7 GB |
| IRIS-W1 | 2 GB (board-targeted) | 300 MB | ~2.3 GB |
| **All four** | - | - | **~4.9 GB** |

> IRIS-W1 `clone --full` fetches the complete MCUXpresso SDK instead (~7–8 GB).

---

## For More Details

- **W50/W51:** See [NORA-W50-W51-GettingStartedSDK/README.md](NORA-W50-W51-GettingStartedSDK/README.md)
- **W30:** See [NORA-W30-GettingStartedSDK/README.md](NORA-W30-GettingStartedSDK/README.md)
- **W40:** See [NORA-W40-GettingStartedSDK/README.md](NORA-W40-GettingStartedSDK/README.md)
- **IRIS-W10:** See [IRIS-W10-GettingStartedSDK/README.md](IRIS-W10-GettingStartedSDK/README.md)
- **All Variants:** See [BUILD_ALL_EXAMPLES.md](BUILD_ALL_EXAMPLES.md)
