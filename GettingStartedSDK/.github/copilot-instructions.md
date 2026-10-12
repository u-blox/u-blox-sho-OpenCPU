# GitHub Copilot Build Infrastructure Guide

This file helps GitHub Copilot understand the u-blox Getting Started SDK build
infrastructure for iris-w10, nora-w30, nora-w40, nora-w50-w51, NORA-B20-B21-B22 and ALMA-B20-B21.

## Communication Preferences

- **Emoji usage:** Minimal - focus on clear technical information without decorative elements
- **Response style:** Concise and direct
- **Documentation:** Straightforward without embellishment
- **Focus:** Technical accuracy and efficiency

## Project Context

**Repository:** u-blox-sho-OpenCPU (GitLab)
**Primary Work:** Building firmware for 6 u-blox wireless module families
**Build Infrastructure:** GettingStartedSDK/ folder with consolidated scripts
**Current Branch:** cmag_getting_started_sdk (review branch) or master

### Module Specifications

| Target | Module | SoC | Framework | Board Target | Features |
|--------|--------|-----|-----------|--------------|----------|
| `iris-w10` | IRIS-W10x | NXP RW612/RW610 | MCUXpresso SDK (west/CMake) | rdrw612bga | Wi-Fi 6, Bluetooth LE 5.4, optional Thread |
| `nora-w30` | NORA-W30x | Realtek RTL8720DF | Realtek RTOS SDK | N/A | Wi-Fi, Bluetooth (needs WSL2/Linux) |
| `nora-w40` | NORA-W40x | Espressif ESP32-C6 | ESP-IDF | esp32c6 | Wi-Fi 6 (2.4 GHz), Bluetooth LE 5.3, Thread/Zigbee |
| `nora-w50-w51` | NORA-W50x/W51x | TI CC3501E/CC3551E | SimpleLink Wi-Fi SDK | LP_EM_CC35X1 | Wi-Fi 6E, Bluetooth LE 5.4 |
| `nora-b20-b21-b22` | NORA-B20x/B21x/B22x | Nordic nRF54L15/L10/L05 | nRF Connect SDK (Zephyr) | ubx_evknorab2/nrf54l15/cpuapp | Bluetooth 6.0 + Channel Sounding, 802.15.4, NFC |
| `alma-b20-b21` | ALMA-B20x/B21x | Nordic nRF54LM20A/B | nRF Connect SDK (Zephyr) | nrf54lm20dk/nrf54lm20a/cpuapp | Bluetooth 6.0, 802.15.4, Axon NPU (B-variant) |

### Open CPU vs u-connectXpress - CRITICAL

u-blox splits each family by the **third digit** of the part number. This SDK
builds **Open CPU** parts only, where the customer application runs on the
module. The u-connectXpress parts ship with AT-command firmware pre-flashed
and are configured by a host MCU - they cannot be built from here.

| Open CPU (this SDK) | u-connectXpress (NOT this SDK) |
|---------------------|--------------------------------|
| NORA-W30x | NORA-W36x |
| NORA-W50x / W51x | NORA-W56x / W57x |
| NORA-B20x / B21x / B22x | NORA-B26x / B27x |
| IRIS-W10x, NORA-W40x, ALMA-B20x/B21x | - |

Naming rule (team decision, 2026-10): a target is named after **every Open CPU
sub-series** in its family, lowercase, joined with `-`:
`iris-w10`, `nora-w30`, `nora-w40`, `nora-w50-w51`, `nora-b20-b21-b22`,
`alma-b20-b21`.
- The same name is used for CLI keys, `targets/<name>/` and `modules/<name>/`
  folders and `~/ubx-matter/<name>`. Python and doc file names use `_`
  (`nora_w50_w51_build.py`, `docs/nora_w50_w51_README.md`).
- Never use the bare series name (`nora-w3`, `nora-w5`, `nora-b2`) as a
  canonical name: `NORA-W3 series` also covers W36 (u-connectXpress), so it
  would advertise parts this SDK cannot build.
