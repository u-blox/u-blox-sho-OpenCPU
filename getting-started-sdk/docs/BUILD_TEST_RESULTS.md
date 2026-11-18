# Getting Started SDK - Build Test Results

The only record of real builds. Add a row after every verified build; do not
copy these numbers into other docs.

Host: Windows 11 + WSL2 (Ubuntu-24.04, Ubuntu-22.04), Python 3.14.
Branch: `cmag_getting_started_sdk`.

## Summary

| Target | Example | SDK / toolchain | Result | Date |
|--------|---------|-----------------|--------|------|
| IRIS-W10 | `demo_apps/hello_world` | MCUXpresso 26.09.00-pvw2, Arm GCC 14.2.1 | [OK] 28,968 B flash (1.4% of 2 MB) | 2026-10-07 |
| IRIS-W10 | `demo_apps/hello_world` + `--rf-config` (IRIS-W101-00B), `--flash` + `--log` on EVK-IRIS-W1 | MCUXpresso `main` (`sdks/mcuxpresso-sdk/main`), J-Link via the on-board MCU-Link | [OK] build, rf-config (Fidelix FCB), boot-ROM recovery (`--flash COM147`, SW3 EXT-REQ), then J-Link `--flash` with verify; `hello world.` on COM147 | 2026-10-12 |
| NORA-W40 | `hello_world` | ESP-IDF 6.2.0, Windows | [OK] `.bin` 130,736 B, 88% of app partition free | 2026-10-07 |
| NORA-W40 | `ubx/rf-calibration` + `--rf-config` (NORA-W401) | ESP-IDF 6.2.0, riscv32-esp-elf 16.1.0 | [OK] `u-blox-nora-w40.bin` 920,544 B, 12% of 1 MB app partition free | 2026-10-12 |
| NORA-W40 | `ubx/rf-calibration`, `--flash` + `--log` on EVK-NORA-W40 (FTDI COM USB, S4 ON) | ESP-IDF 6.2.0 (`sdks/esp-idf/master`), esptool 5.4.0 | [OK] auto-reset into the bootloader over FTDI; log shows `ubx_phy_cal: loading PHY init data from application binary`, MAC f0:f5:bd:13:6f:94 | 2026-10-12 |
| NORA-W40 | `ubx/read-mac` | ESP-IDF 6.2.0 (`sdks/esp-idf/master`), riscv32-esp-elf 16.1.0 | [OK] build only: `u-blox-nora-w40-read-mac.bin` 196,304 B, 81% of 1 MB app partition free; not run on hardware yet | 2026-10-12 |
| NORA-W50-W51 | `ble_wifi_provisioning` | simplelink_wifi_sdk_10_20_00_39, `LP_EM_CC35X1` | [OK] `.out` 16 MB | 2026-09-28 |
| NORA-W30 | `project_lp` + `project_hp`, `--flash` | Ameba-D `main` in `~/ubx-sdk/sdks` (WSL2 Ubuntu-24.04), asdk-6.4.1; J-Link V9.46, EVK J-Link OB | [OK] build, `km0_km4_image2.bin` 671,744 B; [OK] flash (3 images, J-Link device `RTL8720DF`); [OK] boot and console: `ATW?` reports MAC 54:f8:2a:13:f7:94 | 2026-10-12 |
| NORA-B20-B21-B22 | `hello_world` (`ubx_evknorab2/nrf54l15/cpuapp`) | NCS v3.4.1 (Zephyr 4.4.2), Zephyr SDK 1.0.1 GCC 14.3.0, Windows | [OK] 30,236 B flash (1.94% of 1524 KB), 5,800 B RAM (2.21%); [OK] `--flash` (nrfutil, EVK-NORA-B2 OB) and `--log` on the FTDI "USB Serial Port": `Hello World! ubx_evknorab2/nrf54l15/cpuapp` | 2026-10-12 |
| ALMA-B20-B21 | `hello_world` | NCS v3.4.1 | not built yet | - |
| ALMA-W10-W11 | `hello_world` | NCS v3.5.0-preview4 | not built yet | - |

All results above were taken before the SDKs moved to `sdks/<vendor>/<version>/`
(2026-10-12). Re-run each target once to confirm the new layout.

## Notes

**NORA-W40 `ubx/rf-calibration`** (`ubx-sdk.cmd nora-w40 --variant NORA-W401 --rf-config --build ubx/rf-calibration`):
built in place from `esp-idf/nora-w40/` at the repository root. Without
`--rf-config` the link fails (duplicate `esp_phy_get_init_data`); the launcher
refuses that combination up front. RF configuration was reverted afterwards
(`module_config.py nora-w40 revert`).

**NORA-W40** builds with ESP-IDF's own Python environment
(`~/.espressif/python_env/idf6.2_py3.14_env/`), not the repository `.venv`.

**NORA-W30** builds on Linux only; on Windows the launcher hops into WSL2.
From `/mnt/e` a `project_hp` build ran for over 40 minutes; with the SDK in
the WSL2 file system it is much faster. J-Link device `RTL872xCS` connects
but fails to erase; `RTL8720DF` works. Leaving the chip under debugger control
after flashing made it fault at its first low-power sleep; `--flash` now ends
with debug off and a reset-pin pulse, like pressing RESET.
