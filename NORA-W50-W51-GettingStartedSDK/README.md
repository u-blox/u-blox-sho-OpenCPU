# NORA-W50 / W51 Open CPU — Getting started with the TI SimpleLink Wi-Fi SDK

Build your own firmware on the module's own Cortex-M33 (Open CPU) using Texas Instruments'
SDK and **TI's own example applications**. Covers Windows, Linux and WSL2.

---

## 1. What you are targeting

| Item | Value |
|---|---|
| Modules | NORA-W501 / W506 (single-band 2.4 GHz), NORA-W511 / W516 (dual-band 2.4 + 5 GHz) |
| SoC | TI **CC35x1E** — CC3501E (single-band) / CC3551E (dual-band) |
| MCU | Arm Cortex-M33 @ 160 MHz, 1.1 MB SRAM, 4 or 8 MB flash |
| Radio | Wi-Fi 6 (802.11 b/g/n/ax), Bluetooth LE 5.4 |
| Security | TrustZone-M, HSM/crypto accelerator, secure boot, secure key storage, debug lock |
| SDK | **TI SimpleLink Wi-Fi SDK** (current release line 10.20.00.xx) |
| RTOS | **FreeRTOS** (TI SDK default) or **Zephyr** (TI downstream) |
| SDK board names | `LP_EM_CC35X1`, `LP_EM_CC35X1ET` (TI LaunchPads) / `lp_em_cc35x1` (Zephyr) |

> The SDK ships board files for TI's `LP_EM_CC35X1` LaunchPad. For a u-blox EVK you keep the
> same device but re-run SysConfig to match the module's pinout and flash size. Ask u-blox
> support for module-specific board files.

Pick **one** of two tracks:

- **Track A — FreeRTOS + SimpleLink Wi-Fi SDK.** TI's primary path. Most examples, incl. all BLE demos.
- **Track B — Zephyr.** TI downstream Zephyr with CC35xx drivers. Fewer examples, standard Zephyr samples.

---

## 2. Prerequisites (all platforms)

| Tool | Where |
|---|---|
| SimpleLink Wi-Fi SDK | <https://github.com/TexasInstruments/simplelink-wifi-sdk> or the [installer](https://www.ti.com/tool/download/SIMPLELINK-WIFI-SDK) |
| SysConfig | <https://www.ti.com/tool/SYSCONFIG> (also bundled with CCS) |
| TI Arm Clang (`tiarmclang`) | <https://www.ti.com/tool/download/ARM-CGT-CLANG> |
| Arm GNU Toolchain (`arm-none-eabi-gcc`) | <https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads> |
| CMake | <https://cmake.org/> |
| GNU make | Native on Linux; on Windows use `gmake` from `ccs/utils/bin/` |
| Code Composer Studio (optional IDE) | <https://www.ti.com/tool/CCSTUDIO> |
| Python 3 + Git | your package manager |

You need **either** TI Arm Clang **or** Arm GNU — the examples ship a `ticlang/` and a `gcc/`
build folder. Check the SDK release notes for the exact validated versions.

### Windows

