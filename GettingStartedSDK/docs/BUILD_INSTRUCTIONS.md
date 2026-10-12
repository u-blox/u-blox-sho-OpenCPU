# NORA-W30 & NORA-W40 Build Instructions

**Date:** 2026-09-28
**Status:** SDKs cloned and ready. Both builds require specific terminal environments.

---

## Quick Summary

| Module | Build Environment | Command | Time | Status |
|--------|-------------------|---------|------|--------|
| IRIS-W10 | Git Bash | `python scripts/iris_w10_build.py build demo_apps/hello_world` | 3 min | [VERIFIED] |
| NORA-W50-W51 | Git Bash | `python scripts/nora_w50_w51_build.py build ble_wifi_provisioning` | 2-3 min | [VERIFIED] |
| NORA-W40 | Windows cmd.exe | See below | 10-30 sec | [IN_PROGRESS] |
| NORA-W30 | WSL2 or Cygwin | See below | 5-15 min | [IN_PROGRESS] |

---

## NORA-W40 (ESP32-C6) Build

### Why Git Bash Doesn't Work

ESP-IDF explicitly rejects the `MSYSTEM` environment variable set by Git Bash/MSYS2.
- Git Bash sets: `MSYSTEM=MINGW64` or `UCRT64`
- ESP-IDF export scripts detect this and exit with error
- This is intentional: MSYS2/Cygwin are not officially supported by ESP-IDF

### Solution: Use Windows Command Prompt or PowerShell

**Step 1:** Open Windows Command Prompt (`cmd.exe`)
```
Start Menu -> cmd.exe
```

**Step 2:** Navigate to example directory
```batch
cd E:\u-blox\u-blox-sho-OpenCPU\GettingStartedSDK\esp-idf\examples\get-started\hello_world
```

**Step 3:** Build
```batch
idf.py build
```

**Expected Output:**
```
[OK] Building done. Artifacts will be available in build/ directory.
```

**Binary Locations:**
- `build/hello_world.elf` (~500 KB)
- `build/hello_world.bin` (~50 KB)

**Build Time:** 10-30 seconds

### Troubleshooting

**Problem:** `idf.py: command not found`
- **Solution:** You must run from Windows Command Prompt, not PowerShell or Git Bash

**Problem:** `No module named 'esp_pylib'`
- **Solution:** Ensure you're not running from Git Bash (check for MSYSTEM variable)

---

## NORA-W30 (Realtek RTL8720DF) Build

### Build System Overview

- **Chip:** Realtek RTL8720DF (Ameba-D)
- **SDK:** Cloned to `GettingStartedSDK/ameba-rtos-d/` (320 MB)
- **Build System:** Traditional make-based (GCC + CMake)
- **Toolchain:** Downloaded automatically during first build (~300 MB)

### Option 1: Build with WSL2 (RECOMMENDED)

**Requirements:**
- WSL2 installed with Ubuntu-24.04 (or any recent Linux)
- Make and ARM GCC available in WSL

**Step 1:** Open Windows Command Prompt or PowerShell

**Step 2:** Run WSL2 build command (single command):
```batch
wsl -d Ubuntu-24.04 bash -c "cd /mnt/e/u-blox/u-blox-sho-OpenCPU/GettingStartedSDK/ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp && make all"
```

Or for more visibility, enter WSL directly:
```batch
wsl -d Ubuntu-24.04
```

Then inside WSL:
```bash
cd /mnt/e/u-blox/u-blox-sho-OpenCPU/GettingStartedSDK/ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp
make all
```

**Expected Output:**
```
[Finished] Image manipulating end
```

**Binary Locations:**
- `asdk/image/km4_image2_all.bin` (main core firmware)
- `asdk/image/km0_image2_all.bin` (low-power core firmware, optional)

**Build Time:** 5-15 minutes (toolchain downloads on first build)

### Option 2: Build with Cygwin (Windows)

**Requirements:**
- Cygwin installed with development tools (make, gcc, etc.)

**Step 1:** Open Cygwin bash terminal

**Step 2:** Navigate and build
```bash
cd /cygdrive/e/u-blox/u-blox-sho-OpenCPU/GettingStartedSDK/ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp
make all
```

**Build Time:** 5-15 minutes

### Option 3: Build on Native Linux

If you have Linux available, clone the project and run:
```bash
cd /path/to/ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp
make all
```

### Troubleshooting

**Problem:** `Makefile.include.gen: No such file or directory`
- **Solution:** This is generated during the build. Ensure you're running `make all` in the correct directory (project_hp)

**Problem:** `command not found: make`
- **Solution for WSL2:** Install build tools: `sudo apt-get install build-essential`
- **Solution for Cygwin:** Install make during Cygwin setup

**Problem:** Build downloading large files slowly
- **Solution:** This is normal on first build (~300 MB toolchain download). Wait for completion.

---

## Building Multiple Times

If you need to rebuild:

**For W40:**
```batch
cd E:\u-blox\u-blox-sho-OpenCPU\GettingStartedSDK\esp-idf\examples\get-started\hello_world
rm -rf build  (or del build)
idf.py build
```

**For W30:**
```bash
cd /path/to/project_hp
make clean
make all
```

---

## Verifying Builds

### NORA-W40
```batch
dir build
# Should show: hello_world.elf, hello_world.bin, and other files
```

### NORA-W30
```bash
ls asdk/image/
# Should show: km4_image2_all.bin
```

---

## Next Steps After Successful Build

1. **Document binary sizes** in BUILD_TEST_RESULTS.md
2. **Test with hardware** (if NORA-W30 or NORA-W40 boards available)
3. **Flash firmware** to device using appropriate tools
4. **Update project status** to [VERIFIED]

---

## Support

For issues:
- **W40:** Refer to [ESP-IDF Documentation](https://docs.espressif.com/projects/esp-idf/)
- **W30:** Refer to [Realtek Ameba Documentation](https://aiot.realmcu.com)