- The old short keys (`iris-w1`, `nora-w3`, `nora-w4`, `nora-w5`, `nora-b2`,
  `alma-b2`) stay accepted as aliases in `scripts/ubx.py`. Do not show them in
  help or docs.
- `target_paths.LEGACY` maps each target to its old slug and folder;
  `adopt_legacy()` moves an old `targets/NORA-W3/` or `~/ubx-matter/NORA-W4/`
  into the new folder on first use. Keep it.
- Do not rename EVK product names (`EVK-IRIS-W1`), u-blox URLs
  (`.../product/nora-w5-series`) or Zephyr board ids (`ubx_evk_iris_w1`, `ubx_evknorab2`).
- Repo-root u-blox assets follow `<vendor-sdk>/<module>/` (lowercase, hyphens):
  `mcuxpresso/iris-w10/`, `ameba-rtos-d/nora-w30/`, `esp-idf/nora-w40/`. New
  targets use the target key as the module folder. Profiles reference them
  through their `assets` field only.
- `scripts/ubx.py` has a `UCONNECTXPRESS` map so that typing `nora-w36` gives
  a product-line explanation instead of a bare "unknown target".

NORA-W40 uses ESP32-C6 (ESP32-C6FH4/FH8). ESP32-S3 is the previous generation
(NORA-W1/W2) and must not be used for NORA-W40.

ALMA-B20-B21 is under development and has no `ubx_evkalmab2` board definition in
Zephyr or NCS yet, so it builds against Nordic's `nrf54lm20dk`. Do not claim a
u-blox board target exists.

ALMA-W1 is not implemented. Keep `nordic_ncs_build.py`'s `TARGETS` table
extensible for it, but do not fabricate specs - MCP returns no data for it.

## Directory Structure

```
GettingStartedSDK/                  Workspace root
├── .github/
│   └── copilot-instructions.md    This file
├── .venv/                          Virtual environment (Python packages)
├── ubx-sdk.cmd / ubx-sdk.sh        SDK launcher - the entry point users run
├── ubx-matter.cmd / ubx-matter.sh  Optional Matter launcher (separate on purpose)
├── ubx.code-workspace              VS Code workspace (multi-root)
├── README.md                       Overview + quick start
├── scripts/                        Build driver scripts
│   ├── ubx.py                      Shared launcher core (flag surface, WSL2 hop)
│   ├── ubx_sdk.py                  SDK entry point (ubx.main())
│   ├── ubx_matter.py              Matter entry point (ubx.main(matter=True))
│   ├── matter_build.py            Matter driver for the 4 vendor-SDK targets
│   ├── matter_vendor/             Per-vendor Matter setup/build scripts (nora_w40.sh, nora_w50_w51.sh)
│   ├── module_config.py           RF calibration / TX power / MAC, all targets
│   ├── target_paths.py            Shared per-target directory layout
│   ├── iris_w10_build.py          NXP RW612/RW610 builder
│   ├── nora_w50_w51_build.py           TI CC35XX builder
│   ├── nora_w30_build.py          Realtek RTL872x builder
│   ├── nora_w40_build.py          Espressif ESP32-C6 builder
│   ├── nordic_ncs_build.py        Shared nRF Connect SDK builder (NORA-B20-B21-B22, ALMA-B20-B21)
│   ├── flash_helper.py            Flashing helper
│   ├── serial_logger.py           Serial console logger
│   ├── setup_venv.py              Virtual environment initializer
│   └── migrate_venv.sh / .bat     Moves a stray repo-root .venv into here
├── modules/                        Module config profiles (RF, TX power, MAC)
│   ├── README.md                   Profile schema reference
│   └── {alma-b20-b21,iris-w10,nora-b20-b21-b22,nora-w30,nora-w40,nora-w50-w51}/profile.json
├── targets/                        Per-target base folders (generated content)
│   ├── alma-b20-b21/{sdk,config}/
│   ├── iris-w10/{sdk,config}/      sdk/mcuxpresso-sdk = west workspace, fetched on demand
│   ├── nora-b20-b21-b22/{sdk,config}/
│   ├── nora-w30/{sdk,config}/      sdk/ameba-rtos-d, fetched on demand
│   ├── nora-w40/{sdk,config}/      sdk/esp-idf, fetched on demand
│   └── nora-w50-w51/{sdk,config}/
├── tests/                         pytest suite (launchers, Matter driver, module config)
└── docs/                           All other documentation
    ├── iris_w10_README.md
    ├── nora_w50_w51_README.md
    ├── nora_w30_README.md
    ├── nora_w40_README.md
    ├── nora_b20_b21_b22_README.md
    ├── alma_b20_b21_README.md
    ├── BUILD_ALL_EXAMPLES.md      Comprehensive build guide
    ├── QUICK_BUILD_REFERENCE.md   Quick cheat sheet
    ├── REVIEWERS_GUIDE.md         Review instructions for team
    ├── VENV_SETUP.md              venv setup guide
    └── WORKSPACE_SETUP.md         VS Code workspace guide
```

