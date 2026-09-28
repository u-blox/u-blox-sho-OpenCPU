# Quick Build Cheatsheet — All Three NORA Variants

Visual quick reference for building NORA-W50/W51, W30, and W40 firmware.

---

## Fastest Path: 3 Commands Each

### **NORA-W50/W51** (TI CC35x1E)
```bash
cd ~/ti-w5
python nora_w50_w51_build.py configure
python nora_w50_w51_build.py build-sdk --toolchain ticlang
python nora_w50_w51_build.py build network_terminal --toolchain ticlang
# Result: ~/ti-w5/wifi-examples/network_terminal/ticlang/Release/network_terminal.out
# Time: ~15-20 min
# Platform: Windows, WSL2, Linux
```

### **NORA-W30** (Realtek RTL872x)
```bash
cd ~/nora-w30
python3 nora_w30_build.py clone
python3 nora_w30_build.py build hello_world
# Result: realtek-rtos-sdk/examples/hello_world/build/hello_world.axf
# Time: ~5 min
# Platform: Linux or WSL2 only
```

### **NORA-W40** (ESP32-S3 + ESP-IDF)
```bash
cd ~/nora-w40
python nora_w40_build.py clone
python nora_w40_build.py install
# [Windows] .\esp-idf\export.ps1  OR  [Linux] source esp-idf/export.sh
python nora_w40_build.py build get-started/hello_world
# Result: esp-idf/examples/get-started/hello_world/build/hello_world.bin
# Time: ~15 min (includes install)
# Platform: Windows, WSL2, Linux
```

---

## Command Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BUILD COMMAND REFERENCE                         │
├──────────────┬──────────────┬──────────────┬──────────────────────────────┤
│ Operation    │ W50/W51 (TI) │ W30 (Realtek)│ W40 (ESP-IDF)                │
├──────────────┼──────────────┼──────────────┼──────────────────────────────┤
│ Check env    │ doctor       │ doctor       │ doctor                       │
│ Get SDK      │ clone        │ clone        │ clone                        │
│ Setup env    │ install      │ install      │ install                      │
│ Config tools │ configure    │ (auto)       │ (auto)                       │
│ Build libs   │ build-sdk    │ (auto)       │ (auto)                       │
│ List examples│ list         │ list         │ list                         │
│ Build one    │ build NAME   │ build NAME   │ build CAT/NAME               │
│ Clean one    │ --clean flag │ clean NAME   │ clean NAME                   │
│ Clean all    │ (manual)     │ clean --all  │ clean --all                  │
│ All-in-one   │ all NAME     │ all NAME     │ all CAT/NAME*                │
└──────────────┴──────────────┴──────────────┴──────────────────────────────┘
* W40 requires environment sourced first
```

---

## Platform Support & Setup Time

```
┌─────────────────────┬──────────────────────────────────────────────────┐
│ NORA-W50/W51 (TI)   │ Setup: 20-30 min  │  Build: 2-3 min each  │ 25 min total
│ Platforms: Win/WSL2/Linux                                           │
│ Status: ✅ Fully tested on Windows 11, Ubuntu 22.04, WSL2           │
└─────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────┬──────────────────────────────────────────────────┐
│ NORA-W30 (Realtek)  │ Setup: 2-5 min    │  Build: 1-2 min each  │  8 min total
│ Platforms: Linux / WSL2 (Windows not recommended)                  │
│ Status: ✅ Fully tested on Ubuntu 22.04, WSL2 with Ubuntu 22.04    │
└─────────────────────┴──────────────────────────────────────────────────┘

┌─────────────────────┬──────────────────────────────────────────────────┐
│ NORA-W40 (ESP-IDF)  │ Setup: 10-15 min  │  Build: 2-3 min each  │ 18 min total
│ Platforms: Win/WSL2/Linux (all equal quality)                      │
│ Status: ✅ Fully tested on Windows 11, Ubuntu 22.04, WSL2          │
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
└── nora-w40/                  # NORA-W40 (ESP-IDF)
    ├── nora_w40_build.py
    ├── esp-idf/
    └── .nora_w40_build.windows.json  (or .wsl/.linux)
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

---

## Disk Space Requirements

| Variant | SDK Size | Build Size | Total |
|---------|----------|-----------|-------|
| W50/W51 | 500 MB | 200 MB | ~700 MB |
| W30 | 100 MB | 50 MB | ~150 MB |
| W40 | 1.2 GB | 500 MB | ~1.7 GB |
| **All Three** | - | - | **~2.6 GB** |

---

## For More Details

- **W50/W51:** See [NORA-W50-W51-GettingStartedSDK/README.md](NORA-W50-W51-GettingStartedSDK/README.md)
- **W30:** See [NORA-W30-GettingStartedSDK/README.md](NORA-W30-GettingStartedSDK/README.md)
- **W40:** See [NORA-W40-GettingStartedSDK/README.md](NORA-W40-GettingStartedSDK/README.md)
- **All Three:** See [BUILD_ALL_THREE_EXAMPLES.md](BUILD_ALL_THREE_EXAMPLES.md)
