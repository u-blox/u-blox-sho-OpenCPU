# GitHub Copilot Build Infrastructure Guide

This file helps GitHub Copilot understand the u-blox Getting Started SDK build
infrastructure for IRIS-W1, NORA-W3, NORA-W4, NORA-W5, NORA-B2 and ALMA-B2.

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
| `iris-w1` | IRIS-W10x | NXP RW612/RW610 | MCUXpresso SDK (west/CMake) | rdrw612bga | Wi-Fi 6, Bluetooth LE 5.4, optional Thread |
| `nora-w3` | NORA-W30x | Realtek RTL8720DF | Realtek RTOS SDK | N/A | Wi-Fi, Bluetooth (needs WSL2/Linux) |
| `nora-w4` | NORA-W40x | Espressif ESP32-C6 | ESP-IDF | esp32c6 | Wi-Fi 6 (2.4 GHz), Bluetooth LE 5.3, Thread/Zigbee |
| `nora-w5` | NORA-W50x/W51x | TI CC3501E/CC3551E | SimpleLink Wi-Fi SDK | LP_EM_CC35X1 | Wi-Fi 6E, Bluetooth LE 5.4 |
| `nora-b2` | NORA-B20x/B21x/B22x | Nordic nRF54L15/L10/L05 | nRF Connect SDK (Zephyr) | ubx_evknorab2/nrf54l15/cpuapp | Bluetooth 6.0 + Channel Sounding, 802.15.4, NFC |
| `alma-b2` | ALMA-B20x/B21x | Nordic nRF54LM20A/B | nRF Connect SDK (Zephyr) | nrf54lm20dk/nrf54lm20a/cpuapp | Bluetooth 6.0, 802.15.4, Axon NPU (B-variant) |

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

Consequences for naming:
- Never shorten `nora-w3` to `nora-w3`. `NORA-W3 series` is the umbrella over
  both W30 (Open CPU) and W36 (u-connectXpress), so the short name would
  advertise parts this SDK cannot build.
- `iris-w1` and `nora-w4` are the official series names. Do not invent
  `iris-w1` or `nora-w4`.
- `nora-w5` and `nora-b2` are correct because `NORA-W5 series` and
  `NORA-B2 series` are themselves official series names.
- `scripts/ubx.py` has a `UCONNECTXPRESS` map so that typing `nora-w36` gives
  a product-line explanation instead of a bare "unknown target".

NORA-W4 uses ESP32-C6 (ESP32-C6FH4/FH8). ESP32-S3 is the previous generation
(NORA-W1/W2) and must not be used for NORA-W4.

ALMA-B2 is under development and has no `ubx_evkalmab2` board definition in
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
│   ├── module_config.py           RF calibration / TX power / MAC, all targets
│   ├── target_paths.py            Shared per-target directory layout
│   ├── iris_w1_build.py          NXP RW612/RW610 builder
│   ├── nora_w5_build.py           TI CC35XX builder
│   ├── nora_w3_build.py          Realtek RTL872x builder
│   ├── nora_w4_build.py          Espressif ESP32-C6 builder
│   ├── nordic_ncs_build.py        Shared nRF Connect SDK builder (NORA-B2, ALMA-B2)
│   ├── flash_helper.py            Flashing helper
│   ├── serial_logger.py           Serial console logger
│   ├── setup_venv.py              Virtual environment initializer
│   └── migrate_venv.sh / .bat     Moves a stray repo-root .venv into here
├── matter/                         Matter app sources, per target (optional)
│   ├── README.md
│   └── {IRIS-W1,NORA-W3,NORA-W4,NORA-W5}/
├── modules/                        Module config profiles (RF, TX power, MAC)
│   ├── README.md                   Profile schema reference
│   └── {ALMA-B2,IRIS-W1,NORA-B2,NORA-W3,NORA-W4,NORA-W5}/profile.json
├── targets/                        Per-target base folders (generated content)
│   ├── ALMA-B2/{sdk,config}/
│   ├── IRIS-W1/{sdk,config}/
│   ├── NORA-B2/{sdk,config}/
│   ├── NORA-W3/{sdk,config}/
│   ├── NORA-W4/{sdk,config}/
│   └── NORA-W5/{sdk,config}/
├── ameba-rtos-d/                  Vendor SDK, fetched on demand (NORA-W3)
├── esp-idf/                       Vendor SDK, fetched on demand (NORA-W4)
├── mcuxpresso-sdk/                Vendor SDK, fetched on demand (IRIS-W1)
└── docs/                           All other documentation
    ├── iris_w1_README.md
    ├── nora_w5_README.md
    ├── nora_w3_README.md
    ├── nora_w4_README.md
    ├── nora_b2_README.md
    ├── alma_b2_README.md
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