The GettingStartedSDK root is kept deliberately minimal: the two launcher
pairs, `ubx.code-workspace`, `README.md` and the folders above. Do not add
loose `.md` or `.bat` files to the root - docs go in `docs/`, scripts go in
`scripts/`.

Naming rule: anything shared by both launchers is plain `ubx`
(`ubx.py`, `ubx.code-workspace`); anything layer-specific is suffixed
(`ubx-sdk.*`, `ubx-matter.*`).

Only `README.md`, `.gitattributes` and `.gitlab-ci.yml` (GitLab only reads CI
config from the root) belong at the repository root. The root
is shared with the u-blox asset folders (`zephyr/`, `nrf5-sdk/`, `mcuxpresso/`,
`esp-idf/`, `ameba-rtos-d/`), so SDK files must not be added there.
`GettingStartedSDK/ubx.code-workspace` is multi-root (`"."` plus `".."`), so it
opens both the SDK and the repository root from its own folder.

## Build System Architecture

### Shared Components

2. **Virtual Environment (.venv/)**
   - Shared by all variant scripts
   - Location: GettingStartedSDK/.venv/
   - Contains: west (MCUXpresso manager), build dependencies
   - Setup: `python scripts/setup_venv.py` from GettingStartedSDK/
   - The launcher picks it up automatically; a Windows venv is never used from
     WSL and vice versa because the shims probe for `Scripts/python.exe` vs
     `bin/python`

2. **Per-Target Base Folders (targets/)**
   - `scripts/target_paths.py` is the single source of truth for the layout
   - `targets/<target>/sdk/` holds on-demand SDK clones and west workspaces
   - `targets/<target>/config/build.<host>.json` holds the per-platform tool cache
   - Vendor SDKs are never committed. They are gitignored and fetched by each
     target's `clone` command, so a fresh clone stays small and a user only
     downloads the SDK for the module they actually own.
   - Each vendor SDK lives in `targets/<target>/sdk/<upstream repo>`
     (`target_paths.vendor_sdk()`). Older versions fetched into the SDK root
     (`esp-idf/`, `ameba-rtos-d/`, `mcuxpresso-sdk/`); the launcher moves such
     a folder in on first use and rewrites the cached paths
     (`target_paths.adopt_root_sdk()`, skipped on `--dry-run`). Never fetch into
     the SDK root again - those names are the u-blox asset folders at the
     repository root.
   - Build artifacts stay in their vendor-native locations (west, idf.py and
     Realtek make each expect to find their own output in-tree)

3. **Cross-Platform Support**
   - Windows (Git Bash/MSYS2, CMD, PowerShell)
   - WSL2 (Ubuntu)
   - Native Linux
   - macOS (basic support)

### Build Script Patterns

Each build script follows this structure:

```python
# 1. Platform Detection
def host_kind() -> str:
    """Detect: 'windows', 'wsl', or 'linux'"""

# 2. Tool Detection
def detect_python(), detect_git(), detect_west(), detect_cmake(), etc.

# 3. Configuration Cache
def config_file() -> Path      # delegates to target_paths.resolve_config()
def load_config() -> Dict
def save_config(cfg: Dict)

# 4. Commands
def cmd_doctor(args)       # Verify tools
def cmd_clone(args)        # Download SDK
def cmd_list(args)         # Show available examples
def cmd_build(args)        # Build example
def cmd_clean(args)        # Clean artifacts
```

