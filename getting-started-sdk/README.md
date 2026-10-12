# u-blox Getting Started SDK

One launcher, six module families. Build, flash and log Wi-Fi/Bluetooth firmware
for IRIS-W10, NORA-W30, NORA-W40, NORA-W50-W51, NORA-B20-B21-B22 and ALMA-B20-B21 without learning
six vendor build systems. Matter is available for the same silicon.

| Target | Module | SoC | Framework | Board target |
|--------|--------|-----|-----------|--------------|
| `iris-w10` | IRIS-W10x | NXP RW612/RW610 | MCUXpresso SDK (west/CMake) | `rdrw612bga` |
| `nora-w30` | NORA-W30x | Realtek RTL8720DF | Realtek Ameba-D RTOS SDK | `project_hp` |
| `nora-w40` | NORA-W40x | Espressif ESP32-C6 | ESP-IDF | `esp32c6` |
| `nora-w50-w51` | NORA-W50x/W51x | TI CC3501E/CC3551E | SimpleLink Wi-Fi SDK | `LP_EM_CC35X1` |
| `nora-b20-b21-b22` | NORA-B20x/B21x/B22x | Nordic nRF54L15/L10/L05 | nRF Connect SDK (Zephyr) | `ubx_evknorab2/nrf54l15/cpuapp` |
| `alma-b20-b21` | ALMA-B20x/B21x | Nordic nRF54LM20A/B | nRF Connect SDK (Zephyr) | `nrf54lm20dk/nrf54lm20a/cpuapp` |

This is the **Open CPU** SDK: your application runs on the module. The
u-connectXpress parts (NORA-W36x, W56x, W57x, B26x, B27x) ship with AT-command
firmware pre-flashed and are configured by a host, not built from here.

ALMA-B20-B21 is under development and has no u-blox board definition yet, so it
builds against Nordic's nRF54LM20 DK. See [docs/alma_b20_b21_README.md](docs/alma_b20_b21_README.md).

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
run in a fixed order — `--doctor` -> `--clone` -> `--install` -> `--build-sdk` ->
`--rf-config` -> `--list` -> `--clean` -> `--build` -> `--flash` -> `--mac-set` ->
`--mac` -> `--log` — so a full rebuild-and-run is one line:

```bash
./ubx-sdk.sh iris-w10 --clean --build demo_apps/hello_world --flash --log
```

`--list` shows what a target can build: the examples in the fetched vendor SDK,
followed by the u-blox examples from the repository as `ubx/<name>`.
Run it after `--clone`:

```bash
./ubx-sdk.sh nora-w50-w51 --list
./ubx-sdk.sh nora-w40 --build ubx/rf-calibration --flash --log
```

`--dry-run` prints the commands a flag combination would run, in order,
without running anything (works for `ubx-matter` too):

```bash
./ubx-sdk.sh nora-w40 --dry-run --clean --build hello_world --flash --log
```

## Module configuration (RF calibration, TX power, regulatory)

The vendor SDKs ship RF data for the vendor's own reference board. Firmware
built that way is **not regulatory compliant** on a u-blox module. `--rf-config`
applies the u-blox calibration, TX power limits and flash driver for a specific
part number before the build:

```bash
./ubx-sdk.sh nora-w30 --variant NORA-W301 --region ETSI --rf-config --build project_hp
./ubx-sdk.sh iris-w10 --variant IRIS-W101-00B --rf-config --build demo_apps/hello_world
```

What gets applied is declared per target in `modules/<target>/profile.json`; the
assets themselves stay in the per-module folders at the repository root and are
referenced, never duplicated. `--doctor` reports whether the configuration is
applied, `--mac` reports the module's MAC / Bluetooth device address, and
`--mac-set <ADDR>` shows how to use another one (`--burn` stores it in eFuse
where a host tool exists; irreversible). See `modules/README.md`.

The launcher picks the shared `.venv` if there is one, hops into WSL2 for
targets that only build on Linux, and passes anything after `--` straight
through to the vendor driver:

```bash
./ubx-sdk.sh iris-w10 --build hello_world -- --config release
```

## Matter (optional)

Matter works through `ubx-matter` for all six targets. You can ignore the
launcher completely if you are not building Matter — nothing in the plain SDK
flow touches it, and the multi-GB Matter SDKs are only fetched when you ask.

