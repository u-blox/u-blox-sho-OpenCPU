# u-blox Getting Started SDK

One launcher, seven module families. Build, flash and log Wi-Fi/Bluetooth firmware
for IRIS-W10, NORA-W30, NORA-W40, NORA-W50-W51, NORA-B20-B21-B22, ALMA-B20-B21 and ALMA-W10-W11
without learning six vendor build systems. Matter is available for the same silicon.

| Target | Module | SoC | Framework | Board target |
|--------|--------|-----|-----------|--------------|
| `iris-w10` | IRIS-W10x | NXP RW612/RW610 | MCUXpresso SDK (west/CMake) | `rdrw612bga` |
| `nora-w30` | NORA-W30x | Realtek RTL8720DF | Realtek Ameba-D RTOS SDK | `project_hp` |
| `nora-w40` | NORA-W40x | Espressif ESP32-C6 | ESP-IDF | `esp32c6` |
| `nora-w50-w51` | NORA-W50x/W51x | TI CC3501E/CC3551E | SimpleLink Wi-Fi SDK | `LP_EM_CC35X1` |
| `nora-b20-b21-b22` | NORA-B20x/B21x/B22x | Nordic nRF54L15/L10/L05 | nRF Connect SDK (Zephyr) | `ubx_evknorab2/nrf54l15/cpuapp` |
| `alma-b20-b21` | ALMA-B20x/B21x | Nordic nRF54LM20A/B | nRF Connect SDK (Zephyr) | `nrf54lm20dk/nrf54lm20a/cpuapp` |
| `alma-w10-w11` | ALMA-W10x/W11x | Nordic nRF7120/nRF7120E | nRF Connect SDK pre-release (Zephyr) | `nrf7120dk/nrf7120/cpuapp` |

This is the **Open CPU** SDK: your application runs on the module. The
u-connectXpress parts (NORA-W36x, W56x, W57x, B26x, B27x, ALMA-W16x) ship with AT-command
firmware pre-flashed and are configured by a host, not built from here.

ALMA-B20-B21 is under development and has no u-blox board definition yet, so it
builds against Nordic's nRF54LM20 DK. See [docs/alma_b20_b21_README.md](docs/alma_b20_b21_README.md).
ALMA-W10-W11 needs an nRF Connect SDK pre-release and builds against Nordic's
nRF7120 DK. See [docs/alma_w10_w11_README.md](docs/alma_w10_w11_README.md).

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
applies the u-blox configuration for a specific part number to the fetched SDK
before the build:

- **Output power**: the u-blox certified TX power tables for the module.
- **Calibration**: the u-blox Wi-Fi (and on IRIS-W10 Bluetooth/802.15.4)
  calibration data that replaces the vendor reference-board values.
- **SDK patches**: small vendor-SDK changes that make the SDK load that data,
  matched to the SDK version, plus the flash driver for the module's flash part
  on IRIS-W10.

```bash
./ubx-sdk.sh nora-w30 --variant NORA-W301 --region ETSI --rf-config --build project_hp
./ubx-sdk.sh iris-w10 --variant IRIS-W101-00B --rf-config --build demo_apps/hello_world
./ubx-sdk.sh nora-w40 --variant NORA-W401 --rf-config --build ubx/rf-calibration
```

- `--variant` takes the part number; `--rf-config` without it lists the known ones.
- `--region` (FCC, ISED, ETSI, MKK, ACMA) prints which regulatory domain the
  application must select at runtime, where the module needs one.
- `--doctor` reports whether the configuration is applied and whether any file
  changed since. Vendor files are backed up as `<name>.ubx-orig`;
  `python scripts/module_config.py <target> revert` restores them.

| Target | RF configuration |
|--------|------------------|
| `iris-w10`, `nora-w30`, `nora-w40` | Available for every listed part number |
| `nora-w50-w51`, `nora-b20-b21-b22`, `alma-b20-b21`, `alma-w10-w11` | Pending: waiting for the u-blox RF assets |

What gets applied is declared per target in `modules/<target>/profile.json`; the
assets themselves stay in the per-module folders at the repository root and are
referenced, never duplicated. See [modules/README.md](modules/README.md).

