# Linker Scripts

This repository contains ARMGCC linker scripts for **8 MB** and **16 MB** external Flash memory configurations, compatible with different SDK versions of the **RW612** chipset.

Follow the instructions below to replace the appropriate linker script in your SDK project.

## Flash Memory Configurations

Replace the existing linker script file **`RW612_flash.ld`** located in your SDK application. For example:

```text
SDK_2x_xx_xxx_RD-RW612-BGA/
└── boards/
    └── rdrw612bga/
        └── demo_apps/
            └── hello_world/
                └── armgcc/
                    └── RW612_flash.ld
```

Replace it with the appropriate linker script based on your Flash memory size:

| Flash Memory Size | Linker Script |
|-------------------|---------------|
| **8 MB** | [`Flash_8MB/RW612_flash.ld`](/MCUXpresso/IRIS-W1/sw_config/Linker_Scripts/Flash_8MB/RW612_flash.ld) |
| **16 MB** | [`Flash_16MB/RW612_flash.ld`](/MCUXpresso/IRIS-W1/sw_config/Linker_Scripts/Flash_16MB/RW612_flash.ld) |

> **Note:** Make sure you use the linker script that matches the Flash memory size of your hardware.

---

## Support

If you encounter any issues, please refer to the SDK documentation or reach out for support.