```bash
./ubx-matter.sh nora-w40 --doctor
./ubx-matter.sh nora-w40 --clone --install
./ubx-matter.sh nora-w40 --list
./ubx-matter.sh nora-w40 --build light
```

Only the examples each vendor's Matter SDK ships are listed and built; this
layer adds no u-blox application code. The set differs per vendor, so run
`--list` per target.

For IRIS-W10, NORA-W30, NORA-W40 and NORA-W50-W51, Matter is a separate vendor SDK,
fetched by `--clone` into `~/ubx-matter/<target>` inside WSL2 (or
`UBX_MATTER_ROOT`). These toolchains are Linux-only, so on Windows every
`ubx-matter` action for them hops into WSL2. `--build` is wired for NORA-W40 and
NORA-W50-W51; IRIS-W10 and NORA-W30 examples are listed only for now.

| Target | Vendor Matter SDK | Default example |
|--------|-------------------|-----------------|
| `iris-w10` | `NXP/matter` | `lighting-app` (list only) |
| `nora-w30` | `ameba-rtos-matter` | `light` (list only) |
| `nora-w40` | `esp-matter` | `light` |
| `nora-w50-w51` | `TexasInstruments/matter` | `lighting-app` |
| `nora-b20-b21-b22`, `alma-b20-b21` | nRF Connect SDK | `light_bulb` |

NORA-W50-W51 Matter needs the `Ubuntu-22.04` WSL2 distro (TI supports nothing else)
plus the Linux SysConfig and SimpleLink Wi-Fi Toolbox installed under `~/ti`.

Matter builds also use the vendor's reference-board RF data; `--rf-config` is
an `ubx-sdk` flag and is not applied to the Matter SDKs. See the Matter guide
for applying it on NORA-W40.

NORA-B20-B21-B22 and ALMA-B20-B21 instead get Matter from the nRF Connect SDK itself, so
`--clone` fetches the same NCS workspace `ubx-sdk` uses and nothing extra is
downloaded. `--list` shows the `nrf/samples/matter` apps, and `--flash`/`--log`
work too:

```bash
./ubx-matter.sh nora-b20-b21-b22 --list
./ubx-matter.sh nora-b20-b21-b22 --build light_bulb --flash --log
```

See [docs/matter_README.md](docs/matter_README.md).

## Layout

```
getting-started-sdk/
├── ubx-sdk.cmd / .sh             SDK launcher (start here)
├── ubx-matter.cmd / .sh          Optional Matter launcher
├── ubx.code-workspace            VS Code workspace
├── scripts/                      Per-target drivers + venv helpers
│   └── matter_vendor/            Per-vendor Matter setup/build scripts
├── modules/<T>/profile.json      RF calibration / TX power profiles
├── modules/<T>/config/           Per-host tool cache (gitignored)
├── sdks/<vendor>/<version>/      Vendor SDKs, fetched on demand (gitignored)
├── tests/                        pytest suite for the launchers and drivers
└── docs/                         Per-module guides and build references
```

Vendor SDKs are never committed. Each target's `--clone` fetches only what that
module needs, so a fresh checkout stays small.

Where things live:

| What | Where |
|------|-------|
| u-blox RF data, patches, board files, examples | repository root: `esp-idf/nora-w40/`, `mcuxpresso/iris-w10/`, `ameba-rtos-d/nora-w30/`, `zephyr/`, ... |
| The tooling (this folder) | `getting-started-sdk/` |
| ESP-IDF, MCUXpresso, Ameba-D, SimpleLink | `getting-started-sdk/sdks/<vendor>/<version>`, e.g. `sdks/esp-idf/master`; `--clone <tag>` fetches another version next to it |
| nRF Connect SDK (NORA-B20-B21-B22, ALMA-B20-B21) | `C:\ncs\<version>` or `~/ncs/<version>`, shared with Nordic's own tools |
| Matter SDKs | `~/ubx-matter/<target>` inside WSL2 |

The repository-root folders are named after the SDK they belong to, but they
only hold u-blox files; the SDK itself is never cloned there. `--rf-config`
copies or patches those files into the fetched SDK.

## Setup

The launcher works with any Python 3.10+. For an isolated environment with
`west` and the serial tooling pre-installed:

```bash
python scripts/setup_venv.py
```