```powershell
winget install Git.Git Python.Python.3.12 Kitware.CMake
```
Then install CCS (gives you SysConfig + `gmake`), TI Arm Clang and/or Arm GNU Toolchain via
their own installers. Use a **Git Bash** or **CCS command prompt** shell for the `make` steps.

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y git python3 python3-pip cmake make build-essential libncurses6
```
Install SysConfig and the Arm toolchains from the links above (they are `.run` / tarball installers).

Give yourself access to the on-board XDS110 debugger without root. CCS ships the rules file —
run the installer script it provides:
```bash
sudo <ccs-install-dir>/ccs/install_scripts/install_drivers.sh
sudo usermod -aG dialout,plugdev $USER   # log out / in afterwards
```

### WSL2

Use the Linux instructions inside WSL2, plus:

1. Keep the source tree in the **Linux** filesystem (`~/ti-w5`), not `/mnt/c` — builds are much faster.
2. USB (XDS110 / UART) is not visible by default. From an **admin PowerShell** on Windows:
   ```powershell
   winget install usbipd
   usbipd list
   usbipd bind   --busid <BUSID>
   usbipd attach --wsl --busid <BUSID>
   ```
   Then in WSL: `lsusb` should show the device, and it appears as `/dev/ttyACM*`.
3. Alternative that always works: **build in WSL, flash from Windows** with the SimpleLink
   Wi-Fi toolbox / CCS pointing at the image under `\\wsl$\Ubuntu\home\<user>\...`.

---

## 3. Track A — FreeRTOS + SimpleLink Wi-Fi SDK

### 3.0 Scripted path (recommended)

[ti_w5_build.py](ti_w5_build.py) automates everything below on Windows, WSL2 and Linux. It
finds an installed SDK (or clones TI's example repos), writes the detected tool paths into
`imports.mak`, builds the SDK libraries and then builds examples.

```bash
python ti_w5_build.py doctor              # what is installed, what is missing
python ti_w5_build.py configure           # patch imports.mak (backs up as imports.mak.orig)
python ti_w5_build.py build-sdk           # build SDK libraries (slow, once per SDK)
python ti_w5_build.py list                # show real example names
python ti_w5_build.py build network_terminal
```

| Command | Purpose |
|---|---|
| `doctor` | Host type, detected toolchain, discovered SDK trees and boards |
| `clone` | Clone TI's example repos with the SDK submodule (only needed if no SDK is installed) |
| `configure` | Write `SYSCONFIG_TOOL`, `TICLANG_ARMCOMPILER`, `GCC_ARMCOMPILER`, `CMAKE`, `PYTHON`, `SIMPLELINK_WIFI_TOOLBOX_INSTALL_DIR` into every `imports.mak` |
| `build-sdk` | `make` at the SDK root; `--toolchain ticlang` builds one toolchain only (about half the time) |
| `list` | Enumerate examples per board |
| `build <name>...` | Build examples; `--all`, `--clean`, `--keep-going` |
| `all` | configure + build-sdk + build in one go |

Useful flags: `--toolchain gcc` (default `ticlang`), `--board LP_EM_CC35X1ET`,
`--sdk <path>` to point at a specific SDK, `-j8` for parallel builds, and
`--gcc_armcompiler <dir>` style overrides for any tool it fails to detect.
Settings are cached in `.ti_w5_build.<host>.json`, one file per host type so the same
folder works from Windows and WSL at once.

On Windows the script converts paths containing spaces to their 8.3 short form, because
TI's `imports.mak` states that tool paths must not contain spaces.

Verified on Windows 11 against SDK 10.20.00.39 with SysConfig 1.28.0, TI Arm Clang,
Arm GNU Toolchain, CMake and GNU make 4.4.1: SDK libraries and the `uart2echo` and
`network_terminal` examples all build and link. The Linux and WSL2 paths use the same
code and are expected to work, but have not been run yet.

The manual equivalent is described below.

### 3.1 Get the SDK

Either install it with TI's installer (gives you `examples/`, `docs/` and `tools/`):

<https://www.ti.com/tool/download/SIMPLELINK-WIFI-SDK> → e.g. `C:\ti\simplelink_wifi_sdk_10_20_00_39`

or clone TI's example repos, which pull the SDK in as a submodule:

```bash
# Wi-Fi + BLE demo applications
git clone --recurse-submodules https://github.com/TexasInstruments/simplelink-wifi-examples.git

