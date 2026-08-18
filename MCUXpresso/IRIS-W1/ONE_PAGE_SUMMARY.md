# IRIS-W1 Update Summary

This page summarizes the recent documentation and setup changes for the IRIS-W1 support package.

## What changed

### 1) RF test guidance was updated
The repository no longer emphasizes Labtool as the main RF verification path. Instead, it points users to the standard NXP SDK RF test applications:

- Wi-Fi: `wifi_test_mode`
- BLE: EdgeFast BLE shell
- 802.15.4: `ot_cli`

The workflow is documented in [sw_config/RF_Test/README.md](sw_config/RF_Test/README.md).

### 2) Linker files were split by build toolchain
The linker configuration is now organized by build environment:

- [sw_config/Linker_Scripts/ARMGCC](sw_config/Linker_Scripts/ARMGCC/) for `.ld` scripts used with `armgcc`
- [sw_config/Linker_Scripts/MCUXpressoIDE](sw_config/Linker_Scripts/MCUXpressoIDE/) for `.ldt` templates used with MCUXpresso IDE

This avoids mixing `armgcc` and MCUXpresso build artifacts, which are not interchangeable.

### 3) Linker setup is part of the required pre-setup
For IRIS-W1 modules, the correct linker script or template must be selected together with the matching flash configuration and flash driver before building the application.

This is included in the setup guidance for:

- [EVK-IRIS-W1/README.md](EVK-IRIS-W1/README.md)
- [USB-IRIS-W1/README.md](USB-IRIS-W1/README.md)

### 4) NXP Labtool clarification
NXP guidance distinguishes between:

- Routine RF verification: use the standard NXP RF test applications
- RF calibration / manufacturing: Labtool may still be required in the NXP MFG environment

This clarification is included as a note in the relevant documentation so users do not treat Labtool as the normal test flow.

## Recommended usage

Use the IRIS-W1 support package in this order:

1. Identify Module Flash Memory
2. Select the correct flash configuration and flash driver
3. Select the matching linker setup for the build toolchain
4. Build the target application
5. Use the RF test app that matches the radio under test

## Key reference documents

- [README.md](README.md)
- [sw_config/README.md](sw_config/README.md)
- [sw_config/RF_Test/README.md](sw_config/RF_Test/README.md)
- [sw_config/Linker_Scripts/README.md](sw_config/Linker_Scripts/README.md)
- [sw_config/Linker_Scripts/MCUXpressoIDE/README.md](sw_config/Linker_Scripts/MCUXpressoIDE/README.md)

## Bottom line

The repo now reflects the supported path for normal RF verification: use the NXP SDK RF test applications, keep the linker files toolchain-specific, and treat Labtool as a calibration/manufacturing-only tool rather than a standard development workflow.