Only `README.md` and `.gitattributes` belong at the repository root. The root
is shared with unrelated projects (`nRF5_SDK/`, `zephyr/`, `MCUXpresso/`,
`*-OutputPower/`), so SDK files must not be added there.
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
   - `targets/<TARGET>/sdk/` holds on-demand SDK clones and west workspaces
   - `targets/<TARGET>/config/build.<host>.json` holds the per-platform tool cache
   - Vendor SDKs are never committed. They are gitignored and fetched by each
     target's `clone` command, so a fresh clone stays small and a user only
     downloads the SDK for the module they actually own. Scripts must therefore
     detect an SDK at either the repo root or `targets/<TARGET>/sdk/`.
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
`--list` -> `--clean` -> `--build` -> `--flash` -> `--mac` -> `--log`. Anything
after a bare `--` is passed verbatim to the underlying driver.

`--rf-config` and `--mac` are served by `scripts/module_config.py` for every
target, not by the per-target driver. See "Module configuration" below.

### 1. First Time Setup
```bash
cd GettingStartedSDK
python scripts/setup_venv.py   # optional; the launcher also works without it
```

### 2. Build IRIS-W1 Example
```bash
export ARMGCC_DIR="/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
./ubx-sdk.sh iris-w1 --doctor
./ubx-sdk.sh iris-w1 --clone --full          # omit --full for RW612 only
./ubx-sdk.sh iris-w1 --build demo_apps/hello_world --flash --log
```

### 3. Build NORA-W5 Example
```bash
./ubx-sdk.sh nora-w5 --doctor
./ubx-sdk.sh nora-w5 --clone --build-sdk --build ble_wifi_provisioning
```

### 4. Build NORA-W4 (ESP32-C6)
```bash
./ubx-sdk.sh nora-w4 --clone --install --build hello_world
```

### 5. Build NORA-W3 (Realtek - needs WSL2)
```bash
# Works from Windows too: the launcher hops into WSL2 by itself.
./ubx-sdk.sh nora-w3 --clone --build project_hp
```

### 6. Build NORA-B2 / ALMA-B2 (Nordic, nRF Connect SDK)
```bash
./ubx-sdk.sh nora-b2 --clone --install --build hello_world --flash --log
./ubx-sdk.sh alma-b2 --build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp
```

Both share `scripts/nordic_ncs_build.py`. The launcher passes the target key as
the driver's first argument via `Target.driver_args`, the same mechanism Matter
uses. An existing `~/ncs` workspace is detected and reused instead of cloning.
Matter for these targets comes from `nrf/samples/matter/*`. `ubx-matter` routes
them to the same NCS driver rather than `matter_build.py`, so `--list` is
filtered to Matter apps, bare `--build` names are scoped to `matter/`, and
`--flash`/`--log` work. They never hop into WSL2 because NCS builds natively on
Windows.

### 7. Module configuration (RF calibration, TX power, MAC)

```bash
./ubx-sdk.sh nora-w3 --variant NORA-W301 --region ETSI --rf-config --build project_hp
./ubx-sdk.sh iris-w1 --variant IRIS-W101-00B --rf-config
./ubx-sdk.sh nora-w4 --mac
```

Vendor SDKs ship RF data for the vendor's reference board, so firmware built
without `--rf-config` is **not regulatory compliant** on a u-blox module. Never
describe a plain `--build` flow as production-ready.

`scripts/module_config.py` serves `--rf-config` and `--mac` for every target.
What it applies is data, not code: `modules/<TARGET>/profile.json` lists ops
(`copy`, `replace`, `copy-tree`, `replace-line`, `patch`) against the fetched
vendor SDK. Assets are never duplicated into `modules/` - they stay in the
u-blox folders at the repository root and are referenced by path:

| Target | Assets | Status |
|--------|--------|--------|
| IRIS-W1 | `MCUXpresso/IRIS-W1/sw_config/` | ready |
| NORA-W3 | `NORA-W30-OutputPower/` | ready |
| NORA-W4 | `NORA-W40-OutputPower/` | ready |
| NORA-W5, NORA-B2, ALMA-B2 | none yet | `status: pending` |

