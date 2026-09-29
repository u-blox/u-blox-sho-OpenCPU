# u-blox Getting Started SDK

One launcher, four modules. Build, flash and log Wi-Fi/Bluetooth firmware for
IRIS-W10, NORA-W30, NORA-W40 and NORA-W50/W51 without learning four vendor
build systems. Matter is available as an optional add-on for the same silicon.

| Module | SoC | Framework | Board target |
|--------|-----|-----------|--------------|
| **IRIS-W10** | NXP RW612/RW610 | MCUXpresso SDK (west/CMake) | `rdrw612bga` |
| **NORA-W30** | Realtek RTL872x | Realtek Ameba-D RTOS SDK | `project_hp` |
| **NORA-W40** | Espressif ESP32-C6 | ESP-IDF | `esp32c6` |
| **NORA-W50/W51** | TI CC35XX | SimpleLink Wi-Fi SDK | `LP_EM_CC35X1` |

## Quick start

```cmd
REM Windows
ubx-sdk.cmd nora-w40 --doctor
ubx-sdk.cmd nora-w40 --clone --install --build hello_world
```

```bash
# Linux / WSL2 / macOS
./ubx-sdk.sh nora-w40 --doctor
./ubx-sdk.sh nora-w40 --clone --install --build hello_world
```

`ubx-sdk --help` lists every target and flag. Flags are combinable and always
run in a fixed order — `--doctor` → `--clone` → `--install` → `--build-sdk` →
`--clean` → `--build` → `--flash` → `--log` — so a full rebuild-and-run is one
line:

```bash
./ubx-sdk.sh iris-w10 --clean --build demo_apps/hello_world --flash --log
```

The launcher picks the shared `.venv` if there is one, hops into WSL2 for
targets that only build on Linux, and passes anything after `--` straight
through to the vendor driver:

```bash
./ubx-sdk.sh iris-w10 --build hello_world -- --config release
```

## Matter (optional)

Matter is a separate layer with its own launcher, `ubx-matter`. You can ignore
it completely if you are not building Matter — nothing in the plain SDK flow
touches it, and the multi-GB Matter SDKs are only fetched when you ask for
them.

```bash
./ubx-matter.sh nora-w40 --doctor
./ubx-matter.sh nora-w40 --clone
./ubx-matter.sh nora-w40 --build thermometer
```

See [matter/README.md](matter/README.md).

## Layout

```
GettingStartedSDK/
├── ubx-sdk.cmd / .sh             SDK launcher (start here)
├── ubx-matter.cmd / .sh          Optional Matter launcher
├── ubx.code-workspace            VS Code workspace
├── scripts/                      Per-target drivers + venv helpers
├── matter/                       Matter app sources, per target
├── targets/<T>/sdk/              Vendor + Matter SDKs, fetched on demand (gitignored)
├── targets/<T>/config/           Per-host tool cache
└── docs/                         Per-module guides and build references
```

Vendor SDKs are never committed. Each target's `--clone` fetches only what that
module needs, so a fresh checkout stays small.

## Setup

The launcher works with any Python 3.10+. For an isolated environment with
`west` and the serial tooling pre-installed:

```bash
python scripts/setup_venv.py
```

IRIS-W10 additionally needs the Arm GNU Toolchain:

```bash
export ARMGCC_DIR="/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
```

## Documentation

| Document | Contents |
|----------|----------|
| [docs/iris_w10_README.md](docs/iris_w10_README.md) | IRIS-W10 (NXP RW612) |
| [docs/nora_w30_README.md](docs/nora_w30_README.md) | NORA-W30 (Realtek, WSL2) |
| [docs/nora_w40_README.md](docs/nora_w40_README.md) | NORA-W40 (ESP32-C6) |
| [docs/nora_w50_w51_README.md](docs/nora_w50_w51_README.md) | NORA-W50/W51 (TI CC35XX) |
| [docs/BUILD_ALL_EXAMPLES.md](docs/BUILD_ALL_EXAMPLES.md) | Full build guide, all four |
| [docs/QUICK_BUILD_REFERENCE.md](docs/QUICK_BUILD_REFERENCE.md) | Command cheat sheet |
| [docs/VENV_SETUP.md](docs/VENV_SETUP.md) | Virtual environment details |
| [docs/WORKSPACE_SETUP.md](docs/WORKSPACE_SETUP.md) | VS Code workspace |
| [docs/REVIEWERS_GUIDE.md](docs/REVIEWERS_GUIDE.md) | Review procedure |
| [matter/README.md](matter/README.md) | Matter apps and SDKs |
