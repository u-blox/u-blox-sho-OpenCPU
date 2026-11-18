# Quick Build Reference

Command cheat sheet for all six Getting Started SDK targets. Everything goes
through the launcher: `ubx-sdk.cmd` on Windows, `./ubx-sdk.sh` on
Linux/WSL2/macOS. The examples below use the shell form.

---

## Targets

| Target | SoC | Framework | Host notes |
|--------|-----|-----------|------------|
| `iris-w10` | NXP RW612/RW610 | MCUXpresso | Arm GNU Toolchain (auto-detected) |
| `nora-w30` | Realtek RTL8720DF | Ameba-D | Linux/WSL2 only (auto hop) |
| `nora-w40` | Espressif ESP32-C6 | ESP-IDF | Any |
| `nora-w50-w51` | TI CC3501E/CC3551E | SimpleLink | Any |
| `nora-b20-b21-b22` | Nordic nRF54L15/L10/L05 | nRF Connect SDK | Any |
| `alma-b20-b21` | Nordic nRF54LM20A/B | nRF Connect SDK | Any; Nordic DK board |
| `alma-w10-w11` | Nordic nRF7120/nRF7120E | nRF Connect SDK (pre-release) | Any; Nordic DK board |

u-connectXpress parts (NORA-W36x, W56x, W57x, B26x, B27x, ALMA-W16x) ship pre-flashed with
AT-command firmware and are not built from this Open CPU SDK.

---

## Flags

Combinable, and always executed in this order:

```
--doctor -> --clone -> --install -> --build-sdk -> --rf-config -> --list -> --clean -> --build -> --flash -> --mac-set -> --mac -> --log
```

| Flag | Purpose |
|------|---------|
| `--doctor` | Verify host tools for the target; a failure does not stop a following `--clone`/`--install` |
| `--clone [VERSION]` | Fetch the vendor SDK on demand into `sdks/<vendor>/<VERSION>` (branch or tag; default: the release this SDK is tested with, `main`/`master` for the newest code) |
| `--full` | With `--clone`, IRIS-W10 only: the whole MCUXpresso SDK instead of the RW612 board set |
| `--install` | Install/refresh the SDK's own tool environment |
| `--build-sdk` | NORA-W50-W51 only: build the SDK libraries |
| `--rf-config` | Apply the u-blox output power, calibration and SDK patches |
| `--variant <PART>` | Module part number, e.g. `NORA-W301`, `IRIS-W101-00B` |
| `--region <DOMAIN>` | Regulatory domain: FCC, ISED, ETSI, MKK, ACMA |
| `--set KEY=VALUE` | With `--rf-config`: override a profile variable, e.g. `flash_part=macronix-8mb` (IRIS-W10) |
| `--list` | List vendor examples and u-blox examples (`ubx/<name>`) |
| `--build [NAME]` | Build an example (target default if omitted); `ubx/<name>` for a u-blox one |
| `--clean` | Clean build artifacts |
| `--clean-all` | Remove the SDK version in use (other versions in `sdks/<vendor>/` stay) |
| `--flash [SERIAL]` | Flash via the target's debug probe; IRIS-W10 `--flash COM<n>` uses the boot ROM |
| `--mac-set ADDR [PORT]` | Show how to use another MAC address |
| `--burn` | With `--mac-set`: store it in eFuse where supported (irreversible) |
| `--mac [PORT]` | Report the module MAC / Bluetooth device address |
| `--log [PORT]` | Open the serial console (port auto-detected); typed lines are sent to the module |
| `--wsl` / `--no-wsl` | Force or suppress the automatic hop into WSL2 |
| `--dry-run` | Print the commands the other flags would run, without running them |
| `--` | Pass everything after it verbatim to the driver's build step (`--build` only) |

Firmware built without `--rf-config` uses the vendor reference-board RF data and
is not regulatory compliant. `--doctor` reports whether it has been applied.

---

## First build, per target

### IRIS-W10 (NXP RW612/RW610)
```bash
./ubx-sdk.sh iris-w10 --doctor                      # shows the Arm toolchain it found
./ubx-sdk.sh iris-w10 --clone                       # board-only, about 2 GB
./ubx-sdk.sh iris-w10 --build demo_apps/hello_world --flash --log
```

### NORA-W30 (Realtek RTL8720DF)
```bash
./ubx-sdk.sh nora-w30 --doctor
./ubx-sdk.sh nora-w30 --clone --build project_lp
./ubx-sdk.sh nora-w30 --build project_hp --flash --log
```
Linux-only build system. Run it from Windows anyway - the launcher builds in
WSL2 and flashes over J-Link on Windows.

### NORA-W40 (Espressif ESP32-C6)
```bash
./ubx-sdk.sh nora-w40 --doctor
./ubx-sdk.sh nora-w40 --clone --install --build hello_world --flash --log
```

