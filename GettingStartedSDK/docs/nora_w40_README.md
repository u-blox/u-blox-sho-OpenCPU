# NORA-W40 Getting Started Guide

## Overview

NORA-W40 modules are based on the **Espressif ESP32-S3** SoC with Wi-Fi 6 (802.11ax) and Bluetooth LE 5.3. This guide covers building and deploying firmware using the latest **ESP-IDF** (Espressif IoT Development Framework).

**Key Features:**
- Dual-core Xtensa processor @ 240 MHz
- 2.4 GHz Wi-Fi 6 + Bluetooth LE 5.3
- 8 MB internal flash, up to 16 MB external flash
- Excellent Windows & Linux support

**SDK:** ESP-IDF v5.x (latest stable)  
**Platforms:** Windows (native), WSL2, Linux (Ubuntu/Debian)  
**Build System:** CMake + GNU Make  
**Toolchain:** xtensa-esp32s3-elf (installed via esp-idf-tools)

---

## Prerequisites

### Windows

1. **Python 3.8+** (for ESP-IDF tools)
   - Download: https://www.python.org/downloads/
   - Add to PATH during installation

2. **Git** (for cloning ESP-IDF)
   - Download: https://git-scm.com/download/win
   - Use default settings (Git Bash)

3. **CMake 3.20+**
   - Download: https://cmake.org/download/
   - Add to PATH

4. **USB Driver** (CH340 or CP2102 depending on EVK)
   - CH340: https://sparks.gogo.co.nz/ch340.html
   - CP2102: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 python3-pip python3-venv \
  git cmake build-essential \
  libusb-1.0-0 udev
```

Grant serial port access:
```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
# Log out and back in to apply
```

### WSL2

Use the Linux setup above (same commands work in WSL2 Ubuntu).

---

## Quick Start (Scripted Path)

The `nora_w40_build.py` script automates the entire process:

```bash
# 1. Check environment
python nora_w40_build.py doctor

# 2. Clone ESP-IDF
python nora_w40_build.py clone

# 3. List available examples
python nora_w40_build.py list

# 4. Build an example
python nora_w40_build.py build hello_world

