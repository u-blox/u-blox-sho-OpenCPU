# Getting Started SDK - Build Test Results

The only record of real builds. Add a row after every verified build; do not
copy these numbers into other docs.

Host: Windows 11 + WSL2 (Ubuntu-24.04, Ubuntu-22.04), Python 3.14.
Branch: `cmag_getting_started_sdk`.

## Summary

| Target | Example | SDK / toolchain | Result | Date |
|--------|---------|-----------------|--------|------|
| IRIS-W10 | `demo_apps/hello_world` | MCUXpresso 26.09.00-pvw2, Arm GCC 14.2.1 | [OK] 28,968 B flash (1.4% of 2 MB) | 2026-10-07 |
| NORA-W40 | `hello_world` | ESP-IDF 6.2.0, Windows | [OK] `.bin` 130,736 B, 88% of app partition free | 2026-10-07 |
| NORA-W40 | `ubx/rf-calibration` + `--rf-config` (NORA-W401) | ESP-IDF 6.2.0, riscv32-esp-elf 16.1.0 | [OK] `u-blox-nora-w40.bin` 920,544 B, 12% of 1 MB app partition free | 2026-10-12 |
| NORA-W40 | `ubx/read-mac` | ESP-IDF 6.2.0 (`sdks/esp-idf/master`), riscv32-esp-elf 16.1.0 | [OK] build only: `u-blox-nora-w40-read-mac.bin` 196,304 B, 81% of 1 MB app partition free; not run on hardware yet | 2026-10-12 |
| NORA-W50-W51 | `ble_wifi_provisioning` | simplelink_wifi_sdk_10_20_00_39, `LP_EM_CC35X1` | [OK] `.out` 16 MB | 2026-09-28 |
| NORA-W30 | `project_hp` | Ameba-D, WSL2 | [FAIL] E: full during build; re-run pending | 2026-10-07 |
| NORA-B20-B21-B22 | `hello_world` (`ubx_evknorab2/nrf54l15/cpuapp`) | NCS v3.4.1 (Zephyr 4.4.2), Zephyr SDK 1.0.1 GCC 14.3.0, Windows | [OK] 30,236 B flash (1.94% of 1524 KB), 5,800 B RAM (2.21%); not run on hardware yet | 2026-10-12 |
| ALMA-B20-B21 | `hello_world` | NCS v3.4.1 | not built yet | - |

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
Building from `/mnt/<drive>` is slow.