## Common Build Workflows

### Always go through the launcher

`ubx-sdk.cmd` (Windows) and `ubx-sdk.sh` (Linux/WSL2/macOS) are the user-facing
entry points. They are thin shims: they pick the shared `.venv` if it exists,
then forward to `scripts/ubx_sdk.py`, which calls into `scripts/ubx.py` - the
shared core that owns the flag surface, the fixed action order and the
automatic WSL2 hop. Suggest launcher commands to users, not raw
`python scripts/...` invocations. Reach for the per-target driver directly only
when debugging that driver. Matter has its own shim pair,
`ubx-matter.cmd` / `ubx-matter.sh`.

Flags are combinable and always execute in this order:
`--doctor` -> `--clone` -> `--install` -> `--build-sdk` -> `--rf-config` ->
`--list` -> `--clean` -> `--build` -> `--flash` -> `--mac-set` -> `--mac` -> `--log`. Anything
after a bare `--` is passed verbatim to the underlying driver.

`--rf-config`, `--mac-set` and `--mac` are served by `scripts/module_config.py` for every
target, not by the per-target driver. See "Module configuration" below.

### 1. First Time Setup
```bash
cd GettingStartedSDK
python scripts/setup_venv.py   # optional; the launcher also works without it
```

### 2. Build IRIS-W10 Example
```bash
./ubx-sdk.sh iris-w10 --doctor
./ubx-sdk.sh iris-w10 --clone --full          # omit --full for RW612 only
./ubx-sdk.sh iris-w10 --build demo_apps/hello_world --flash --log
```

### 3. Build NORA-W50-W51 Example
```bash
./ubx-sdk.sh nora-w50-w51 --doctor
./ubx-sdk.sh nora-w50-w51 --clone --build-sdk --build ble_wifi_provisioning
```

### 4. Build NORA-W40 (ESP32-C6)
```bash
./ubx-sdk.sh nora-w40 --clone --install --build hello_world
```

### 5. Build NORA-W30 (Realtek - needs WSL2)
```bash
# Works from Windows too: the launcher hops into WSL2 by itself.
./ubx-sdk.sh nora-w30 --clone --build project_hp
```

### 6. Build NORA-B20-B21-B22 / ALMA-B20-B21 (Nordic, nRF Connect SDK)
```bash
./ubx-sdk.sh nora-b20-b21-b22 --clone --install --build hello_world --flash --log
./ubx-sdk.sh alma-b20-b21 --build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp
```

Both share `scripts/nordic_ncs_build.py`. The launcher passes the target key as
the driver's first argument via `Target.driver_args`, the same mechanism Matter
uses. Existing NCS workspaces are detected (`C:\ncs\*`, `~/ncs*`, `ZEPHYR_BASE`);
`--clone` creates `<system drive>/ncs/<rev>` (never the repo drive), and
`nordic_ncs_build.py <target> use [path]` lists or selects one.
Matter for these targets comes from `nrf/samples/matter/*`. `ubx-matter` routes
them to the same NCS driver rather than `matter_build.py`, so `--list` is
filtered to Matter apps, bare `--build` names are scoped to `matter/`, and
`--flash`/`--log` work. They never hop into WSL2 because NCS builds natively on
Windows.

### 7. Module configuration (RF calibration, TX power, MAC)

```bash
./ubx-sdk.sh nora-w30 --variant NORA-W301 --region ETSI --rf-config --build project_hp
./ubx-sdk.sh iris-w10 --variant IRIS-W101-00B --rf-config
./ubx-sdk.sh nora-w40 --mac
```

Vendor SDKs ship RF data for the vendor's reference board, so firmware built
without `--rf-config` is **not regulatory compliant** on a u-blox module. Never
describe a plain `--build` flow as production-ready.

