# ARMGCC Linker Scripts

ARMGCC linker scripts for **8 MB** and **16 MB** external Flash memory configurations, compatible with different SDK versions of the **RW612** chipset.

Use these files only when building with the `armgcc` toolchain. For MCUXpresso IDE projects, use the [MCUXpressoIDE](../MCUXpressoIDE/) linker templates instead.

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
| **8 MB** | [`Flash_8MB/RW612_flash.ld`](Flash_8MB/RW612_flash.ld) |
| **16 MB** | [`Flash_16MB/RW612_flash.ld`](Flash_16MB/RW612_flash.ld) |

> **Note:** Make sure you use the linker script that matches the Flash memory size of your hardware.