# Peripheral / driver examples (UART, GPIO, SPI, I2C, ADC, CAN, crypto, ...)
git clone --recurse-submodules https://github.com/TexasInstruments/simplelink-coresdk_wifi-examples.git
```

Already cloned without submodules? `git submodule update --init`.

### 3.2 Point the build at your tools

Edit `imports.mak` at the SDK root (and, for the git path, the one in the repo root too):

```make
SYSCONFIG_TOOL                      ?= C:/ti/sysconfig_1.28.0/sysconfig_cli.bat
TICLANG_ARMCOMPILER                 ?= C:/ti/ti-cgt-armllvm_4.0.4.LTS
GCC_ARMCOMPILER                     ?= C:/arm-none-eabi-gcc/12.3.Rel1-0-win32
CMAKE                               ?= C:/Progra~2/CMake/bin/cmake
PYTHON                              ?= python
SIMPLELINK_WIFI_TOOLBOX_INSTALL_DIR ?= C:/ti/simplelink_wifi_toolbox_win_4_3_23
```

On Linux/WSL the same variables point at `/opt/ti/...` and `sysconfig_cli.sh`.

Two rules the SDK enforces:

- **Paths must not contain spaces.** On Windows use the 8.3 short form
  (`C:/Progra~1/...`) — `ti_w5_build.py configure` does this conversion for you.
- Setting a `*_ARMCOMPILER` variable to empty disables that toolchain. Leave only the one
  you actually have if you want faster builds.

### 3.3 Build the SDK libraries (once per SDK update)

```bash
cd C:/ti/simplelink_wifi_sdk_10_20_00_39      # or <repo>/Simplelink-wifi-sdk
make            # gmake on Windows
```

The SDK ships mostly without prebuilt libraries — skipping this step makes every example fail to link.

### 3.4 Build an example

Path pattern: `examples/rtos/<board>/<group>/<example>/freertos/<ticlang|gcc>/`

```bash
cd examples/rtos/LP_EM_CC35X1/demos/network_terminal/freertos/ticlang
make
# make clean to rebuild
```

On Windows run this from a **cmd/PowerShell** prompt rather than Git Bash — the TI makefiles
branch on `$(SHELL)` and are tested against the native Windows shell.

`make` in `examples/rtos/LP_EM_CC35X1/` builds every example for both toolchains.

### 3.5 Or build in Code Composer Studio

1. **Preferences → Code Composer Studio → Products → Add…** → select the `Simplelink-wifi-sdk` folder.
2. **Project → Import CCS Project…** → browse to the example repo → pick the example(s) → **Finish**.

Each example also contains a `.syscfg` file — open it in SysConfig (or CCS) to change pinmux,
Wi-Fi settings, clocks and peripherals instead of hand-editing C.

---

## 4. TI's example applications — use these, don't write from scratch

### Wi-Fi / BLE demos
Path `examples/rtos/LP_EM_CC35X1/demos/` (also available for board `LP_EM_CC35X1ET`)

| Example | What it gives you |
|---|---|
| `network_terminal` | **Best Wi-Fi starting point.** UART CLI to scan, connect, set profiles, open TCP/UDP/TLS sockets, ping, run transceiver mode. |
| `mqtt_client` | Connect to Wi-Fi then publish/subscribe over MQTT (incl. TLS). |
| `ble_wifi_provisioning` | **Best Wi-Fi + BLE combo.** Provision Wi-Fi credentials from a phone over BLE. |
| `ble_controller` | BLE controller / host-controller interface bring-up. |
| `ble_dtm` | Bluetooth LE Direct Test Mode — RF/production BLE testing. |
| `at_commands` | AT-style command interface running on the device. |
| `ota_example` | Over-the-air firmware update flow. |
| `power_measurement` | Low-power / Target Wake Time current-consumption measurements. |
| `indigo` | Wi-Fi Alliance certification test tool. |

### Peripheral & driver examples
Path `examples/rtos/LP_EM_CC35X1/drivers/`

`empty` (project skeleton — start custom apps here), `uart2echo`, `gpiointerrupt`, `pwmled1`,
`adcsinglechannel`, `i2ccontroller`, `spicontroller`, `spiperipheral`, `i2secho`, `pdmsamples`,
`watchdog`, `canInitiator`, `canResponder`, `canTimeSync`, `itmwrite`, `exception`,
`sha2hash`, `sha3hash`, `psaAeadEncrypt`, `psaKeyDerivation`, `psaRawKeyAgreement`, `psaSignVerify`.

Every example folder has a `README.html` with wiring, expected output and step-by-step usage —
read it before running.

### Suggested first run

1. `drivers/uart2echo` — proves toolchain, flashing and serial console work.
2. `demos/network_terminal` — proves Wi-Fi works; type `scan` then `wlanconnect`.
3. `demos/ble_wifi_provisioning` — proves BLE works and shows Wi-Fi + BLE coexistence.

---

## 5. Track B — Zephyr

```bash
python3 -m venv ~/zephyrvenv && source ~/zephyrvenv/bin/activate
pip install west

