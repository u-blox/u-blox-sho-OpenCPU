# u-blox Getting Started SDK

One launcher, six module families. Build, flash and log Wi-Fi/Bluetooth firmware
for IRIS-W1, NORA-W3, NORA-W4, NORA-W5, NORA-B2 and ALMA-B2 without learning
six vendor build systems. Matter is available for the same silicon.

| Target | Module | SoC | Framework | Board target |
|--------|--------|-----|-----------|--------------|
| `iris-w1` | IRIS-W10x | NXP RW612/RW610 | MCUXpresso SDK (west/CMake) | `rdrw612bga` |
| `nora-w3` | NORA-W30x | Realtek RTL8720DF | Realtek Ameba-D RTOS SDK | `project_hp` |
| `nora-w4` | NORA-W40x | Espressif ESP32-C6 | ESP-IDF | `esp32c6` |
| `nora-w5` | NORA-W50x/W51x | TI CC3501E/CC3551E | SimpleLink Wi-Fi SDK | `LP_EM_CC35X1` |
| `nora-b2` | NORA-B20x/B21x/B22x | Nordic nRF54L15/L10/L05 | nRF Connect SDK (Zephyr) | `ubx_evknorab2/nrf54l15/cpuapp` |
| `alma-b2` | ALMA-B20x/B21x | Nordic nRF54LM20A/B | nRF Connect SDK (Zephyr) | `nrf54lm20dk/nrf54lm20a/cpuapp` |

This is the **Open CPU** SDK: your application runs on the module. The
u-connectXpress parts (NORA-W36x, W56x, W57x, B26x, B27x) ship with AT-command
firmware pre-flashed and are configured by a host, not built from here.

ALMA-B2 is under development and has no u-blox board definition yet, so it
builds against Nordic's nRF54LM20 DK. See [docs/alma_b2_README.md](docs/alma_b2_README.md).

## Quick start

```cmd
REM Windows
ubx-sdk.cmd nora-w4 --doctor
ubx-sdk.cmd nora-w4 --clone --install --build hello_world
```

```bash
# Linux / WSL2 / macOS
./ubx-sdk.sh nora-w4 --doctor
./ubx-sdk.sh nora-w4 --clone --install --build hello_world
```

`ubx-sdk --help` lists every target and flag. Flags are combinable and always
run in a fixed order — `--doctor` -> `--clone` -> `--install` -> `--build-sdk` ->
`--rf-config` -> `--list` -> `--clean` -> `--build` -> `--flash` -> `--mac` ->
`--log` — so a full rebuild-and-run is one line:

```bash
./ubx-sdk.sh iris-w1 --clean --build demo_apps/hello_world --flash --log
```

`--list` shows what a target can build: the examples in the fetched vendor SDK.
Run it after `--clone`:

```bash
./ubx-sdk.sh nora-w5 --list
```

## Module configuration (RF calibration, TX power, regulatory)

The vendor SDKs ship RF data for the vendor's own reference board. Firmware
built that way is **not regulatory compliant** on a u-blox module. `--rf-config`
applies the u-blox calibration, TX power limits and flash driver for a specific
part number before the build:

```bash
./ubx-sdk.sh nora-w3 --variant NORA-W301 --region ETSI --rf-config --build project_hp
./ubx-sdk.sh iris-w1 --variant IRIS-W101-00B --rf-config --build demo_apps/hello_world
```

What gets applied is declared per target in `modules/<TARGET>/profile.json`; the
assets themselves stay in the per-module folders at the repository root and are
referenced, never duplicated. `--doctor` reports whether the configuration is
applied, `--mac` reports the module's MAC / Bluetooth device address. See
`modules/README.md`.

The launcher picks the shared `.venv` if there is one, hops into WSL2 for
targets that only build on Linux, and passes anything after `--` straight
through to the vendor driver:

```bash
./ubx-sdk.sh iris-w1 --build hello_world -- --config release
```

## Matter (optional)

Matter works through `ubx-matter` for all six targets. You can ignore the
launcher completely if you are not building Matter — nothing in the plain SDK
flow touches it, and the multi-GB Matter SDKs are only fetched when you ask.

```bash
./ubx-matter.sh nora-w4 --doctor
./ubx-matter.sh nora-w4 --clone --install
./ubx-matter.sh nora-w4 --list
./ubx-matter.sh nora-w4 --build light
```

Only the examples each vendor's Matter SDK ships are listed and built; this
layer adds no u-blox application code. The set differs per vendor, so run
`--list` per target.

For IRIS-W1, NORA-W3, NORA-W4 and NORA-W5, Matter is a separate vendor SDK,
fetched by `--clone` into `~/ubx-matter/<TARGET>` inside WSL2 (or
`UBX_MATTER_ROOT`). These toolchains are Linux-only, so on Windows every
`ubx-matter` action for them hops into WSL2. `--build` is wired for NORA-W4 and
NORA-W5; IRIS-W1 and NORA-W3 examples are listed only for now.