## MAC address and Bluetooth device address

Every module has a unique address set in production: by u-blox (eFuse or OTP)
or, on the Nordic modules, by Nordic in the SoC (FICR). Firmware uses it
automatically; nothing has to be configured.

```bash
./ubx-sdk.sh nora-w40 --mac                          # read it from the module
./ubx-sdk.sh nora-w40 --build ubx/read-mac --flash --log   # print it on the module
./ubx-sdk.sh nora-w40 --mac-set 02:12:34:56:78:9A    # show how to use another one
```

- `--mac [PORT]` reads the address over the serial port where a host tool
  exists (NORA-W40, via esptool) and lists every address derived from it
  (Wi-Fi station, SoftAP, Bluetooth LE, IEEE 802.15.4). For the other targets it
  prints the one-line command to read it on the module.
- `--mac-set <ADDR>` prints the code to use a different address at runtime (RAM
  only, nothing is written to the module).
- `--burn` with `--mac-set` stores the address permanently, NORA-W40 only
  (espefuse, `CUSTOM_MAC` eFuse). It is **irreversible**: an eFuse can be
  written once.

| Target | Factory address | Read it | Permanent change |
|--------|-----------------|---------|------------------|
| `iris-w10` | RW612 OTP | `--build wifi_examples/wifi_cli --flash --log`, then type `wlan-mac` | No |
| `nora-w30` | Realtek eFuse | `--build project_hp --flash --log`, then type `ATW?` | From the app only (eFuse, one time) |
| `nora-w40` | ESP32-C6 eFuse (base for Wi-Fi, Bluetooth LE, 802.15.4) | `--mac` from the PC, or `--build ubx/read-mac --flash --log` | `--mac-set <ADDR> --burn` (one time) |
| `nora-w50-w51` | CC35xx factory configuration | Not yet | No |
| `nora-b20-b21-b22`, `alma-b20-b21` | Nordic FICR `DEVICEADDR` (random static Bluetooth address); u-blox programs none | `--build bluetooth/beacon --flash --log` ("advertising as ...") | No |

## Launcher details

The launcher picks the shared `.venv` if there is one, hops into WSL2 for
targets that only build on Linux, and passes anything after `--` straight
through to the driver's build step (`--build` only):

```bash
./ubx-sdk.sh iris-w10 --build hello_world -- --config release
```

## Matter (optional)

`ubx-matter` builds the Matter examples each vendor ships, for all six
targets. Nothing in the plain SDK flow touches it, and the multi-GB Matter SDKs
are only fetched when you ask.

```bash
./ubx-matter.sh nora-w40 --doctor
./ubx-matter.sh nora-w40 --clone --install --build light
./ubx-matter.sh nora-b20-b21-b22 --build light_bulb --flash --log
```

The Nordic targets use the NCS workspace `ubx-sdk` already fetched; the others
fetch a vendor Matter SDK into WSL2. `--rf-config` is not applied to the Matter
SDKs. See [docs/matter_README.md](docs/matter_README.md).

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
| ESP-IDF, MCUXpresso, Ameba-D, SimpleLink | `getting-started-sdk/sdks/<vendor>/<version>`, e.g. `sdks/esp-idf/v5.5.5`; a plain `--clone` fetches the tested release, `--clone <tag>` or `--clone main` another version next to it |
| nRF Connect SDK (NORA-B20-B21-B22, ALMA-B20-B21, ALMA-W10-W11) | `C:\ncs\<version>` or `~/ncs/<version>`, shared with Nordic's own tools |
| Matter SDKs | `~/ubx-matter/<target>` inside WSL2 |

The repository-root folders are named after the SDK they belong to, but they
only hold u-blox files; the SDK itself is never cloned there. `--rf-config`
copies or patches those files into the fetched SDK.

## Setup

The launcher works with any Python 3.10+. For an isolated environment with
`west` and the serial tooling pre-installed, run `python scripts/setup_venv.py`;
see [docs/SETUP.md](docs/SETUP.md) for the venv and the VS Code workspace.

