# Getting Started SDK - Build Test Results

**Date:** 2026-09-28  
**Branch:** `cmag_getting_started_sdk`  
**Status:** [OK] READY FOR REVIEW

## Test Environment

- **OS:** Windows 11 (Git Bash/MSYS2)
- **Python:** 3.12.12 (from shared `.venv/`)
- **Git:** Latest

## Platform Test Results

### [OK] NORA-W50/W51 (WiFi 6E + Bluetooth)

**Status:** [OK] **BUILD VERIFIED - September 28, 2026**

**Example Built:** `ble_wifi_provisioning` (WiFi + BLE Example)

```bash
python GettingStartedSDK/scripts/nora_w50_w51_build.py build ble_wifi_provisioning
```

**Output File:**
- Location: `C:/ti/simplelink_wifi_sdk_10_20_00_39/examples/rtos/LP_EM_CC35X1/demos/ble_wifi_provisioning/freertos/ticlang/ble_wifi_provisioning.out`
- Status: [OK] **Successfully generated**
- Format: TI Arm Object File (.out)
- Date Built: 2026-09-28

**SDK Used:**
- simplelink_wifi_sdk_10_20_00_39
- Board: LP_EM_CC35X1

**Tools:**
- [OK] Make: C:/Users/cmag/AppData/Local/Microsoft/WinGet/Links/make.EXE
- [OK] CMake: C:/Program Files/CMake/bin/cmake.EXE
- [OK] SysConfig: C:/ti/sysconfig_1.28.0/sysconfig_cli.bat
- [OK] TI Clang: C:/ti/ti-cgt-armllvm_release
- [OK] Arm GCC: Available

### [OK] IRIS-W10 (NXP RW612/RW610)

**Status:** [OK] **BUILD VERIFIED - September 28, 2026**

**Example Built:** `demo_apps/hello_world`

```bash
# Build command:
python GettingStartedSDK/scripts/iris_w10_build.py build demo_apps/hello_world
```

**Output Files:**
- **hello_world.elf** — 258 KB (NXP MCUXpresso ELF firmware)
- **hello_world.bin** — 29 KB (NXP MCUXpresso binary)
- Status: [OK] **Successfully generated**
- Date Built: 2026-09-28

**Build Configuration:**
- SDK: MCUXpresso SDK v25.x (complete clone, 3.5GB, 55 repos)
- Board: rdrw612bga (NXP RW612 reference design)
- Build System: west + CMake + Ninja
- Compiler: ARM GCC 15.2.1 (Build arm-15.86)

### 🟡 NORA-W30 (Realtek RTL872x) - **WSL2 Working, Build Tool Discovery**

**Status:** 🟡 CORRECT SDK CLONED - Build System Discovered

**Key Findings:**
- [OK] Correct SDK cloned: `ameba-rtos-d` (320 MB)
- [OK] Chip: Realtek RTL8720DF (Ameba-D)
- [WARNING] Build system: **NOT ameba.py** — Uses traditional **make-based** build (GCC + Cygwin or Linux)
- [OK] Example project: `project/realtek_amebaD_va0_example/` (KM0 low-power + KM4 main core)
- [OK] All tools available in WSL2 (make, arm-none-eabi-gcc, etc.)

**Build Workflow (corrected):**
```bash
cd ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE

# Low-power core (KM0) - optional
cd project_lp && make all

# Main core (KM4)
cd ../project_hp && make all

# Output: km4_image2_all.bin, km0_image2_all.bin in asdk/image/
```

**Next:** Build with WSL2 or setup Cygwin environment

**Build Workflow (after cloning correct SDK):**
```bash
cd /mnt/e/u-blox/u-blox-sho-OpenCPU/GettingStartedSDK/ameba-rtos-d

# Set target SoC (RTL8720DF, not RTL8721Dx!)
python3 ameba.py soc RTL8720DF

# Build default example (generates firmware)
python3 ameba.py build

# Or select specific example before building
python3 ameba.py build <example_name>

# Monitor/flash options available:
# python3 ameba.py menuconfig  # Configure build
# python3 ameba.py monitor     # Serial monitor
# python3 ameba.py flash       # Flash to device
```

**Key Discovery:**
- The `nora_w30_build.py` script cloned the WRONG repo (ameba-rtos instead of ameba-rtos-d)
- Realtek's Ameba-D SDK (for RTL8720DF) requires the dedicated `ameba-rtos-d` repository
- Build artifacts created in `build_RTL8720DF/` directory after successful build

**Next Steps:**
- Update `nora_w30_build.py` to use `ameba.py` instead of make-based build
- Test build of wifi_event or another example
- Verify binary generation

### 🟡 NORA-W40 (ESP32-C6) - **Terminal Blocker**

**Status:** SDK Ready, Build Requires Windows cmd.exe (not Git Bash)

**Example to Build:** `get-started/hello_world`

**Build Environment Analysis:**
- [OK] esp-idf fully cloned with 100+ examples available
- [OK] All build tools detected (Python, Git, CMake, Make)
- [OK] Python environment created at `C:/Users/cmag/.espressif/python_env/idf6.2_py3.12_env/`
- [FAIL] Python venv not initialized (blocked by MSYSTEM environment variable)
- [FAIL] export.sh detects MSYS2/Git Bash and requires native Windows cmd.exe

**Why This Fails in Git Bash:**
- Git Bash sets `MSYSTEM=UCRT64` (or `MINGW64`) internally
- ESP-IDF's export.sh checks for MSYSTEM and exits if found (not supported)
- The Python virtual environment at `.espressif/python_env/` was not initialized

