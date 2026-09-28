# GitHub Copilot Build Infrastructure Guide

This file helps GitHub Copilot understand the u-blox Getting Started SDK build infrastructure for IRIS-W10, NORA-W50/W51, NORA-W30, and NORA-W40.

## Communication Preferences

- **Emoji usage:** Minimal - focus on clear technical information without decorative elements
- **Response style:** Concise and direct
- **Documentation:** Straightforward without embellishment
- **Focus:** Technical accuracy and efficiency

## Project Context

**Repository:** u-blox-sho-OpenCPU (GitLab)  
**Primary Work:** Building firmware for 4 u-blox WiFi/Bluetooth modules  
**Build Infrastructure:** GettingStartedSDK/ folder with consolidated scripts  
**Current Branch:** cmag_getting_started_sdk (review branch) or master

### Module Specifications

| Module | SoC | Framework | Board Target | Features |
|--------|-----|-----------|--------------|----------|
| **IRIS-W10** | NXP RW612/RW610 | MCUXpresso SDK (west/CMake) | rdrw612bga | Wi-Fi 6, Bluetooth LE 5.4, optional Thread |
| **NORA-W50/W51** | TI CC35XX | SimpleLink WiFi SDK | LP_EM_CC35X1 | Wi-Fi 6E, Bluetooth LE 5.4 |
| **NORA-W30** | Realtek RTL872x | Realtek RTOS SDK | N/A | Wi-Fi, Bluetooth (needs WSL2/Linux) |
| **NORA-W40** | Espressif ESP32-C6 | ESP-IDF | esp32c6 | Wi-Fi 6 (2.4 GHz), Bluetooth LE 5.3, Thread/Zigbee |

NORA-W40 uses ESP32-C6 (ESP32-C6FH4/FH8). ESP32-S3 is the previous generation
(NORA-W1/W2) and must not be used for NORA-W40.

## Directory Structure

```
GettingStartedSDK/                  Workspace root
├── .github/
│   └── copilot-instructions.md    This file
├── .venv/                          Virtual environment (Python packages)
├── scripts/                        Build driver scripts
│   ├── target_paths.py            Shared per-target directory layout
│   ├── iris_w10_build.py          NXP RW612/RW610 builder
│   ├── nora_w50_w51_build.py      TI CC35XX builder
│   ├── nora_w30_build.py          Realtek RTL872x builder
│   ├── nora_w40_build.py          Espressif ESP32-C6 builder
│   ├── flash_helper.py            Flashing helper
│   └── serial_logger.py           Serial console logger
├── targets/                        Per-target base folders (generated content)
│   ├── IRIS-W10/{sdk,config}/
│   ├── NORA-W30/{sdk,config}/
│   ├── NORA-W40/{sdk,config}/
│   └── NORA-W50-W51/{sdk,config}/
├── ameba-rtos-d/                  Vendor SDK, fetched on demand (NORA-W30)
├── esp-idf/                       Vendor SDK, fetched on demand (NORA-W40)
├── mcuxpresso-sdk/                Vendor SDK, fetched on demand (IRIS-W10)
├── docs/                          Module-specific README files
│   ├── iris_w10_README.md
│   ├── nora_w50_w51_README.md
│   ├── nora_w30_README.md
│   └── nora_w40_README.md
├── setup_venv.py                  Virtual environment initializer
├── migrate_venv.sh / .bat         Moves a stray repo-root .venv into here
├── VENV_SETUP.md                  venv setup guide
├── WORKSPACE_SETUP.md             VS Code workspace guide
├── BUILD_ALL_EXAMPLES.md          Comprehensive build guide
├── QUICK_BUILD_REFERENCE.md       Quick cheat sheet
└── REVIEWERS_GUIDE.md             Review instructions for team
```

Only `README.md`, `.gitattributes` and the `.code-workspace` files belong at the
repository root. The root is shared with unrelated projects (`nRF5_SDK/`,
`zephyr/`, `MCUXpresso/`, `*-OutputPower/`), so SDK files must not be added
there. The `.code-workspace` files are multi-root (`"."` plus
`"GettingStartedSDK"`) and must stay at the root to keep both paths valid.

## Build System Architecture

### Shared Components

1. **Virtual Environment (.venv/)**
   - Shared by all 4 variant scripts
   - Location: GettingStartedSDK/.venv/
   - Contains: west (MCUXpresso manager), build dependencies
   - Setup: `python setup_venv.py` from GettingStartedSDK/

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

### IMPORTANT: Always Activate .venv Before Building

Before running any build commands, activate the virtual environment:

**Windows (Git Bash/MSYS2):**
```bash
source .venv/Scripts/activate
```

**Linux/WSL2/macOS:**
```bash
source .venv/bin/activate
```

The prompt will show `(.venv)` when activated. All build scripts must run with .venv active to use correct Python dependencies.

### 1. First Time Setup
```bash
cd GettingStartedSDK
python setup_venv.py
source .venv/bin/activate  # or appropriate activation for your platform
```

### 2. Build IRIS-W10 Example
```bash
export ARMGCC_DIR="/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
python scripts/iris_w10_build.py doctor
python scripts/iris_w10_build.py clone --full  # or --board-only
python scripts/iris_w10_build.py build demo_apps/hello_world
```

### 3. Build NORA-W50/W51 Example
```bash
python scripts/nora_w50_w51_build.py doctor
python scripts/nora_w50_w51_build.py build ble_wifi_provisioning
```