`scripts/module_config.py` serves `--rf-config`, `--mac-set` and `--mac` for every
target. What it applies is data, not code: `modules/<target>/profile.json`
describes every target with the same five topics - `output_power`,
`calibration` and `patches` (ops: `copy`, `replace`, `copy-tree`,
`replace-line`, `patch`, applied by `--rf-config` in that order), `mac`
(read, plus `write.runtime` lines and an optional `write.permanent` host tool
for `--mac-set [--burn]`) and `examples` (u-blox examples, `--build ubx/<name>`;
`project` builds in place, `drop-in` only prints the steps). Assets are never
duplicated into `modules/` - they stay in the u-blox folders at the repository
root, referenced through the profile's `assets` field:

| Target | Assets | Status |
|--------|--------|--------|
| IRIS-W10 | `mcuxpresso/iris-w10/sw-config/` | ready |
| NORA-W30 | `ameba-rtos-d/nora-w30/` | ready |
| NORA-W40 | `esp-idf/nora-w40/` | ready |
| nora-w50-w51, nora-b20-b21-b22, ALMA-B20-B21 | none yet | `status: pending` |

Ops are idempotent, back the vendor file up to `<name>.ubx-orig`, and record a
SHA-256 in `targets/<target>/config/rf_config.json`, so `--doctor` can report
drift and `module_config.py <target> revert` undoes everything. Adding a part
number or a target is a profile edit only - do not add per-target branches to
`ubx.py` or to a driver. Schema reference: `modules/README.md`.

The NORA-W40 patch exists for ESP-IDF 5.1, 5.5 and 6.2, one `patch` op each, picked
by a per-op `sdk_version` guard; `requires.sdk_version` rejects any other IDF.
For a new IDF, add a re-cut patch rather than widening a range. The 5.5 and 6.2 cuts
print a warning: same PHY data layout, but power values were characterised on 5.1.
`module_config.py <target> apply --sdk <path>` targets a specific checkout (e.g. the
Matter ESP-IDF); one applied state per target, so it refuses a second tree.

On Windows there is no GNU `patch`, so `module_config.py` falls back to
`git apply`. Inside a git checkout that silently skips every path and exits 0
unless repository discovery is disabled (`GIT_CEILING_DIRECTORIES`), which
`_git_apply()` does. Do not remove that.

### 8. Matter (optional, separate launcher)

```bash
./ubx-matter.sh nora-w40 --doctor
./ubx-matter.sh nora-w40 --clone --install
./ubx-matter.sh nora-w40 --list
./ubx-matter.sh nora-w40 --build light
```

Matter is deliberately kept off the plain SDK flag surface: most users never
build it and the SDKs are multi-GB. `ubx-sdk --help` does not list Matter
flags, and `ubx-sdk <target> --matter` fails with a pointer to `ubx-matter`.
Both shims
share `scripts/ubx.py`; `scripts/ubx_matter.py` just calls
`ubx.main(matter=True)`, which selects a Matter-specific help text and
`scripts/matter_build.py` as the driver for the four vendor-SDK targets. The
Nordic targets route to `nordic_ncs_build.py` instead - see section 6.

Matter SDKs are vendor forks of `project-chip/connectedhomeip`, each pinned to
a tagged release rather than a moving branch:

| Target | Repository | Revision |
|--------|------------|----------|
| IRIS-W10 | `NXP/matter` | `v1.6.0.0.1` |
| NORA-W30 | `ameba-rtos-d` + `ameba-rtos-matter` | `main`, `release/v1.5` |
| NORA-W40 | `esp-idf` + `esp-matter` | `v5.5.5`, `release/v1.5` |
| NORA-W50-W51 | `TexasInstruments/matter` | `matter-v1.5-ti-1.1` |

They are fetched into `~/ubx-matter/<target>` inside WSL2 (or `UBX_MATTER_ROOT`),
because these toolchains must not be built from a `/mnt/<drive>` path. On
Windows every vendor-SDK Matter action hops into WSL2, including `--doctor` and
`--list`, since the SDK only exists there. NORA-W50-W51 hops into the `Ubuntu-22.04`
distro (`Target.matter_wsl_distro`; override `UBX_WSL_DISTRO`).