Ops are idempotent, back the vendor file up to `<name>.ubx-orig`, and record a
SHA-256 in `targets/<TARGET>/config/rf_config.json`, so `--doctor` can report
drift and `module_config.py <target> revert` undoes everything. Adding a part
number or a target is a profile edit only - do not add per-target branches to
`ubx.py` or to a driver. Schema reference: `modules/README.md`.

The NORA-W4 patch is cut against ESP-IDF 5.1 and the `requires.sdk_version`
guard rejects a newer IDF. That is deliberate; refresh the patch rather than
widening the range.

### 8. Matter (optional, separate launcher)

```bash
./ubx-matter.sh nora-w4 --doctor
./ubx-matter.sh nora-w4 --clone
./ubx-matter.sh nora-w4 --build thermometer
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
| IRIS-W1 | `NXP/matter` | `v1.6.0.0.1` |
| NORA-W3 | `ameba-rtos-d` + `ameba-rtos-matter` | `master`, `release/v1.5` |
| NORA-W4 | `esp-idf` + `esp-matter` | `v5.4.1`, `release/v1.5` |
| NORA-W5 | `TexasInstruments/matter` | `matter-v1.5-ti-1.1` |

They are fetched into `targets/<TARGET>/sdk/matter/`, or under
`UBX_MATTER_ROOT` when that is set - required under WSL2, because these
toolchains must not be built from a `/mnt/<drive>` path. App sources live in
`matter/<TARGET>/<app>/` with a `build.sh` accepting `setup`/`build`/`clean`.

All four vendor-SDK Matter targets are Linux-only. TI's is Ubuntu 22.04 only,
targets CC3551E on LP-EM-CC35X1, and `matter-v1.5-ti-1.1` is the GA, Matter 1.5
platform-certified tag - prefer it over the newer `-ea` tags. NORA-B2 and
ALMA-B2 are the exception: NCS builds natively on Windows, so they never hop.

The `matter/<TARGET>/` folders currently contain no applications, so for those
four targets `--doctor` and `--clone` work but `--list` and `--build` have
nothing to act on until an app is ported. Do not describe that flow as if apps
already exist. NORA-B2 and ALMA-B2 are the only targets where Matter builds end
to end today, via the NCS samples.

Reference implementations to port from live in the `u-connectMatter` repo under
`companion/` - do not use u-connectClient or u-connectXpress as a starting
point.

## Environment Variables

| Variable | Module | Value | Example |
|----------|--------|-------|---------|
| ARMGCC_DIR | IRIS-W1 | Path to Arm GNU Toolchain root | `/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi` |
| NORA_W5_WORKSPACE | NORA-W5 | Override workspace location | `~/nora-w5` |
| ZEPHYR_SDK_INSTALL_DIR | NORA-B2, ALMA-B2 | Zephyr SDK location | `~/zephyr-sdk-0.17.0` |
| UBX_MATTER_ROOT | Matter (vendor SDKs) | Where Matter SDKs are cloned | `~/ubx-matter` |
| MSYSTEM | Git Bash | UCRT64 or MINGW64 | `UCRT64` (auto-detected) |

## Output Artifacts

| Module | Build Output | Location |
|--------|--------------|----------|
| IRIS-W1 | `<example>.elf`, `<example>.bin` | `<west workspace>/build/<config>/` |
| NORA-W5 | *.out | `<examples>/<rtos>/<board>/<toolchain>/` |
| NORA-W4 | *.elf, *.bin | `<esp-idf>/examples/<example>/build/` |
| NORA-W3 | *.bin | in-source, under the example directory |
| NORA-B2 | zephyr.elf, zephyr.hex, zephyr.bin | `<ncs>/build/<sample>/zephyr/` |
| ALMA-B2 | zephyr.elf, zephyr.hex, zephyr.bin | `<ncs>/build/<sample>/zephyr/` |

## Common Issues & Solutions

### Python/pip Issues
**Problem:** "pip: command not found" or "No module named pip"
**Solution:** Use `detect_python()` to find Python with pip
**Prevention:** setup_venv.py handles this automatically

### ARMGCC_DIR Not Set
**Problem:** IRIS-W1 build fails, "ARMGCC_DIR not configured"
**Solution:** `export ARMGCC_DIR="path/to/arm/toolchain"`
**Note:** Path should be root, NOT bin/ subdirectory

### SDK Clone Takes Forever
**Problem:** west clone is slow, timeout, or hangs
**Solution:** Use `--board-only` for just RW612, not full SDK
**Alternative:** Pre-cache SDK, use existing workspace

### WSL2 Required for NORA-W3
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
  `targets/<TARGET>/config/build.<host>.json`
- Legacy `.{script_name}.{platform}.json` files at the SDK root are migrated
  automatically on first run
- Auto-load/save to track user choices between runs

## When to Use Each Command

`<target>` is one of `iris-w1`, `nora-w3`, `nora-w4`, `nora-w5`, `nora-b2`,
`alma-b2`.

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
- Each build script has `cmd_doctor()` - verifies tools
- Check docs/README for module-specific requirements
- docs/REVIEWERS_GUIDE.md has full test procedures

### Integration Tests
- Build empty/hello_world example for each module
- Verify output files created
- Check firmware can be flashed to board

### Cross-Platform Testing
- Test on: Windows (Git Bash), WSL2, Linux (if available)
- NORA-W3 requires Linux/WSL2
- IRIS-W1 requires ARMGCC_DIR set

## Future Development

### Short Term
- Complete IRIS-W1 build testing (SDK download large)
- Test NORA-W4 with ESP-IDF clone
- Test NORA-W3 on WSL2

### Medium Term
- Add debugger support (J-Link, MCU-Link, Realtek tools)
- Create separate debug workspace when mature
- Expand examples for each module

### Long Term
- CI/CD integration for automated testing
- Release management and versioning
- Advanced multi-module build orchestration

## Current Build Status (2026-09-28)

### [OK] Verified Working
- **IRIS-W1:** hello_world.elf (258 KB) and hello_world.bin (29 KB) built successfully
- **NORA-W5:** ble_wifi_provisioning.out built successfully

### Ready for Build
- **NORA-W4:** Requires ESP-IDF installation (`./ubx-sdk.sh nora-w4 --install`)
- **NORA-W3:** Requires WSL2 Realtek SDK clone (`./ubx-sdk.sh nora-w3 --clone`, hops into WSL2 automatically)

### Hardware Verification (Next Phase)
When hardware is connected, test:
1. **IRIS-W1 Serial Logging:** `./ubx-sdk.sh iris-w1 --log`
2. **IRIS-W1 J-Link Flash:** `./ubx-sdk.sh iris-w1 --flash demo_apps/hello_world`
3. **NORA-W5 Hardware Test:** (TI reference board validation)
4. **NORA-W3 Hardware Test:** (Realtek RTL872x validation on WSL2)
5. **NORA-W4 Hardware Test:** (Espressif ESP32-C6 validation)

See docs/BUILD_TEST_RESULTS.md for detailed status and docs/BUILD_ALL_EXAMPLES.md for complete build workflows.

## Documentation Files

| File | Purpose |
|------|---------|
| README.md | GettingStartedSDK overview, quick start for all modules |
| matter/README.md | Matter apps, SDK map, how to add an app |
| modules/README.md | Module config profile schema, op reference |
| docs/iris_w1_README.md | IRIS-W1 detailed guide |
| docs/nora_w5_README.md | NORA-W5 detailed guide |
| docs/nora_w3_README.md | NORA-W3 WSL2 setup |
| docs/nora_w4_README.md | NORA-W4 ESP-IDF setup |
| docs/nora_b2_README.md | NORA-B2 nRF Connect SDK setup |
| docs/alma_b2_README.md | ALMA-B2 nRF Connect SDK setup |
| docs/BUILD_ALL_EXAMPLES.md | Complete building guide |
| docs/QUICK_BUILD_REFERENCE.md | Command cheat sheet |
| docs/REVIEWERS_GUIDE.md | Team review procedures |
| docs/VENV_SETUP.md | Virtual environment guide |
| docs/WORKSPACE_SETUP.md | VS Code workspace guide |

## Helpful Copilot Tasks

Here are things you can ask Copilot for help with:

1. **Build Script Help**
   - "How do I build IRIS-W1 hello_world example?"
   - "What's the ARMGCC_DIR error and how do I fix it?"
   - "Why is my SDK clone so slow?"

2. **Module Specification Help** (uses u-blox MCP)
   - "What are IRIS-W1 capabilities?"
   - "Does NORA-W50 support Thread protocol?"
   - "What are the pin configurations for NORA-W4?"

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
**Last Updated:** 2026-09-28
**Branch:** cmag_getting_started_sdk (under review)
**Status:** [OK] IRIS-W1 & NORA-W5 builds verified — W30/W40 ready for build — Hardware testing pending