### 4. Build NORA-W40 (ESP32-C6)
```bash
python scripts/nora_w40_build.py clone
python scripts/nora_w40_build.py build hello_world
```

### 5. Build NORA-W30 (Realtek - needs WSL2)
```bash
# From WSL2/Linux terminal
cd /mnt/e/u-blox/u-blox-sho-OpenCPU/GettingStartedSDK
source .venv/bin/activate
python scripts/nora_w30_build.py clone
python scripts/nora_w30_build.py build wlan_sample
```

## Environment Variables

| Variable | Module | Value | Example |
|----------|--------|-------|---------|
| ARMGCC_DIR | IRIS-W10 | Path to Arm GNU Toolchain root | `/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi` |
| NORA_W50_W51_WORKSPACE | NORA-W50/W51 | Override workspace location | `~/nora-w50-w51` |
| MSYSTEM | Git Bash | UCRT64 or MINGW64 | `UCRT64` (auto-detected) |

## Output Artifacts

| Module | Build Output | Location |
|--------|--------------|----------|
| IRIS-W10 | zephyr.elf, zephyr.bin | `<west workspace>/build/` |
| NORA-W50/W51 | *.out | `<examples>/<rtos>/<board>/<toolchain>/` |
| NORA-W40 | *.elf, *.bin | `<esp-idf>/examples/<example>/build/` |
| NORA-W30 | *.bin | in-source, under the example directory |

## Common Issues & Solutions

### Python/pip Issues
**Problem:** "pip: command not found" or "No module named pip"  
**Solution:** Use `detect_python()` to find Python with pip  
**Prevention:** setup_venv.py handles this automatically

### ARMGCC_DIR Not Set
**Problem:** IRIS-W10 build fails, "ARMGCC_DIR not configured"  
**Solution:** `export ARMGCC_DIR="path/to/arm/toolchain"`  
**Note:** Path should be root, NOT bin/ subdirectory

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
  `targets/<TARGET>/config/build.<host>.json`
- Legacy `.{script_name}.{platform}.json` files at the SDK root are migrated
  automatically on first run
- Auto-load/save to track user choices between runs

## When to Use Each Script

| Task | Script | Command |
|------|--------|---------|
| Verify tools installed | any | `python scripts/{script} doctor` |
| Download SDK | {module}_build.py | `python scripts/{script} clone` |
| List examples | {module}_build.py | `python scripts/{script} list` |
| Build example | {module}_build.py | `python scripts/{script} build {example}` |
| Clean build | {module}_build.py | `python scripts/{script} clean` |
| Full pipeline | {module}_build.py | `python scripts/{script} all` |

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
- REVIEWERS_GUIDE.md has full test procedures

### Integration Tests
- Build empty/hello_world example for each module
- Verify output files created
- Check firmware can be flashed to board

### Cross-Platform Testing
- Test on: Windows (Git Bash), WSL2, Linux (if available)
- NORA-W30 requires Linux/WSL2
- IRIS-W10 requires ARMGCC_DIR set

## Future Development

### Short Term
- Complete IRIS-W10 build testing (SDK download large)
- Test NORA-W40 with ESP-IDF clone
- Test NORA-W30 on WSL2

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
- **IRIS-W10:** hello_world.elf (258 KB) and hello_world.bin (29 KB) built successfully
- **NORA-W50/W51:** ble_wifi_provisioning.out built successfully

### Ready for Build
- **NORA-W40:** Requires ESP-IDF installation (`python scripts/nora_w40_build.py install`)
- **NORA-W30:** Requires WSL2 Realtek SDK clone (`wsl -d Ubuntu-24.04 bash -c "... python scripts/nora_w30_build.py clone"`)

### Hardware Verification (Next Phase)
When hardware is connected, test:
1. **IRIS-W10 Serial Logging:** `python scripts/iris_w10_build.py log`
2. **IRIS-W10 J-Link Flash:** `python scripts/iris_w10_build.py flash demo_apps/hello_world`
3. **NORA-W50/W51 Hardware Test:** (TI reference board validation)
4. **NORA-W30 Hardware Test:** (Realtek RTL872x validation on WSL2)
5. **NORA-W40 Hardware Test:** (Espressif ESP32-C6 validation)

See BUILD_TEST_RESULTS.md for detailed status and BUILD_ALL_EXAMPLES.md for complete build workflows.

## Documentation Files

| File | Purpose |
|------|---------|
| README.md (main) | Overview, quick start for all modules |
| docs/iris_w10_README.md | IRIS-W10 detailed guide |
| docs/nora_w50_w51_README.md | NORA-W50/W51 detailed guide |
| docs/nora_w30_README.md | NORA-W30 WSL2 setup |
| docs/nora_w40_README.md | NORA-W40 ESP-IDF setup |
| BUILD_ALL_EXAMPLES.md | Complete building guide for all 4 |
| QUICK_BUILD_REFERENCE.md | Command cheat sheet |
| REVIEWERS_GUIDE.md | Team review procedures |
| VENV_SETUP.md | Virtual environment guide |

## Helpful Copilot Tasks

Here are things you can ask Copilot for help with:

1. **Build Script Help**
   - "How do I build IRIS-W10 hello_world example?"
   - "What's the ARMGCC_DIR error and how do I fix it?"
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
**Last Updated:** 2026-09-28  
**Branch:** cmag_getting_started_sdk (under review)  
**Status:** [OK] IRIS-W10 & NORA-W50/W51 builds verified — W30/W40 ready for build — Hardware testing pending
