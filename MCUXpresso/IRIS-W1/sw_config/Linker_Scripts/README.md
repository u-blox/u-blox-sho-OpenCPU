# Linker Scripts

Linker files for the **RW612** chipset, organized by the build toolchain. For IRIS-W1 modules, the linker setup is part of the required pre-setup condition and must be updated together with the flash configuration and flash driver files (`flash_config.c` and `mflash_drv.c`).

Select the folder that matches your build environment:

| Toolchain / IDE | Folder | File type |
|---|---|---|
| ARMGCC (command-line `armgcc` build) | [`ARMGCC/`](ARMGCC/) | `.ld` |
| MCUXpresso IDE (managed build) | [`MCUXpressoIDE/`](MCUXpressoIDE/) | `.ldt` |

> **Important:** Use only the files for the toolchain you build with. MCUXpresso IDE does not consume the ARMGCC `.ld` file, and the `armgcc` build does not use the `.ldt` templates.

> **Pre-setup requirement:** The correct linker files are part of the project setup before building the application. They must match the module Flash density and the selected SDK toolchain.

## Folder Structure

```shell
.
├── ARMGCC
│   ├── Flash_8MB
│   │   └── RW612_flash.ld
│   ├── Flash_16MB
│   │   └── RW612_flash.ld
│   └── README.md
├── MCUXpressoIDE
│   ├── main_text.ldt
│   ├── main_data.ldt
│   ├── end_text.ldt
│   ├── symbols.ldt
│   └── README.md
└── README.md
```

## MCUXpresso IDE templates

The MCUXpresso IDE folder contains the linker script templates used by the managed build flow:

- `main_text.ldt`
- `main_data.ldt`
- `end_text.ldt`
- `symbols.ldt`

Copy these files into the project's `linkscripts` folder before building. This is part of the pre-setup requirement for MCUXpresso IDE projects.

## Selecting the Flash Size

Use the file set that matches the Flash density of your module. See [Identifying Module Flash Memory](/MCUXpresso/IRIS-W1/README.md#identifying-module-flash-memory) to determine the memory fitted on your module.

> **NXP note:** Labtool is primarily a manufacturing / RF calibration tool. It is not the normal path for routine RF verification. For standard RF testing, use the NXP RF test applications such as `wifi_test_mode`, the EdgeFast BLE shell, or `ot_cli` as described in the [RF_Test guide](../RF_Test/README.md).

---

## Support

If you encounter any issues, please refer to the SDK documentation or reach out for support.