# Quick Build Reference

Command cheat sheet for all six Getting Started SDK targets. Everything goes
through the launcher: `ubx-sdk.cmd` on Windows, `./ubx-sdk.sh` on
Linux/WSL2/macOS. The examples below use the shell form.

---

## Targets

| Target | SoC | Framework | Host notes |
|--------|-----|-----------|------------|
| `iris-w1` | NXP RW612/RW610 | MCUXpresso | Needs `ARMGCC_DIR` |
| `nora-w3` | Realtek RTL8720DF | Ameba-D | Linux/WSL2 only (auto hop) |
| `nora-w4` | Espressif ESP32-C6 | ESP-IDF | Any |
| `nora-w5` | TI CC3501E/CC3551E | SimpleLink | Any |
| `nora-b2` | Nordic nRF54L15/L10/L05 | nRF Connect SDK | Any |
| `alma-b2` | Nordic nRF54LM20A/B | nRF Connect SDK | Any; Nordic DK board |

u-connectXpress parts (NORA-W36x, W56x, W57x, B26x, B27x) ship pre-flashed with
AT-command firmware and are not built from this Open CPU SDK.

---

## Flags

Combinable, and always executed in this order:

```
--doctor -> --clone -> --install -> --build-sdk -> --rf-config -> --list -> --clean -> --build -> --flash -> --mac -> --log
```

| Flag | Purpose |
|------|---------|
| `--doctor` | Verify host tools for the target |
| `--clone` | Fetch the vendor SDK on demand |
| `--install` | Install/refresh the SDK's own tool environment |
| `--build-sdk` | NORA-W5 only: build the SDK libraries |
| `--rf-config` | Apply the u-blox RF calibration / TX power configuration |
| `--variant <PART>` | Module part number, e.g. `NORA-W301`, `IRIS-W101-00B` |
| `--region <DOMAIN>` | Regulatory domain: FCC, ISED, ETSI, MKK, ACMA |
| `--list` | List available examples |
| `--build [NAME]` | Build an example (target default if omitted) |
| `--clean` | Clean build artifacts |
| `--clean-all` | Remove the fetched SDK entirely |
| `--flash [SERIAL]` | Flash via the target's debug probe |
| `--mac [PORT]` | Report the module MAC / Bluetooth device address |
| `--log [PORT]` | Open the serial monitor (port auto-detected) |
| `--wsl` / `--no-wsl` | Force or suppress the automatic hop into WSL2 |
| `--` | Pass everything after it verbatim to the driver |

Firmware built without `--rf-config` uses the vendor reference-board RF data and
is not regulatory compliant. `--doctor` reports whether it has been applied.

---

## First build, per target

### IRIS-W1 (NXP RW612/RW610)
```bash
export ARMGCC_DIR="/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
./ubx-sdk.sh iris-w1 --doctor
./ubx-sdk.sh iris-w1 --clone                       # add --full for the whole SDK
./ubx-sdk.sh iris-w1 --build demo_apps/hello_world --flash --log
```

### NORA-W3 (Realtek RTL8720DF)
```bash
./ubx-sdk.sh nora-w3 --doctor
./ubx-sdk.sh nora-w3 --clone --build project_hp
```
Linux-only build system. Run it from Windows anyway - the launcher hops into
WSL2 by itself.

### NORA-W4 (Espressif ESP32-C6)
```bash
./ubx-sdk.sh nora-w4 --doctor
./ubx-sdk.sh nora-w4 --clone --install --build hello_world --flash --log
```

### NORA-W5 (TI CC3501E/CC3551E)
```bash
./ubx-sdk.sh nora-w5 --doctor
./ubx-sdk.sh nora-w5 --clone --build-sdk --build network_terminal
```

### NORA-B2 (Nordic nRF54L)
```bash
./ubx-sdk.sh nora-b2 --doctor
./ubx-sdk.sh nora-b2 --clone --install --build hello_world --flash --log
```
An existing `~/ncs` workspace is detected and reused, so a Toolchain Manager
install needs no clone.

### ALMA-B2 (Nordic nRF54LM20)
```bash
./ubx-sdk.sh alma-b2 --clone --install --build hello_world
./ubx-sdk.sh alma-b2 --build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp
```
Under development - builds against Nordic's nRF54LM20 DK, not a u-blox board.

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
| IRIS-W1 | `<example>.elf`, `.bin` | `<west workspace>/build/<config>/` |
| NORA-W3 | `*.bin` | in-source, under the example directory |
| NORA-W4 | `*.elf`, `*.bin` | `<esp-idf>/examples/<example>/build/` |
| NORA-W5 | `*.out`, `*.map` | `<examples>/<rtos>/<board>/<toolchain>/` |
| NORA-B2 | `zephyr.elf/.hex/.bin` | `<ncs>/build/<sample>/zephyr/` |
| ALMA-B2 | `zephyr.elf/.hex/.bin` | `<ncs>/build/<sample>/zephyr/` |

Vendor SDKs land in `targets/<TARGET>/sdk/` and are gitignored. Per-host tool
caches live in `targets/<TARGET>/config/build.<host>.json`.

---

## Matter

`ubx-matter` drives all six targets:

```bash
./ubx-matter.sh <target> --doctor
./ubx-matter.sh <target> --clone
./ubx-matter.sh <target> --build <app>
```

For IRIS-W1, NORA-W3, NORA-W4 and NORA-W5 this fetches a multi-GB vendor Matter
SDK on request, and the build hops into WSL2 on Windows.

NORA-B2 and ALMA-B2 get Matter from the nRF Connect SDK instead, so `--clone`
fetches the same NCS workspace `ubx-sdk` uses, `--list` shows the
`nrf/samples/matter` apps, `--flash`/`--log` work, and there is no WSL2 hop:

```bash
./ubx-matter.sh nora-b2 --build light_bulb --flash --log
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Any tool reported missing | `--doctor` names it; install, then re-run |
| `ARMGCC_DIR not configured` | Point it at the toolchain **root**, not `bin/` |
| "u-connectXpress module" error | You typed an AT-command part; use the Open CPU sibling it names |
| Build fails after an SDK update | `./ubx-sdk.sh <target> --clean --build NAME` |
| SDK clone interrupted | Re-run `--clone`; it resumes rather than restarting |
| Stale environment | Restart the shell; for NORA-W4 re-run `--install` |
| Wrong serial port picked | Pass it: `--log COM12` or `--log /dev/ttyUSB0` |
| Nordic board target not found | Needs NCS v3.x; clone a current workspace |

---

## Related documents

| Document | Contents |
|----------|----------|
| [BUILD_ALL_EXAMPLES.md](BUILD_ALL_EXAMPLES.md) | Full build guide |
| [iris_w1_README.md](iris_w1_README.md) | IRIS-W1 details |
| [nora_w3_README.md](nora_w3_README.md) | NORA-W3 details, WSL2 setup |
| [nora_w4_README.md](nora_w4_README.md) | NORA-W4 details |
| [nora_w5_README.md](nora_w5_README.md) | NORA-W5 details |
| [nora_b2_README.md](nora_b2_README.md) | NORA-B2 details |
| [alma_b2_README.md](alma_b2_README.md) | ALMA-B2 details |
| [VENV_SETUP.md](VENV_SETUP.md) | Virtual environment |
| [WORKSPACE_SETUP.md](WORKSPACE_SETUP.md) | VS Code workspace |
