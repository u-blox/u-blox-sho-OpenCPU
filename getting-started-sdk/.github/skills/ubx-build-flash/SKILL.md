---
name: ubx-build-flash
description: 'Build, flash, log and troubleshoot firmware for u-blox Open CPU modules (IRIS-W10, NORA-W30, NORA-W40, NORA-W50-W51, NORA-B20-B21-B22, ALMA-B20-B21) with the ubx-sdk launcher. Use when: building an example, first-time setup, flashing an EVK, reading the serial log, a build or clone fails, toolchain not found, WSL2 hop, picking an NCS workspace, finding the output binary.'
argument-hint: '<target> and what you want to do, e.g. "nora-w40 build and flash hello_world"'
---

# Build, flash and log with ubx-sdk

## Procedure

1. Resolve the target key (`iris-w10`, `nora-w30`, `nora-w40`, `nora-w50-w51`,
   `nora-b20-b21-b22`, `alma-b20-b21`). A u-connectXpress part (W36x, W56x,
   W57x, B26x, B27x) cannot be built here; say so.
2. Run `--doctor` first and read what is missing before proposing fixes.
3. Use the launcher from the SDK root: `ubx-sdk.cmd` on Windows,
   `./ubx-sdk.sh` elsewhere. Combine flags in one call; they run in a fixed order.
4. For hardware that ships to customers, include `--variant <PART> --rf-config`
   (see skill `ubx-module-config`). A plain `--build` is not regulatory compliant.
5. Use `--dry-run` to show what a flag combination will execute.
6. After a real build, record it in `docs/BUILD_TEST_RESULTS.md`.
7. Never work around the launcher (manual `make`, `west`, `idf.py`, driver
   calls in WSL2, deleting build folders, own flash commands). If a step fails
   because a script is wrong or missing a feature, fix the script with a test,
   then rerun the same launcher command.

## First build per target

```bash
./ubx-sdk.sh iris-w10 --doctor --clone --install --build demo_apps/hello_world --flash --log
./ubx-sdk.sh nora-w30 --clone --build project_hp                 # hops into WSL2 on Windows
./ubx-sdk.sh nora-w40 --clone --install --build hello_world --flash --log
./ubx-sdk.sh nora-w50-w51 --clone --build-sdk --build network_terminal
./ubx-sdk.sh nora-b20-b21-b22 --clone --install --build hello_world --flash --log
./ubx-sdk.sh alma-b20-b21 --build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp
```

u-blox examples from the repository build the same way: `--list` shows them
as `ubx/<name>`, e.g. `nora-w40 --variant NORA-W401 --rf-config --build ubx/rf-calibration`.

## Where things end up

| Target | SDK | Firmware |
|--------|-----|----------|
| IRIS-W10 | `sdks/mcuxpresso-sdk/<version>` | `<workspace>/build/<config>/<example>.{elf,bin}` |
| NORA-W30 | `sdks/ameba-rtos-d/<version>` | `.../GCC-RELEASE/project_hp/asdk/image/km4_image2_all.bin` |
| NORA-W40 | `sdks/esp-idf/<version>` | `<example>/build/<project>.bin` |
| NORA-W50-W51 | `sdks/simplelink-wifi/<version>/` | `<example>/<rtos>/<board>/<toolchain>/*.out` |
| NORA-B20-B21-B22, ALMA-B20-B21 | `C:\ncs\<rev>` or `~/ncs/<rev>` | `<ncs>/build/<sample>/zephyr/zephyr.{elf,hex,bin}` |

## Flash and log

| Target | Probe |
|--------|-------|
| IRIS-W10 | J-Link / MCU-Link; J-Link device is `RW612`, not the board name |
| NORA-W40 | USB serial via `idf.py flash`; `--log` runs `idf.py monitor` in the example |
| NORA-W50-W51 | XDS110 (`--flash <serial>`) |
| NORA-B20-B21-B22, ALMA-B20-B21 | on-board J-Link OB via `west flash -r nrfutil` (needs `nrfutil`) |
| NORA-W30 | not wired (`--flash` is skipped); use Realtek ImageTool |

`--log [PORT]` auto-detects the port when omitted.

## Environment variables

| Variable | Use |
|----------|-----|
| `ARMGCC_DIR` | Force an Arm GNU toolchain for IRIS-W10 (root, not `bin/`); normally auto-detected |
| `NORA_W50_W51_WORKSPACE` | Override the NORA-W50-W51 workspace |
| `ZEPHYR_BASE` | Points the Nordic driver at an existing NCS workspace |
| `UBX_SKIP_SPACE_CHECK=1` | Clone even when the disk-space estimate says no |
| `UBX_WSL_DISTRO` | WSL2 distro for the hop |

## Troubleshooting

- **Arm toolchain not found (IRIS-W10)**: install the Arm GNU Toolchain or the
  MCUXpresso Installer; the driver searches the Arm install paths,
  `~/.mcuxpressotools` and `PATH`. `--doctor` shows the pick.
- **NORA-W30 on Windows**: the Realtek build is Linux-only; the launcher hops
  into WSL2. Building from `/mnt/<drive>` is slow but works.
- **WSL2 itself fails** (does not start, hangs, `Wsl/Service/...` error): restart
  its compute service from an Administrator prompt, then rerun:
  `net stop vmcompute` and `net start vmcompute`. The launcher prints this after
  any failed WSL2 run.
- **NCS too old**: an existing `~/ncs` may predate `ubx_evknorab2` (not in
  v2.9.0). The driver reports the version; `--clone` fetches the pinned one into
  `<system drive>/ncs/<rev>`. `nordic_ncs_build.py <target> use [path]` selects one.
- **Clone stops on disk space**: free space or set `UBX_SKIP_SPACE_CHECK=1`.
  A full drive shows up as unrelated compiler errors.
- **CMake cache points at an old path** after the SDK or SDK folder moved:
  `--clean` the example once.
- **ESP-IDF example builds for ESP32 instead of ESP32-C6**: the driver runs
  `set-target esp32c6`; if a stale `sdkconfig` disagrees, `--clean` it.
- **`ubx/rf-calibration` fails to link**: it needs `--rf-config` first.
- **Windows venv used from WSL2 or the reverse**: they are not interchangeable;
  the shims pick the right one, so run through the launcher.