All four vendor-SDK Matter targets are Linux-only. TI's is Ubuntu 22.04 only,
targets CC3551E on LP-EM-CC35X1, and `matter-v1.5-ti-1.1` is the GA, Matter 1.5
platform-certified tag - prefer it over the newer `-ea` tags. Matter 1.5 needs
Python 3.11, so `--install` uses deadsnakes `python3.11` on 22.04. SysConfig
and the Wi-Fi Toolbox (Linux) must be installed by the user under `~/ti`.
NORA-B20-B21-B22 and ALMA-B20-B21 are the exception: NCS builds natively on Windows, so they
never hop.

The Matter layer is **vendor examples only** - no u-blox application code, no
`matter/` folder. `matter_build.py` globs `MatterTarget.examples` in the fetched
SDK for `--list` and builds through `scripts/matter_vendor/<target>.sh`
(`setup` / `build <dir>` / `clean <dir>`). That script exists for NORA-W40
(esp-matter) and NORA-W50-W51 (TI, which ships only `lighting-app`); IRIS-W10 and
NORA-W30 are listed only. Do not reintroduce custom Matter apps such as the
thermometer - those live in `u-connectMatter`.

## Environment Variables

| Variable | Module | Value | Example |
|----------|--------|-------|---------|
| ARMGCC_DIR | IRIS-W10 | Optional override of the auto-detected Arm GNU Toolchain root | `/opt/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi` |
| NORA_W50_W51_WORKSPACE | NORA-W50-W51 | Override workspace location | `~/nora-w50-w51` |
| ZEPHYR_SDK_INSTALL_DIR | nora-b20-b21-b22, ALMA-B20-B21 | Zephyr SDK location | `~/zephyr-sdk-0.17.0` |
| UBX_MATTER_ROOT | Matter (vendor SDKs) | Where Matter SDKs are cloned | `~/ubx-matter` |
| MSYSTEM | Git Bash | UCRT64 or MINGW64 | `UCRT64` (auto-detected) |

## Output Artifacts

| Module | Build Output | Location |
|--------|--------------|----------|
| IRIS-W10 | `<example>.elf`, `<example>.bin` | `<west workspace>/build/<config>/` |
| NORA-W50-W51 | *.out | `<examples>/<rtos>/<board>/<toolchain>/` |
| NORA-W40 | *.elf, *.bin | `<esp-idf>/examples/<example>/build/` |
| NORA-W30 | *.bin | in-source, under the example directory |
| NORA-B20-B21-B22 | zephyr.elf, zephyr.hex, zephyr.bin | `<ncs>/build/<sample>/zephyr/` |
| ALMA-B20-B21 | zephyr.elf, zephyr.hex, zephyr.bin | `<ncs>/build/<sample>/zephyr/` |

## Common Issues & Solutions

### Python/pip Issues
**Problem:** "pip: command not found" or "No module named pip"
**Solution:** Use `detect_python()` to find Python with pip
**Prevention:** setup_venv.py handles this automatically

### No Arm GNU Toolchain (IRIS-W10)
**Problem:** IRIS-W10 build fails, "No Arm GNU toolchain found"
**Solution:** Install the Arm GNU Toolchain. `iris_w10_build.armgcc_dir()` finds
it (Arm installer paths, `~/.mcuxpressotools`, PATH) and sets `ARMGCC_DIR` for
the build; users never export it. `ARMGCC_DIR` in the environment overrides
**Note:** Override path is the root, NOT the bin/ subdirectory

### SDK Clone Takes Forever
**Problem:** west clone is slow, timeout, or hangs
**Solution:** Use `--board-only` for just RW612, not full SDK
**Alternative:** Pre-cache SDK, use existing workspace

### WSL2 Required for NORA-W30
**Problem:** "Cannot build Realtek on Windows"
**Why:** Realtek SDK has Linux-only build system
**Solution:** Use WSL2 Ubuntu or native Linux machine