### NORA-W50-W51 (TI CC3501E/CC3551E)
```bash
./ubx-sdk.sh nora-w50-w51 --doctor
./ubx-sdk.sh nora-w50-w51 --clone --build-sdk --build network_terminal
```

### NORA-B20-B21-B22 (Nordic nRF54L)
```bash
./ubx-sdk.sh nora-b20-b21-b22 --doctor
./ubx-sdk.sh nora-b20-b21-b22 --clone --install --build hello_world --flash --log
```
Existing NCS workspaces (`C:\ncs\*`, `~/ncs*`, `ZEPHYR_BASE`) are detected and
the one with the board is used; `--clone` creates `C:\ncs\v3.4.1` (about 15 GB).
Pick one explicitly with `python scripts/nordic_ncs_build.py nora-b20-b21-b22 use <path>`.

### ALMA-B20-B21 (Nordic nRF54LM20)
```bash
./ubx-sdk.sh alma-b20-b21 --doctor
./ubx-sdk.sh alma-b20-b21 --clone --install --build hello_world --flash --log
./ubx-sdk.sh alma-b20-b21 --build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp
```
Under development - builds against Nordic's nRF54LM20 DK, not a u-blox board.

### ALMA-W10-W11 (Nordic nRF7120)
```bash
./ubx-sdk.sh alma-w10-w11 --doctor
./ubx-sdk.sh alma-w10-w11 --clone --install --build hello_world --flash --log
./ubx-sdk.sh alma-w10-w11 --build hello_world -- --board nrf7120dk/nrf7120e/cpuapp
```
Pinned to an NCS pre-release in its own workspace; builds against Nordic's
nRF7120 DK, not a u-blox board.

---

## Common operations

| Task | Command |
|------|---------|
| Check tools | `./ubx-sdk.sh <target> --doctor` |
| Fetch the SDK | `./ubx-sdk.sh <target> --clone` |
| See what you can build | `./ubx-sdk.sh <target> --list` |
| Rebuild from clean and run | `./ubx-sdk.sh <target> --clean --build NAME --flash --log` |
| Start over completely | `./ubx-sdk.sh <target> --clean-all --clone` |
| Pass a driver option | `./ubx-sdk.sh <target> --build NAME -- --config release` |
| Create the shared venv | `./ubx-sdk.sh --setup-venv` |

---

## Build output

| Target | Artifacts | Location |
|--------|-----------|----------|
| IRIS-W10 | `<example>.elf`, `.bin`, `.hex` | `sdks/mcuxpresso-sdk/<version>/build/` |
| NORA-W30 | `*.bin` | in-source, under the example directory |
| NORA-W40 | `*.elf`, `*.bin` | `<esp-idf>/examples/<example>/build/` |
| NORA-W50-W51 | `*.out`, `*.map` | `<examples>/<rtos>/<board>/<toolchain>/` |
| NORA-B20-B21-B22 | `zephyr.elf/.hex/.bin` | `<ncs>/build/<sample>/<sample>/zephyr/` |
| ALMA-B20-B21 | `zephyr.elf/.hex/.bin` | `<ncs>/build/<sample>/<sample>/zephyr/` |
| ALMA-W10-W11 | `zephyr.elf/.hex/.bin` | `<ncs>/build/<sample>/<sample>/zephyr/` |

Vendor SDKs land in `sdks/<vendor>/<version>/` and are gitignored. Per-host tool
caches live in `modules/<target>/config/build.<host>.json`.

---

## Matter

`./ubx-matter.sh <target> --doctor | --clone | --install | --list | --build [example]`,
same flag order. See [matter_README.md](matter_README.md).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Any tool reported missing | `--doctor` names it; install, then re-run |
| `No Arm GNU toolchain found` | Install it, or set `ARMGCC_DIR` to the toolchain **root**, not `bin/` |
| "u-connectXpress module" error | You typed an AT-command part; use the Open CPU sibling it names |
| Build fails after an SDK update | `./ubx-sdk.sh <target> --clean --build NAME` |
| SDK clone interrupted | Re-run `--clone` |
| Stale environment | Restart the shell; for NORA-W40 re-run `--install` |
| Wrong serial port picked | Pass it: `--log COM12` or `--log /dev/ttyUSB0` |
| Nordic board target not found | Needs NCS v3.x; clone a current workspace |

---

## Related documents

Per module: [IRIS-W10](iris_w10_README.md), [NORA-W30](nora_w30_README.md),
[NORA-W40](nora_w40_README.md), [NORA-W50-W51](nora_w50_w51_README.md),
[NORA-B20-B21-B22](nora_b20_b21_b22_README.md), [ALMA-B20-B21](alma_b20_b21_README.md), [ALMA-W10-W11](alma_w10_w11_README.md).
Setup: [SETUP.md](SETUP.md).
