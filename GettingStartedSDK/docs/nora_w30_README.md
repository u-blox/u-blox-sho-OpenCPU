# NORA-W30 Getting Started Guide

## Overview

NORA-W30 modules are based on the **Realtek RTL872x** SoC with Wi-Fi 6 (802.11ax) and Bluetooth LE 5.3. This guide covers building and deploying firmware using the **Realtek RTOS SDK** (or Ameba-RTOS).

**Key Features:**
- Single-core Cortex-M4 @ 200 MHz
- 2.4 GHz Wi-Fi 6 + Bluetooth LE 5.3
- 2 MB internal flash, up to 16 MB external flash
- Excellent Linux support; Windows requires WSL2 or Cygwin

**SDK:** Realtek RTOS / Ameba-RTOS (latest)  
**Platforms:** Linux (native), WSL2 (recommended for Windows)  
**Build System:** GNU Make  
**Toolchain:** arm-none-eabi-gcc

---

## Prerequisites

### Linux (Ubuntu/Debian) — Recommended

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-pip \
  git build-essential \
  gcc-arm-none-eabi \
  libusb-1.0-0 udev
```

Grant serial port access:
```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
# Log out and back in to apply group changes
```

### WSL2 (Windows via Ubuntu)

Install WSL2:
```powershell
wsl --install
```

Then use Linux setup above (same commands in WSL2 Ubuntu).

### Windows (Cygwin) — Not Recommended

Cygwin setup for Realtek SDK is complex and error-prone. Use **WSL2 instead**.

If you must use Cygwin:
1. Install Cygwin 64-bit from https://cygwin.com/install.html
2. Select packages: `gcc-core`, `gcc-g++`, `make`, `git`, `wget`, `arm-none-eabi-gcc`
3. Follow Realtek's Cygwin-specific build guide
4. Run builds in Cygwin terminal only

---

## Quick Start (Scripted Path)

The `nora_w30_build.py` script automates the build process:

```bash
# 1. Check environment
python3 nora_w30_build.py doctor

# 2. Clone Realtek RTOS SDK
python3 nora_w30_build.py clone

# 3. List available examples
python3 nora_w30_build.py list

# 4. Build an example
python3 nora_w30_build.py build ota

# 5. Full pipeline (clone + build)
python3 nora_w30_build.py all ota
```

**Note:** Use `python3` on Linux. On Windows/WSL2, use `python` or `python3` depending on PATH.

---

## Manual Setup (Track B)

### Step 1: Clone Realtek SDK

Option A: **Ameba-RTOS (recommended, open-source)**
```bash
git clone --depth=1 https://github.com/ambiot/ameba-rtos.git
cd ameba-rtos
```

Option B: **Realtek Official SDK** (if available from Realtek)
```bash
# Contact Realtek for SDK access if not publicly available
```

### Step 2: Install Toolchain

**Ubuntu/Debian:**
```bash
sudo apt-get install gcc-arm-none-eabi make
```

**WSL2:**
Use the Linux command above.

**Verify installation:**
```bash
arm-none-eabi-gcc --version
make --version
```

### Step 3: Build an Example

Most Realtek examples use a standard Makefile:

```bash
cd ameba-rtos/examples/<example_name>
# or
cd ameba-rtos/project/realtek_amebaZ/<example_name>

make
# or
make -j4  # Parallel build (4 jobs)
```

### Step 4: Flash & Monitor

**Identify serial port:**
```bash
ls /dev/tty* | grep USB
# Usually /dev/ttyUSB0 or /dev/ttyACM0
```

**Flash firmware:**
```bash
# Realtek uses a custom flash tool or bootloader
# Typically via UART or USB
# Check example README for specific instructions