### Mixed Python Versions
**Problem:** MSYS2 has multiple Python installations
**Solution:** setup_venv.py + activate venv handles priority
**Note:** Venv Python always takes precedence

## Code Conventions

### Script Organization
- Tool detection functions early (detect_*)
- Configuration management (config_file, load_config, save_config)
- Command functions (cmd_doctor, cmd_clone, etc.)
- Main entry point at bottom

### Error Handling
- Return 0 for success, 1 for failure
- Print plain-text status indicators: `[OK]`, `[FAIL]`, `[WARNING]`
- Do not add decorative emoji to script output
- Show helpful error messages, not just tracebacks
- Log full output for large operations (SDK clone)

### Path Handling
- Use `Path()` from pathlib for all file operations
- Anchor paths to the script location, never to `Path.cwd()`; a script must
  behave identically no matter which directory it is invoked from
- Use `scripts/target_paths.py` for anything under `targets/`
- Short paths on Windows to avoid spaces (short_path() function)

### Configuration
- JSON format for configs
- Store via `target_paths.resolve_config(TARGET)`, which returns
  `targets/<target>/config/build.<host>.json`
- Legacy `.{script_name}.{platform}.json` files at the SDK root are migrated
  automatically on first run
- Auto-load/save to track user choices between runs

## When to Use Each Command

`<target>` is one of `iris-w10`, `nora-w30`, `nora-w40`, `nora-w50-w51`, `nora-b20-b21-b22`,
`alma-b20-b21`.

| Task | Command |
|------|---------|
| Verify tools installed | `./ubx-sdk.sh <target> --doctor` |
| Download SDK | `./ubx-sdk.sh <target> --clone` |
| Install the SDK's tool env | `./ubx-sdk.sh <target> --install` |
| Apply the u-blox RF config | `./ubx-sdk.sh <target> --variant <PART> --rf-config` |
| List examples | `./ubx-sdk.sh <target> --list` |
| Build example | `./ubx-sdk.sh <target> --build <example>` |
| Clean build | `./ubx-sdk.sh <target> --clean` |
| Remove the SDK | `./ubx-sdk.sh <target> --clean-all` |
| Flash + log | `./ubx-sdk.sh <target> --flash --log` |
| Read the module MAC | `./ubx-sdk.sh <target> --mac` |
| Full pipeline | `./ubx-sdk.sh <target> --clone --install --build <example>` |
| Matter equivalent | `./ubx-matter.sh <target> --doctor` etc. (separate launcher) |

## Integration with u-blox MCP

The u-blox MCP provides access to:
- **Product documentation** - Module specs, datasheets, guides
- **Application notes** - Common use cases and patterns
- **Reference designs** - Hardware integration examples
- **Troubleshooting guides** - Common issues and solutions

Use MCP when:
- Asking about module capabilities (search u-blox knowledge)
- Needing hardware specs or pin configurations
- Looking for application notes or examples
- Understanding limitations (Wi-Fi 6 vs 6E, Thread vs non-Thread, etc.)

Prefer the MCP over repository comments when the two disagree about hardware
facts; module docstrings have been wrong before.

## Testing and Verification

### Unit Tests
- `python -m pytest tests -q` from GettingStartedSDK/ (pytest comes with `setup_venv.py`)
- Hermetic: no SDK, toolchain, WSL2 or hardware. Unit tests monkeypatch
  `subprocess.call` with the `calls` fixture (`tests/conftest.py`); vendor SDKs are
  faked as directory trees under `UBX_MATTER_ROOT=tmp_path`
- `tests/test_cli.py` runs the real entry points in a subprocess with `--dry-run`,
  which prints `[DRY-RUN] <cmd>` for every driver call and WSL2 hop instead of
  running it. Route any new launcher subprocess call through `ubx.execute()` so
  dry-run keeps covering it
- Run on Windows and WSL2; shim and drive-letter tests skip on the other host
- Add a test with every new flag, target, alias or Matter vendor script
- CI: the root `.gitlab-ci.yml` runs this suite on every push that touches
  `GettingStartedSDK/` (python:3.10-slim and 3.12-slim, JUnit report). Keep the
  suite hermetic so it stays runnable there