IRIS-W10 additionally needs the Arm GNU Toolchain. The driver finds it on its own
(standard Arm installer paths, the MCUXpresso Installer's `~/.mcuxpressotools`,
or `arm-none-eabi-gcc` on `PATH`) and passes it to the build as `ARMGCC_DIR`;
`--doctor` shows which one it picked. Set `ARMGCC_DIR` yourself only to force a
specific toolchain.

NORA-B20-B21-B22, ALMA-B20-B21 and ALMA-W10-W11 need a Zephyr/nRF Connect toolchain. The quickest route is
nRF Connect for Desktop and its Toolchain Manager; `--doctor` reports what is
still missing. Existing NCS workspaces are detected (`C:\ncs\*`, `~/ncs*`);
`--clone` creates one in `C:\ncs\v3.4.1` (or `~/ncs/v3.4.1` on Linux).

Every `--clone` checks free disk space against an estimate for that SDK first
(NCS about 15 GB, MCUXpresso 3 GB board-only / 8 GB full, ESP-IDF 3 GB, Ameba-D
2 GB) and stops if it will not fit. Set `UBX_SKIP_SPACE_CHECK=1` to override.

## Tests

The pytest suite needs no vendor SDK, toolchain, WSL2 or hardware: driver calls
are recorded instead of executed, and the end-to-end tests use `--dry-run`. Run
it with the venv's Python, on Windows and on WSL2/Linux:

```bash
python -m pytest tests -q --cov=scripts --cov-report=term
```

CI (GitLab, and GitHub Actions on the mirror) runs it on Linux and Windows with
Python 3.10 and 3.14 and fails below 90% coverage, plus these linters
(`pip install ruff==0.17.0 shellcheck-py codespell==2.4.1`):

```bash
ruff check --isolated --target-version py310 --select E4,E7,E9,F scripts tests
shellcheck -S warning ubx-*.sh scripts/matter_vendor/*.sh
codespell -L ser,ameba --skip "*/config/*" README.md docs modules .github scripts tests ubx-sdk.cmd ubx-sdk.sh ubx-matter.cmd ubx-matter.sh
```

Real builds of every target, one after the other, through `ubx-sdk.cmd` on
Windows or `ubx-sdk.sh` elsewhere (`build_all_matter.py` does the same with
`ubx-matter`). Clean by default; `--incremental` skips the clean, `--setup`
adds `--clone --install` first, target keys limit the run. A full run is long;
it saves a log per step and ends with a summary table for
[docs/BUILD_TEST_RESULTS.md](docs/BUILD_TEST_RESULTS.md):

```bash
python scripts/build_all_sdk.py
```

Whether a newer vendor SDK or Matter release exists: the pins are read from the
drivers and compared with upstream tags and branches (`git ls-remote`, no
download). `[WARNING]` marks a newer stable release; move a pin only together
with its companion pins and after a build-all run:

```bash
python scripts/check_versions.py
```

## Documentation

| Document | Contents |
|----------|----------|
| [docs/QUICK_BUILD_REFERENCE.md](docs/QUICK_BUILD_REFERENCE.md) | Every flag, first build per target, troubleshooting |
| `docs/<target>_README.md` | One per module: [IRIS-W10](docs/iris_w10_README.md), [NORA-W30](docs/nora_w30_README.md), [NORA-W40](docs/nora_w40_README.md), [NORA-W50-W51](docs/nora_w50_w51_README.md), [NORA-B20-B21-B22](docs/nora_b20_b21_b22_README.md), [ALMA-B20-B21](docs/alma_b20_b21_README.md), [ALMA-W10-W11](docs/alma_w10_w11_README.md) |
| [docs/matter_README.md](docs/matter_README.md) | Matter |
| [docs/SETUP.md](docs/SETUP.md) | Python venv, VS Code workspace, Copilot context |
| [modules/README.md](modules/README.md) | Module configuration profiles |
| [docs/BUILD_TEST_RESULTS.md](docs/BUILD_TEST_RESULTS.md) | Builds verified so far |
| [docs/TODO.md](docs/TODO.md) | Open work |
