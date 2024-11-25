
## Software Configuration 

This folder contains essential software configuration and calibration files for the IRIS-W1 module.

## Folder Structure

```shell
.
├── board_file 
├── bt_Calibration
│   ├── fwk_config.h
│   └── fwk_platform_ble.c
├── flash_config
│   ├── Fidelex_8MB
│   └── Macronix_8MB
├── flash_drv
│   ├── Fidelex_8MB
│   └── Macronix_8MB
├── labtool
│   ├── Fidelex_8MB
│   ├── Macronix_8MB
│   └── README.md
├── README.md
├── wifi_Calibration
└── wifi_txpower_cfg
```

### bt_Calibration

This directory (**bt_Calibration**) contains custom calibration data specifically tailored for IRIS-W1 modules to ensure proper toggling of the RF CTRL switch. The default settings in the NXP SDK may not correctly manage this functionality. This is an important configuration file when we use BT/Wi-Fi applications.

### flash_config 

IRIS-W1 is built with different vendors of flash memory (Fidelex, Macronix). This directory holds configuration files for flash memory. It includes subdirectories for different flash memory types.

- **Fidelex_8MB:** Configuration files specific to the Fidelex 8MB flash memory.
- **Macronix_8MB:** Configuration files specific to the Macronix 8MB flash memory.

### flash_drv

This directory (**flash_drv**) contains mflash drv files. Similar to the configuration directory, it includes subdirectories for different flash memory types.

- **Fidelex_8MB:** files specific to the Fidelex 8MB flash memory.
- **Macronix_8MB:** files specific to the Macronix 8MB flash memory.

**NOTE:** please check [this](../EVK-IRIS-W1/examples/README.md) to indetifty vendor type on module.

### labtool 

This document provides guidance on the usage of RW61x manufacturing software (Labtool) application. Labtool is a software application used to control and run various RF and regulatory compliance tests.


### wifi_Calibration

This directory (**wifi_Calibration**) contains calibration data specifically for IRIS-W1 modules.

### wifi_txpower_cfg

This directory (**wifi_txpower_cfg**) provide infomation and example header file for setting the txpower limit specifically for IRIS-W1 modules.