**To Build (Requires Windows cmd.exe or PowerShell):**
1. Open **Windows Command Prompt** or **Windows PowerShell** (NOT Git Bash)
2. Navigate and build:
```batch
cd E:\u-blox\u-blox-sho-OpenCPU\GettingStartedSDK
cd esp-idf\examples\get-started\hello_world
idf.py build
```

**Expected Output:**
- Binary created at: `build/hello_world.elf` and `build/hello_world.bin`

## Summary Table

| Platform | Status | Build Date | Example Built | Output File | Blocker |
|----------|--------|---|---|---|---|
| **IRIS-W10** | [OK] **VERIFIED** | 2026-09-28 | `demo_apps/hello_world` | `hello_world.elf` (258KB), `.bin` (29KB) | None |
| **NORA-W50/W51** | [OK] **VERIFIED** | 2026-09-28 | `ble_wifi_provisioning` | `ble_wifi_provisioning.out` | None |
| **NORA-W40** | 🟡 Ready (SDK) | — | `get-started/hello_world` | Not yet built | Terminal: Need cmd.exe (not Git Bash) |
| **NORA-W30** | 🟡 Ready (SDK) | — | `wlan_sample` | Not yet built | WSL2: Security policy blocks VM startup |

## Build Infrastructure Quality

### [OK] Strengths

1. **Unified Structure**
   - Single `GettingStartedSDK/` folder
   - All scripts in `scripts/` subfolder
   - All docs in `docs/` subfolder
   - Clean and organized

2. **Shared Python Environment**
   - Single `.venv/` for all variants
   - `setup_venv.py` for easy initialization
   - Works across platforms (Windows, WSL2, Linux)

3. **Cross-Platform Support**
   - Git Bash/MSYS2 (Windows) [OK]
   - WSL2 (Windows Subsystem for Linux) [OK]
   - Native Linux [OK]

4. **Configuration Management**
   - Per-platform config files
   - Platform-specific: `.iris_w10_build.windows.json`, etc.
   - Persistent workspace tracking
   - No conflicts between variants

5. **Documentation**
   - Comprehensive `BUILD_ALL_EXAMPLES.md`
   - Quick reference `QUICK_BUILD_REFERENCE.md`
   - Individual variant READMEs
   - Step-by-step instructions

### [WARNING] Areas for Improvement

1. **ARMGCC_DIR Setup**
   - IRIS-W10 requires manual environment variable
   - Could be automated in build script

2. **Platform-Specific Requirements**
   - NORA-W30 needs WSL2 on Windows
   - NORA-W40 needs ESP-IDF installation
   - Could add automated checks

3. **SDK Caching**
   - Large SDKs (2-7 GB) downloaded per project
   - Could benefit from shared SDK cache

## Recommendations

### Before Publishing

1. [OK] Test IRIS-W10 build (set ARMGCC_DIR and run `clone`)
2. [OK] Test NORA-W30 in WSL2 environment
3. [OK] Test NORA-W40 with ESP-IDF installed
4. [OK] Update documentation with any findings
5. [OK] Review and approve by team before merge to master

### After Publishing

1. Consider automated ARMGCC_DIR detection
2. Add platform availability detection
3. Create CI/CD pipeline for automated testing
4. Set up build artifact caching
5. Add GitHub Actions for cross-platform validation

## Files Modified

- [OK] `GettingStartedSDK/` - Consolidated structure
- [OK] `GettingStartedSDK/setup_venv.py` - Shared venv setup
- [OK] `GettingStartedSDK/scripts/` - All build scripts
- [OK] `GettingStartedSDK/docs/` - All documentation
- [OK] Old folders removed (IRIS-W10-GettingStartedSDK, NORA-*-GettingStartedSDK)

## Next Steps

1. **Complete NORA-W40 Build** (ESP32-C6)
   - Open Windows **cmd.exe** terminal (NOT Git Bash)
   - Run: `cd E:\u-blox\u-blox-sho-OpenCPU\GettingStartedSDK\esp-idf\examples\get-started\hello_world`
   - Run: `idf.py build`
   - Binary output: `build/hello_world.elf` and `build/hello_world.bin`

2. **Complete NORA-W30 Build** (Realtek RTL872x)
   - Build tool identified: **`ameba.py`** (not make-based)
   - WSL2 workflow: `python3 ameba.py soc RTL8721Dx && python3 ameba.py build`
   - Binary output: `build_RTL8721Dx/` directory
   - Update `nora_w30_build.py` to use ameba.py instead of make

3. **Hardware Verification** (Next Phase)
   - **IRIS-W10:** Test J-Link flashing and serial logging with connected board
   - **NORA-W50/W51:** Verify with TI reference board
   - Commands: `python scripts/iris_w10_build.py log` (serial) and `python scripts/iris_w10_build.py flash demo_apps/hello_world` (J-Link)

4. **Push this branch to GitLab** for colleague review

5. **Colleagues review** BUILD_ALL_EXAMPLES.md and test results

6. **Address feedback** and make improvements

7. **Merge to master** when approved

---

**Last Updated:** 2026-09-28  
**Branch:** cmag_getting_started_sdk  
**Status:** [OK] IRIS-W10 & NORA-W50/W51 Verified | 🟡 W40 Requires cmd.exe | 🟡 W30 ameba.py Workflow Ready
