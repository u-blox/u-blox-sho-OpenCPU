# u-blox IRIS-W1 Module

This repository contains the setup information and supported files for u-blox IRIS-W1 module:

## Folder Structure

```shell
├── EVK-IRIS-W1
├── sw_config
├── tools
└── USB-IRIS-W1
```

### [EVK-IRIS-W1](EVK-IRIS-W1/README.md)

Contains setup information and example .bin files for the EVK-IRIS-W1 module.

### [sw_config](sw_config/README.md)

software configuration files.

**flash_config and mflash_drv** files 

- Fidelex_8MB: Fidelex 8MB flash file.
- Macronix_8MB: Macronix 8MB flash file.

**NOTE :** flash_config.c and mflash_drv.c file same for EVK and USB IRIS-W1.Use the appropriate config. files based on the flash variant type(vendor). [this](EVK-IRIS-W1/examples/README.md)

### [tools](tools)

- **blhost**: tools for blhost operations.
- **IRIS_blhost.bat**: Batch script for IRIS blhost operations.

**NOTE :** Use the appropriate blHost script based on the flash variant type(vendor).

### [USB-IRIS-W1](USB-IRIS-W1/README.md)

Contains setup information and exmaple files for the USB-IRIS-W1 module.