# 5. Full pipeline (clone + build)
python nora_w40_build.py all hello_world
```

---

## Manual Setup (Track B)

### Step 1: Clone ESP-IDF

```bash
cd your-workspace
git clone --depth=1 https://github.com/espressif/esp-idf.git
cd esp-idf
```

### Step 2: Install ESP-IDF Tools

```bash
python tools/idf_tools.py install
python tools/idf_tools.py install-python-env
```

On Windows, run:
```bash
install.bat
```

### Step 3: Set IDF_PATH Environment Variable

**Linux/WSL2:**
```bash
export IDF_PATH=$(pwd)
```

**Windows (permanent, via setx):**
```cmd
setx IDF_PATH "C:\path\to\esp-idf"
```

### Step 4: Source the Environment

**Linux/WSL2:**
```bash
source export.sh
```

**Windows (Git Bash):**
```bash
source export.sh
# Or use:
. ./export.bat (in cmd.exe)
```

### Step 5: Navigate to Example and Build

```bash
cd examples/hello_world
idf.py build
idf.py flash -p COM3 -b 921600  # Windows: replace COM3 with your port
idf.py flash -p /dev/ttyUSB0    # Linux
```

Monitor output:
```bash
idf.py monitor
# Or with custom baudrate:
idf.py monitor -b 115200
```

---

## Examples

ESP-IDF includes many examples in `examples/` directory:

### Recommended Starting Points

1. **hello_world** — Classic "Hello World" output to UART
   ```bash
   python nora_w40_build.py build hello_world
   ```

2. **wifi/getting_started/station** — Connect to Wi-Fi, ping a host
   ```bash
   cd $IDF_PATH/examples/wifi/getting_started/station
   idf.py menuconfig  # Set Wi-Fi SSID & password
   idf.py build
   idf.py flash
   ```

3. **bluetooth/ble/gatt_server** — Bluetooth LE GATT server
   ```bash
   python nora_w40_build.py build bluetooth/ble/gatt_server
   ```

4. **get-started/blink** — GPIO LED blink example
   ```bash
   python nora_w40_build.py build get-started/blink
   ```

### Full Example List

Run `nora_w40_build.py list` to see all available examples.

---

## Flashing & Monitoring

### Identify Serial Port

**Windows:**
```cmd
mode  # Lists COM ports, or check Device Manager
```

**Linux:**
```bash
ls /dev/tty* | grep USB
# Usually /dev/ttyUSB0 or /dev/ttyACM0
```

### Flash Firmware

```bash
idf.py flash -p COM3              # Windows
idf.py flash -p /dev/ttyUSB0      # Linux
idf.py flash -p /dev/ttyUSB0 -b 921600  # Custom baud rate
```

### Monitor Output

```bash
idf.py monitor -p COM3
idf.py monitor -p /dev/ttyUSB0
# Exit: Ctrl+]
```

---

## Configuration (menuconfig)

Customize build settings:

```bash
idf.py menuconfig
```

Navigate with arrow keys:
- **Component config** → Customize drivers, Wi-Fi, BLE, etc.
- **SDK tool configuration** → Build system options
- **Partition table** → Flash layout

Common settings:
- **Component config** → Wi-Fi → Max TX Power
- **Component config** → Bluetooth → Max TX Power
- **Partition table** → Select custom layout (if needed)

---

## Troubleshooting

### "python: command not found" on Linux

Install Python:
```bash
sudo apt-get install python3
python3 nora_w40_build.py doctor
```

Or create alias:
```bash
alias python=python3
```

### Serial port not found

**Windows:**
- Open Device Manager, look for "USB Serial" device
- Check CH340 or CP2102 driver installation
- Try reseating the USB cable

**Linux:**
- Run `ls /dev/tty*` with and without EVK connected
- Check `dmesg` for USB errors
- Verify user is in `dialout` group: `id` should show `dialout`

### "Permission denied" when flashing (Linux)

Add your user to dialout group:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### idf.py: command not found

Run `source export.sh` (Linux) or `export.bat` (Windows) first.

### Failed to build

Check for obvious issues:
```bash
idf.py fullclean
idf.py build -v  # Verbose output
```

Look for missing dependencies or toolchain issues. Check IDF version matches your example.

---

## Custom Application

### Create a New Project

Use the ESP-IDF template:

```bash
idf.py create-project my-app
cd my-app
```

Or copy an existing example:

```bash
cp -r $IDF_PATH/examples/hello_world my-app
cd my-app
```

### Project Structure

```
my-app/
├── CMakeLists.txt              (Build configuration)
├── main/
│   ├── CMakeLists.txt
│   └── hello_world_main.c      (Main application code)
├── build/                       (Build artifacts - auto-generated)
└── sdkconfig                    (Build settings - from menuconfig)
```

### Edit & Build

1. **Edit main/hello_world_main.c** with your code
2. **Build:** `idf.py build`
3. **Flash:** `idf.py flash`
4. **Monitor:** `idf.py monitor`

### Key APIs

- **Wi-Fi:** `esp_wifi.h`, `esp_netif.h`
- **BLE:** `esp_gap_ble.h`, `esp_gatts_api.h`, `esp_gattc_api.h`
- **GPIO:** `driver/gpio.h`, `driver/rmt.h`
- **UART:** `driver/uart.h`
- **SPI:** `driver/spi_master.h`
- **I2C:** `driver/i2c.h`
- **Timer:** `driver/timer.h`
- **NVS (flash storage):** `nvs_flash.h`

See [ESP-IDF API Reference](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/index.html).

---

## Documentation & Resources

- **ESP-IDF Official Docs:** https://docs.espressif.com/projects/esp-idf/
- **ESP32-S3 Datasheet:** https://www.espressif.com/en/products/socs/esp32-s3/overview
- **ESP-IDF Examples:** https://github.com/espressif/esp-idf/tree/master/examples
- **Espressif GitHub:** https://github.com/espressif/esp-idf
- **u-blox NORA-W40 Datasheet:** https://www.u-blox.com/

---

## Support & Issues

- **ESP-IDF Issues:** https://github.com/espressif/esp-idf/issues
- **u-blox Support:** https://www.u-blox.com/support
- **Community Forums:** https://www.espressif.com/en/community

---

## Verified Setup

✅ **Tested on:**
- Windows 11 (22H2) with Python 3.12, CMake 3.28, Git 2.53
- Ubuntu 24.04 LTS (native & WSL2)
- Debian 12 (bookworm)

✅ **ESP-IDF Version:** v5.2.x (latest stable)

✅ **Toolchain:** xtensa-esp32s3-elf (bundled with ESP-IDF tools)

---

## License & Disclaimer

NORA-W40 is produced by u-blox. ESP-IDF is open-source under the Apache 2.0 license.

See u-blox and Espressif licensing terms for details.
