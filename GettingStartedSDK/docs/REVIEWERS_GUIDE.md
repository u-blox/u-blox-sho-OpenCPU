# Getting Started SDK - Reviewer's Guide

**Branch:** `cmag_getting_started_sdk`
**Status:** Ready for Colleague Review
**Created:** 2026-09-28

## Quick Start for Reviewers

### 1. Clone/Pull the Review Branch

```bash
cd u-blox-sho-OpenCPU
git fetch origin cmag_getting_started_sdk
git checkout cmag_getting_started_sdk
```

### 2. Set Up Environment (One-time)

```bash
# Create shared Python virtual environment
python GettingStartedSDK/scripts/setup_venv.py

# Activate venv
# Windows CMD:   .venv\Scripts\activate.bat
# Git Bash:      source .venv/bin/activate
# WSL2/Linux:    source .venv/bin/activate
```

### 3. Verify Structure

```bash
# Check new consolidated layout
ls -la GettingStartedSDK/
# Should see: ubx-sdk.cmd, ubx-sdk.sh, ubx-matter.cmd, ubx-matter.sh,
#             scripts/, modules/, docs/, targets/, README.md
```

### 4. Test Infrastructure

#### Test NORA-W50-W51 (Fully Working)
```bash
cd GettingStartedSDK

# List available examples
./ubx-sdk.sh nora-w50-w51 --list

# Build a simple example
./ubx-sdk.sh nora-w50-w51 --build empty

# Build WiFi example
./ubx-sdk.sh nora-w50-w51 --build ble_wifi_provisioning
```

#### Test IRIS-W10 (NXP MCUXpresso)
```bash
# Check environment (reports the Arm toolchain it will use)
python GettingStartedSDK/scripts/iris_w10_build.py doctor

# Clone SDK (~2 GB - targeted download)
python GettingStartedSDK/scripts/iris_w10_build.py clone

# List examples
python GettingStartedSDK/scripts/iris_w10_build.py list

# Build hello_world
python GettingStartedSDK/scripts/iris_w10_build.py build demo_apps/hello_world
```

#### Test NORA-W30 (Realtek - WSL2 Recommended)
```bash
# On WSL2 Ubuntu:
cd /mnt/e/u-blox/u-blox-sho-OpenCPU
source .venv/bin/activate
python GettingStartedSDK/scripts/nora_w30_build.py doctor
python GettingStartedSDK/scripts/nora_w30_build.py clone
python GettingStartedSDK/scripts/nora_w30_build.py build wlan_sample
```

#### Test NORA-W40 (ESP-IDF)
```bash
# Check tools
python GettingStartedSDK/scripts/nora_w40_build.py doctor

# Clone ESP-IDF
python GettingStartedSDK/scripts/nora_w40_build.py clone

# Build example
python GettingStartedSDK/scripts/nora_w40_build.py build hello_world
```

### 5. Review Key Files

- **Structure**: `GettingStartedSDK/` folder layout
  - `scripts/` - 4 build drivers (iris_w10, nora_w50_w51, nora_w30, nora_w40)
  - `docs/` - Individual variant READMEs
  - `setup_venv.py` - Shared venv initialization
  - `BUILD_ALL_EXAMPLES.md` - Comprehensive guide
  - `QUICK_BUILD_REFERENCE.md` - Quick cheat sheet
  - `BUILD_TEST_RESULTS.md` - This review document

- **Each Build Script**:
  - Check `config_file()` function - now delegates to `target_paths.py`
  - Configs stored per-target: `targets/<target>/config/build.<host>.json`
  - Legacy root dotfiles (`.iris_w1_build.*.json`) auto-migrated on first run
  - Check `detect_python()` function - handles venv activation
  - Review error handling and tool detection logic

- **Documentation**:
  - `GettingStartedSDK/docs/iris_w10_README.md` - IRIS-W10 setup (10 steps)
  - `GettingStartedSDK/docs/nora_w50_w51_README.md` - NORA-W50-W51 setup
  - `GettingStartedSDK/docs/nora_w30_README.md` - NORA-W30 setup
  - `GettingStartedSDK/docs/nora_w40_README.md` - NORA-W40 setup
  - `GettingStartedSDK/docs/nora_b20_b21_b22_README.md` - NORA-B20-B21-B22 setup
  - `GettingStartedSDK/docs/alma_b20_b21_README.md` - ALMA-B20-B21 setup

## What's New (Since Consolidation)

### [OK] Consolidated Structure
**Before:**
```
repo/
├── IRIS-W10-GettingStartedSDK/
├── NORA-W50-W51-GettingStartedSDK/
├── NORA-W30-GettingStartedSDK/
├── NORA-W40-GettingStartedSDK/
└── BUILD_ALL_EXAMPLES.md
```

**After:**
```
repo/
└── GettingStartedSDK/
    ├── ubx-sdk.cmd / .sh (single launcher for every target)
    ├── ubx-matter.cmd / .sh (optional Matter layer)
    ├── scripts/ (ubx.py, ubx_sdk.py, ubx_matter.py, matter_build.py,
    │           per-target build drivers, target_paths.py, setup_venv.py,
    │           migrate_venv.*, matter_vendor/)
    ├── targets/ (per-target base folders: sdk/, config/)
    │   ├── iris-w10/
    │   ├── nora-w30/
    │   ├── nora-w40/
    │   └── nora-w50-w51/
    ├── docs/ (4 variant READMEs + build guides)
    ├── .github/ (consolidated instructions)
    └── README.md
```

### [OK] Shared Python Environment
- Single `.venv/` at `GettingStartedSDK/.venv/`
- `scripts/setup_venv.py` initializes venv for all variants
- Installs `west` for MCUXpresso SDK management
- Works on Windows, WSL2, and Linux

### [OK] Verified Working
- NORA-W50-W51: [OK] Tested - builds WiFi provisioning example
- IRIS-W10: [OK] Ready - needs SDK clone
- NORA-W30: [OK] Ready - WSL2 environment
- NORA-W40: [OK] Ready - needs ESP-IDF

## Review Checklist

- [ ] **Structure**: Is the consolidated `GettingStartedSDK/` folder well-organized?
- [ ] **Build Scripts**: Do all target scripts work correctly?
- [ ] **Documentation**: Are the READMEs clear and complete?
- [ ] **Venv Setup**: Does `setup_venv.py` work on your system?
- [ ] **Config Files**: Are `targets/<target>/config/build.<host>.json` files created?
- [ ] **Cross-Platform**: Can you test on multiple platforms (Windows, WSL2, Linux)?
- [ ] **Examples**: Did you successfully build at least one example per variant?
- [ ] **Output Files**: Are firmware binaries created in expected locations?

## Issues/Feedback

Please document any issues found:

1. **Issue Type**: (Bug / Enhancement / Documentation)
2. **Platform**: (Windows / WSL2 / Linux)
3. **Description**: (What happened?)
4. **Steps to Reproduce**: (How to recreate?)
5. **Suggested Fix**: (Optional)

## Approval Criteria

This branch is ready for **master merge** when:

- [ ] All platforms tested by reviewers
- [ ] No critical bugs found
- [ ] Documentation approved
- [ ] Team consensus reached
- [ ] CI/CD (if applicable) passes

## Merge Path

1. **Review** (this branch): cmag_getting_started_sdk
2. **Approve** by colleagues
3. **Merge** to master
4. **Push** to GitHub (auto-mirror)

---

**Questions?** Review the comprehensive guide at `BUILD_ALL_EXAMPLES.md`

**Ready to merge?** Create a merge request on GitLab and tag team members for approval.
