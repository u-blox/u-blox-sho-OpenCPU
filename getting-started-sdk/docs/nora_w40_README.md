# NORA-W40 (Espressif ESP32-C6)

| | |
|---|---|
| Radio | 2.4 GHz Wi-Fi 6, Bluetooth LE 5.3, IEEE 802.15.4 (Thread, Zigbee) |
| MCU | RISC-V up to 160 MHz plus a low-power RISC-V core, 512 kB SRAM, 4 or 8 MB flash |
| Parts | NORA-W401 (antenna pin), NORA-W406 (internal PCB antenna) |
| SDK | ESP-IDF (`idf.py`), target `esp32c6` |
| Host | Windows, WSL2, Linux, macOS |

## Quick start

```bash
./ubx-sdk.sh nora-w40 --doctor
./ubx-sdk.sh nora-w40 --clone --install
./ubx-sdk.sh nora-w40 --variant NORA-W401 --rf-config --build ubx/rf-calibration --flash --log
```

Without `--rf-config` the firmware runs on Espressif's default PHY data and is
not regulatory compliant on the module. `ubx/rf-calibration` is a Wi-Fi station
built on the u-blox PHY data; its log must contain
`ubx_phy_cal: loading PHY init data from application binary`.

- `--clone` fetches the ESP-IDF release this SDK is tested with, one the u-blox
  PHY patch covers, into `sdks/esp-idf/<version>`; `--clone master` fetches the
  development branch next to it (`--rf-config` refuses an IDF without a patch).
- `--install` runs ESP-IDF's own installer (toolchain and Python environment
  under `~/.espressif`). It works from cmd, PowerShell, Git Bash and Linux.
- `--build` sets the target to `esp32c6` before the first build. Any example
  from `--list` works, e.g. `--build hello_world` or `--build wifi/getting_started/station`.

Output: `<example>/build/` inside the ESP-IDF tree (`.elf`, `.bin`).

## Flash and log

`--flash` and `--log` run `idf.py flash` and `idf.py monitor` over the EVK's
USB serial port (auto-detected; pass it with `--flash COM5`). Leave the monitor
with Ctrl+].

On EVK-NORA-W40 the FTDI (U7) drives reset and boot, so esptool enters the
bootloader by itself: no BOOT button press. Keep S4 ON (UART0 to the FTDI); the
console is the first of the two FTDI COM ports. Because these lines are used
for reset, UART0 hardware flow control and DSR are not available in this setup.

## ESP-IDF extension

After `--clone --install --rf-config`, choose "Use existing setup" in the
ESP-IDF extension with `IDF_PATH` set to `sdks/esp-idf/<version>` (tools stay in
`~/.espressif`). Open any example or
[esp-idf/nora-w40](../../esp-idf/nora-w40/README.md), target `esp32c6`. See
[SETUP.md](SETUP.md#vendor-extensions).

## u-blox examples

| Example | |
|---------|---|
| `ubx/rf-calibration` | Wi-Fi station on the u-blox PHY init data (needs `--rf-config`) |
| `ubx/read-mac` | Prints the base, Wi-Fi, Bluetooth and 802.15.4 addresses at boot |

They live in [esp-idf/nora-w40](../../esp-idf/nora-w40/README.md), with the RF data
and SDK patches `--rf-config` applies.

## MAC address

Set by u-blox in eFuse; Wi-Fi, Bluetooth and 802.15.4 addresses are derived
from it. `--mac` reads it from the PC with esptool and lists every derived
address. `--mac-set <ADDR>` shows how to use another one at runtime, and
`--mac-set <ADDR> --burn` writes it to the `CUSTOM_MAC` eFuse (one time,
irreversible).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `idf.py` or the toolchain not found | `--install` |
| No serial port (Linux) | `sudo usermod -aG dialout $USER`, then log in again |
| No serial port (WSL2) | Flash from Windows, or attach the port with `usbipd` |