IRIS-W10 additionally needs the Arm GNU Toolchain. The driver finds it on its own
(standard Arm installer paths, the MCUXpresso Installer's `~/.mcuxpressotools`,
or `arm-none-eabi-gcc` on `PATH`) and passes it to the build as `ARMGCC_DIR`;
`--doctor` shows which one it picked. Set `ARMGCC_DIR` yourself only to force a
specific toolchain.

NORA-B20-B21-B22 and ALMA-B20-B21 need a Zephyr/nRF Connect toolchain. The quickest route is
nRF Connect for Desktop and its Toolchain Manager; `--doctor` reports what is
still missing. Existing NCS workspaces are detected (`C:\ncs\*`, `~/ncs*`);
`--clone` creates one in `C:\ncs\v3.4.1` (or `~/ncs/v3.4.1` on Linux).

Every `--clone` checks free disk space against an estimate for that SDK first
(NCS about 15 GB, MCUXpresso 3 GB board-only / 8 GB full, ESP-IDF 3 GB, Ameba-D
2 GB) and stops if it will not fit. Set `UBX_SKIP_SPACE_CHECK=1` to override.

## Tests

The launchers, the Matter driver and the module configuration have a pytest
suite. It needs no vendor SDK, toolchain, WSL2 or hardware: driver calls are
recorded instead of executed, and the end-to-end tests use `--dry-run`.

```bash
python -m pytest tests -q
```

`setup_venv.py` installs pytest. Run the suite on both Windows and WSL2/Linux;
a few tests are platform-specific and skip elsewhere.

Run it with the venv's Python (activate the venv, or call
`.venv\Scripts\python.exe -m pytest tests -q` on Windows). A system Python
with other pytest plugins installed, such as MSYS2's, can fail before any test
runs.

CI runs on every push that touches `getting-started-sdk/`:

| Where | Jobs |
|-------|------|
| GitLab (`.gitlab-ci.yml`) | pytest on Linux, Python 3.10 and 3.12; ruff; shellcheck |
| GitHub Actions (`.github/workflows/getting-started-sdk.yml`, runs on the mirror) | pytest on Linux and Windows, Python 3.10 and 3.12; ruff; shellcheck |

Run the linters locally before pushing (`pip install ruff==0.17.0 shellcheck-py`):

```bash
ruff check --isolated --target-version py310 --select E4,E7,E9,F scripts tests
shellcheck -S warning ubx-*.sh scripts/matter_vendor/*.sh
```

## Documentation

| Document | Contents |
|----------|----------|
| [docs/iris_w10_README.md](docs/iris_w10_README.md) | IRIS-W10 (NXP RW612) |
| [docs/nora_w30_README.md](docs/nora_w30_README.md) | NORA-W30 (Realtek, WSL2) |
| [docs/nora_w40_README.md](docs/nora_w40_README.md) | NORA-W40 (ESP32-C6) |
| [docs/nora_w50_w51_README.md](docs/nora_w50_w51_README.md) | NORA-W50-W51 (TI CC3501E/CC3551E) |
| [docs/nora_b20_b21_b22_README.md](docs/nora_b20_b21_b22_README.md) | NORA-B20-B21-B22 (Nordic nRF54L) |
| [docs/alma_b20_b21_README.md](docs/alma_b20_b21_README.md) | ALMA-B20-B21 (Nordic nRF54LM20) |
| [docs/BUILD_ALL_EXAMPLES.md](docs/BUILD_ALL_EXAMPLES.md) | Full build guide |
| [docs/BUILD_INSTRUCTIONS.md](docs/BUILD_INSTRUCTIONS.md) | Build instructions |
| [docs/BUILD_TEST_RESULTS.md](docs/BUILD_TEST_RESULTS.md) | Build verification status |
| [docs/QUICK_BUILD_REFERENCE.md](docs/QUICK_BUILD_REFERENCE.md) | Command cheat sheet |
| [docs/VENV_SETUP.md](docs/VENV_SETUP.md) | Virtual environment details |
| [docs/WORKSPACE_SETUP.md](docs/WORKSPACE_SETUP.md) | VS Code workspace |
| [docs/REVIEWERS_GUIDE.md](docs/REVIEWERS_GUIDE.md) | Review procedure |
| [docs/matter_README.md](docs/matter_README.md) | Matter SDKs and vendor examples |
| [modules/README.md](modules/README.md) | Module config profile schema |