| Target | Vendor Matter SDK | Default example |
|--------|-------------------|-----------------|
| `iris-w1` | `NXP/matter` | `lighting-app` (list only) |
| `nora-w3` | `ameba-rtos-matter` | `light` (list only) |
| `nora-w4` | `esp-matter` | `light` |
| `nora-w5` | `TexasInstruments/matter` | `lighting-app` |
| `nora-b2`, `alma-b2` | nRF Connect SDK | `light_bulb` |

NORA-W5 Matter needs the `Ubuntu-22.04` WSL2 distro (TI supports nothing else)
plus the Linux SysConfig and SimpleLink Wi-Fi Toolbox installed under `~/ti`.

Matter builds also use the vendor's reference-board RF data; `--rf-config` is
an `ubx-sdk` flag and is not applied to the Matter SDKs. See the Matter guide
for applying it on NORA-W4.

NORA-B2 and ALMA-B2 instead get Matter from the nRF Connect SDK itself, so
`--clone` fetches the same NCS workspace `ubx-sdk` uses and nothing extra is
downloaded. `--list` shows the `nrf/samples/matter` apps, and `--flash`/`--log`
work too:

```bash
./ubx-matter.sh nora-b2 --list
./ubx-matter.sh nora-b2 --build light_bulb --flash --log
```

See [docs/matter_README.md](docs/matter_README.md).

## Layout

```
GettingStartedSDK/
├── ubx-sdk.cmd / .sh             SDK launcher (start here)
├── ubx-matter.cmd / .sh          Optional Matter launcher
├── ubx.code-workspace            VS Code workspace
├── scripts/                      Per-target drivers + venv helpers
│   └── matter_vendor/            Per-vendor Matter setup/build scripts
├── modules/<T>/profile.json      RF calibration / TX power profiles
├── targets/<T>/sdk/              Vendor SDKs, fetched on demand (gitignored)
├── targets/<T>/config/           Per-host tool cache
└── docs/                         Per-module guides and build references
```

Vendor SDKs are never committed. Each target's `--clone` fetches only what that
module needs, so a fresh checkout stays small. Matter SDKs live outside the
repository, in `~/ubx-matter/` inside WSL2.

## Setup

The launcher works with any Python 3.10+. For an isolated environment with
`west` and the serial tooling pre-installed:

```bash
python scripts/setup_venv.py
```

IRIS-W1 additionally needs the Arm GNU Toolchain:

```bash
export ARMGCC_DIR="/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
```

NORA-B2 and ALMA-B2 need a Zephyr/nRF Connect toolchain. The quickest route is
nRF Connect for Desktop and its Toolchain Manager; `--doctor` reports what is
still missing. An existing `~/ncs` workspace is detected and reused.

## Documentation

| Document | Contents |
|----------|----------|
| [docs/iris_w1_README.md](docs/iris_w1_README.md) | IRIS-W1 (NXP RW612) |
| [docs/nora_w3_README.md](docs/nora_w3_README.md) | NORA-W3 (Realtek, WSL2) |
| [docs/nora_w4_README.md](docs/nora_w4_README.md) | NORA-W4 (ESP32-C6) |
| [docs/nora_w5_README.md](docs/nora_w5_README.md) | NORA-W5 (TI CC3501E/CC3551E) |
| [docs/nora_b2_README.md](docs/nora_b2_README.md) | NORA-B2 (Nordic nRF54L) |
| [docs/alma_b2_README.md](docs/alma_b2_README.md) | ALMA-B2 (Nordic nRF54LM20) |
| [docs/BUILD_ALL_EXAMPLES.md](docs/BUILD_ALL_EXAMPLES.md) | Full build guide |
| [docs/BUILD_INSTRUCTIONS.md](docs/BUILD_INSTRUCTIONS.md) | Build instructions |
| [docs/BUILD_TEST_RESULTS.md](docs/BUILD_TEST_RESULTS.md) | Build verification status |
| [docs/QUICK_BUILD_REFERENCE.md](docs/QUICK_BUILD_REFERENCE.md) | Command cheat sheet |
| [docs/VENV_SETUP.md](docs/VENV_SETUP.md) | Virtual environment details |
| [docs/WORKSPACE_SETUP.md](docs/WORKSPACE_SETUP.md) | VS Code workspace |
| [docs/REVIEWERS_GUIDE.md](docs/REVIEWERS_GUIDE.md) | Review procedure |
| [docs/matter_README.md](docs/matter_README.md) | Matter SDKs and vendor examples |
| [modules/README.md](modules/README.md) | Module config profile schema |
