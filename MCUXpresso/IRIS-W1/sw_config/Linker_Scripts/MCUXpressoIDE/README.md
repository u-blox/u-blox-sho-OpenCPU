# MCUXpresso IDE Linker Templates

MCUXpresso IDE managed builds do not use the `armgcc` `RW612_flash.ld` file. The IDE generates the final linker script from **linker script templates** (`.ldt`) and from the memory layout stored in the project.

Use these templates when the application is built inside **MCUXpresso IDE**. For `armgcc` command-line builds, use the [ARMGCC](../ARMGCC/) scripts instead.

> **Pre-setup condition:** The correct MCUXpresso IDE linker templates are part of the required setup before building the application. They must be selected to match the IRIS-W1 module's Flash density and the project toolchain.

## Available Templates

This folder contains the IRIS-W1 MCUXpresso linker templates:

- `main_text.ldt`
- `main_data.ldt`
- `end_text.ldt`
- `symbols.ldt`

These files are the replacement set for the MCUXpresso IDE build flow.

## Adding the Templates to a Project

1. Open the project in MCUXpresso IDE.
2. In the project tree, locate (or create) the `linkscripts` folder:

   ```text
   <project>/
   └── linkscripts/
       └── *.ldt
   ```

3. Copy the `.ldt` files from this folder into `<project>/linkscripts`.
4. Rebuild the project. The IDE regenerates the linker script from the templates.

> **Note:** Custom templates in `linkscripts` override the IDE defaults for that project only. They are not shared between projects.

## Checking the Memory Configuration

The templates must match the Flash density of the module. Verify the Flash size in the project memory configuration:

**Project Properties → C/C++ Build → MCU settings → Memory details**

See [Identifying Module Flash Memory](/MCUXpresso/IRIS-W1/README.md#identifying-module-flash-memory) to determine the memory fitted on your module.

## Keeping Configuration Consistent

When the flash-related files are updated for an IRIS-W1 module, update the linker configuration in the same step:

| File | Purpose |
|---|---|
| `flash_config.c` | Flash configuration block |
| `mflash_drv.c` | Flash driver |
| `.ldt` templates | Memory layout used by the MCUXpresso IDE build |

> **NXP note:** Labtool is mainly used in manufacturing and RF calibration workflows. It is not the normal path for routine RF verification. For standard RF testing, use the NXP RF test applications such as `wifi_test_mode`, the EdgeFast BLE shell, or `ot_cli`.

---

## Support

If you encounter any issues, please refer to the SDK documentation or reach out for support.