- Each build script also has `cmd_doctor()` - verifies tools on a real host

### Integration Tests
- Build empty/hello_world example for each module
- Verify output files created
- Check firmware can be flashed to board

### Cross-Platform Testing
- Test on: Windows (Git Bash), WSL2, Linux (if available)
- NORA-W30 requires Linux/WSL2
- IRIS-W10 requires an Arm GNU Toolchain (auto-detected)

## Future Development

- Wire `--build` for IRIS-W10 and NORA-W30 Matter (`scripts/matter_vendor/`)
- u-blox RF assets for nora-w50-w51, nora-b20-b21-b22, ALMA-B20-B21 (profiles are `pending`)
- Hardware verification of `--flash`, `--log`, `--mac` on every EVK
- `ubx_evkalmab2` board once u-blox publishes it

## Current Build Status

`docs/BUILD_TEST_RESULTS.md` is the single record of what has been built, with
which SDK version, on which host. Update it after every real build; do not copy
its numbers into other files, they go stale.

Known host traps found while building:
- `--doctor` must not shell out to `which` - it does not exist in cmd.exe or
  PowerShell. Use `shutil.which`; `tests/test_cli.py` runs every doctor
- An existing `~/ncs` is reused, but may be too old for the board target
  (`ubx_evknorab2` is not in NCS v2.9.0). The NCS driver reports the workspace
  version and fails early with a `--clone` hint
- Every clone calls `target_paths.check_space()` with an estimate first; a full
  E: drive once broke builds with misleading compiler errors

## Documentation Files

| File | Purpose |
|------|---------|
| README.md | GettingStartedSDK overview, quick start for all modules |
| docs/matter_README.md | Matter SDKs, vendor examples, per-target setup |
| modules/README.md | Module config profile schema, op reference |
| docs/iris_w10_README.md | IRIS-W10 detailed guide |
| docs/nora_w50_w51_README.md | NORA-W50-W51 detailed guide |
| docs/nora_w30_README.md | NORA-W30 WSL2 setup |
| docs/nora_w40_README.md | NORA-W40 ESP-IDF setup |
| docs/nora_b20_b21_b22_README.md | NORA-B20-B21-B22 nRF Connect SDK setup |
| docs/alma_b20_b21_README.md | ALMA-B20-B21 nRF Connect SDK setup |
| docs/BUILD_ALL_EXAMPLES.md | Complete building guide |
| docs/QUICK_BUILD_REFERENCE.md | Command cheat sheet |
| docs/REVIEWERS_GUIDE.md | Team review procedures |
| docs/VENV_SETUP.md | Virtual environment guide |
| docs/WORKSPACE_SETUP.md | VS Code workspace guide |

## Helpful Copilot Tasks

Here are things you can ask Copilot for help with:

1. **Build Script Help**
   - "How do I build IRIS-W10 hello_world example?"
   - "IRIS-W10 says no Arm GNU toolchain found, how do I fix it?"
   - "Why is my SDK clone so slow?"

2. **Module Specification Help** (uses u-blox MCP)
   - "What are IRIS-W10 capabilities?"
   - "Does NORA-W50 support Thread protocol?"
   - "What are the pin configurations for NORA-W40?"

3. **Cross-Platform Issues**
   - "How do I activate the venv on Windows?"
   - "Why is this failing on WSL2 but works on Windows?"
   - "How do I install Arm GNU Toolchain?"

4. **Troubleshooting**
   - "Build is failing with [error message]"
   - "Example isn't flashing to board, what could be wrong?"
   - "SDK download seems stuck, should I restart?"

5. **Development Assistance**
   - "I need to add a new build script for [module]"
   - "How should I structure configuration management?"
   - "What error handling is best for this tool?"

---

**Location:** GettingStartedSDK/.github/copilot-instructions.md (workspace root)
**Last Updated:** 2026-10-07
**Branch:** cmag_getting_started_sdk (under review)
**Status:** see docs/BUILD_TEST_RESULTS.md