# Example: upload via serial (tool-dependent)
python3 upload_tool.py -p /dev/ttyUSB0 -f output.bin
```

**Monitor via serial:**
```bash
picocom /dev/ttyUSB0 -b 115200
# Or
screen /dev/ttyUSB0 115200
# Or
minicom -D /dev/ttyUSB0 -b 115200
```

Exit: `Ctrl+A Ctrl+X` (picocom) or `Ctrl+A, then Q` (screen)

---

## Examples

Realtek SDK includes examples in various locations:

### Common Examples

1. **hello_world** — Classic "Hello World" to UART
   ```bash
   cd ameba-rtos/examples/hello_world
   make
   ```

2. **wifi/sta** — Wi-Fi station (connect to AP)
   ```bash
   cd ameba-rtos/examples/wifi/sta
   make
   # Edit config to set SSID & password
   ```

3. **ble/example** — Bluetooth LE peripheral
   ```bash
   cd ameba-rtos/examples/ble
   make
   ```

4. **gpio/blink** — GPIO LED toggle
   ```bash
   cd ameba-rtos/examples/gpio/blink
   make
   ```

5. **ota** — Over-the-air firmware update
   ```bash
   cd ameba-rtos/examples/ota
   make
   ```

**To list all examples:**
```bash
find ameba-rtos -name Makefile | head -20
```

---

## Configuring Your Build

### Environment Variables

Set SDK root (if not auto-detected):

```bash
export SDK_ROOT=$(pwd)/ameba-rtos
```

### Build Flags

Common make flags:

```bash
make clean              # Remove build artifacts
make -j4               # Parallel build (faster)
make V=1               # Verbose output (debug build issues)
make TARGET=<target>   # Specify target (check Makefile)
```

### Flash Configuration

Edit example's config file (varies by project):
- `config.h` or `platform_conf.h`
- GPIO pins, UART baud rates, Wi-Fi credentials, etc.

Recompile after changes:
```bash
make clean
make
```

---

## Flashing Firmware

### Using Realtek Flash Tool

1. **Download the flash tool** (from Realtek or SDK docs)
2. **Put device in bootloader mode:**
   - Press RESET button while holding DOWNLOAD/BOOT button
   - Or use a specific GPIO sequence (check EVK manual)
3. **Run flash command:**
   ```bash
   ./flash_tool.py -p /dev/ttyUSB0 -f output.bin -a 0x0
   ```

### Using USB Direct (if supported)

Some EVKs support direct USB flash:
```bash
cp output.bin /media/username/DEVICE_NAME/
# Eject device
```

### Manual UART Flash

If using a custom bootloader:
```bash
# Use xmodem or similar
sx output.bin > /dev/ttyUSB0
```

---

## Troubleshooting

### "arm-none-eabi-gcc: command not found" (Linux)

Install toolchain:
```bash
sudo apt-get install gcc-arm-none-eabi
```

Verify:
```bash
which arm-none-eabi-gcc
```

### "make: command not found"

Install make:
```bash
sudo apt-get install make
```

### Serial port not accessible (Linux)

Add user to dialout group:
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
```

Verify:
```bash
ls -la /dev/ttyUSB0  # Should have 'dialout' in permissions
```

### Build fails with "Permission denied"

Check file permissions:
```bash
ls -la Makefile
# Should be readable (r-x)
```

### Flash tool not found

Flash tools are SDK-specific. Check:
- `tools/flash/` directory in SDK
- Realtek documentation
- EVK user manual

### Serial monitor shows garbage

Verify baud rate matches firmware:
```bash
picocom /dev/ttyUSB0 -b 115200
# or
picocom /dev/ttyUSB0 -b 9600  # Common alternative
```

---

## Custom Application

### Create from Template

Most Realtek SDKs provide a project template:

```bash
cd ameba-rtos
cp -r examples/hello_world my-app
cd my-app
```

### Project Structure (Typical)

```
my-app/
├── Makefile              (Build configuration)
├── main.c               (Main application)
├── config.h             (Configuration)
├── build/               (Build artifacts - auto-generated)
└── output/              (Compiled firmware)
```

### Edit & Build

1. **Edit main.c** with your code
2. **Configure** in config.h or Makefile
3. **Build:** `make`
4. **Flash:** Use flash tool (see above)
5. **Monitor:** Connect to serial port at correct baud rate

### Key APIs

- **Wi-Fi:** `wifi_api.h`, `wifi_config.h`
- **BLE:** `ble_api.h`, `gattdefs.h`
- **GPIO:** `gpio_api.h`, `diag.h`
- **UART:** `serial_api.h`, `sys_api.h`
- **SPI:** `spi_api.h`
- **I2C:** `i2c_api.h`
- **Timer:** `timer_api.h`
- **Flash/NVS:** `flash_api.h`

See Realtek SDK documentation or header files for details.

---

## Documentation & Resources

- **Ameba-RTOS GitHub:** https://github.com/ambiot/ameba-rtos
- **Realtek RTL872x Datasheet:** Contact Realtek or u-blox
- **Realtek Documentation:** Check SDK docs/ folder
- **u-blox NORA-W30 Datasheet:** https://www.u-blox.com/
- **Realtek Official:** https://www.realtek.com/

---

## Windows & WSL2 Setup

### Install WSL2

```powershell
# Run PowerShell as Administrator
wsl --install
# Restart required

# Verify
wsl -l -v
```

### Use Linux Build in WSL2

```powershell
wsl
# Now in Ubuntu bash
cd /mnt/c/path/to/your/workspace
python3 nora_w30_build.py doctor
```

### Share Windows files with WSL2

Windows file access from WSL2:
```bash
cd /mnt/c/Users/YourName/Documents/my-project
```

WSL2 file access from Windows Explorer:
```
\\wsl$\Ubuntu\home\username\
```

---

## Support & Issues

- **Ameba-RTOS Issues:** https://github.com/ambiot/ameba-rtos/issues
- **u-blox Support:** https://www.u-blox.com/support
- **Community:** Check Realtek forums

---

## Verified Setup

✅ **Tested on:**
- Ubuntu 24.04 LTS (native)
- Ubuntu 22.04 LTS (WSL2 on Windows 11)
- Debian 12 (bookworm)

✅ **Toolchain:** arm-none-eabi-gcc 12.x+

✅ **SDK:** Ameba-RTOS (latest stable)

---

## License & Disclaimer

NORA-W30 is produced by u-blox. Ameba-RTOS is open-source under Apache 2.0 or GPL (varies by component).

See u-blox and Realtek licensing terms for details.