# Use the TI downstream, not upstream Zephyr. Check the tag list:
#   https://github.com/TexasInstruments/simplelink-zephyr/tags
west init -m https://github.com/TexasInstruments/simplelink-zephyr --mr <tag-name> zephyrproject
cd zephyrproject && west update
west zephyr-export
pip install -r zephyr/scripts/requirements.txt
```

Build standard Zephyr samples for the board `lp_em_cc35x1`:

```bash
west build -p always -b lp_em_cc35x1 zephyr/samples/net/wifi            # Wi-Fi shell
west build -p always -b lp_em_cc35x1 zephyr/samples/bluetooth/peripheral # BLE peripheral
```

BLE FOTA (MCUboot) — add to the app's `prj.conf`:

```ini
CONFIG_BOOTLOADER_MCUBOOT=y
CONFIG_TI_MCUMGR_BT_OTA_DFU=y
```
and build MCUboot separately:
```bash
west build -p always -b lp_em_cc35x1 -d build_mcuboot bootloader/mcuboot/boot/zephyr
```

> Programming `lp_em_cc35x1` requires the **SimpleLink Wi-Fi toolbox** from TI; `west flash`
> is not wired up for this device. TI marks the Zephyr release as beta — Track A is the safer
> choice for production work today.

---

## 6. Flash and run

1. Connect the EVK/LaunchPad over USB — the on-board **XDS110** gives you both debug and a UART.
2. Flash with the **SimpleLink Wi-Fi toolbox** (part of the SDK installer), with **CCS**, or with
   **UniFlash**.
3. Open a serial terminal on the XDS110 *Application/User UART* port at **115200 8N1**
   (`/dev/ttyACM0` on Linux/WSL, `COMx` on Windows).

```bash
# Linux / WSL
screen /dev/ttyACM0 115200
```

---

## 7. Making it your own application

1. Copy `drivers/empty` (bare skeleton) or the demo closest to your use case into your own repo.
2. Open its `.syscfg` in SysConfig → set the CC35x1E device/package, pinmux, UART, Wi-Fi and
   BLE settings to match the NORA-W5x module.
3. Adjust the linker command file for **4 MB vs 8 MB** flash.
4. Keep the example's `makefile` / `.projectspec`; only the relative
   `SIMPLELINK_WIFI_SDK_INSTALL_DIR` path needs to stay correct.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| Linker errors about missing SDK libs | You skipped `make` in `Simplelink-wifi-sdk/`. |
| `sysconfig_cli` not found | Wrong `SYSCONFIG_TOOL` in `imports.mak`; on Windows it must be the `.bat`. |
| `tiarmclang` / `arm-none-eabi-gcc` not found | Fix `TICLANG_ARMCOMPILER` / `GCC_ARMCOMPILER` in `imports.mak`. |
| `make` not found on Windows | Use `gmake` from `ccs/utils/bin/`, or `winget install ezwinports.make`. |
| Odd path errors in the makefiles | A tool path contains spaces. Use the 8.3 short form, or run `ti_w5_build.py configure`. |
| Build fails only after an SDK update | Rebuild SDK libs and re-check SysConfig version in the release notes. |
| Device not enumerating in WSL | `usbipd attach --wsl --busid <BUSID>` from admin PowerShell. |
| No serial output | Wrong port (pick the *Application* UART, not the *Auxiliary* one) or wrong baud (115200). |
| Wi-Fi won't associate | Single-band parts (W501/W506) are 2.4 GHz only — a 5 GHz-only SSID will never appear in `scan`. |

---

## 9. Reference links

- SimpleLink Wi-Fi SDK — <https://github.com/TexasInstruments/simplelink-wifi-sdk>
- Wi-Fi / BLE examples — <https://github.com/TexasInstruments/simplelink-wifi-examples>
- Driver examples — <https://github.com/TexasInstruments/simplelink-coresdk_wifi-examples>
- TI Zephyr downstream — <https://github.com/TexasInstruments/simplelink-zephyr>
- SDK docs (TI Resource Explorer) — <https://dev.ti.com/tirex/explore>
- NORA-W5 series product page — <https://www.u-blox.com/en/product/nora-w5-series>
- TI E2E support forum — <https://e2e.ti.com/>
