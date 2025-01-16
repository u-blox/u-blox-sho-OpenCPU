
## Software Configuration 

This folder contains essential software configuration and calibration files for the IRIS-W1 module.

## Folder Structure

```shell
.
├── App_note_15_4_Radio
│   └── README.md
├── board_file 
├── BT_802_15_4_Calibration_Files
│   ├── SDK_2_16_000
│   │   ├── fwk_config.h
│   │   └── fwk_platform_ble.c
│   └── SDK_2_16_100
│       ├── fwk_config.h
│       └── fwk_platform_ble.c
├── flash_config
│   ├── Fidelex_8MB
│   └── Macronix_8MB
├── flash_drv
│   ├── Fidelex_8MB
│   └── Macronix_8MB
├── labtool
│   ├── app_config.h
│   ├── Fidelex_8MB
│   ├── Macronix_8MB
│   └── README.md
├── README.md
├── wifi_Calibration
└── wifi_txpower_cfg
```


### App_note_15_4_Radio
- Contains application notes README and resources for working with the 802.15.4 radio.

### board_file
- EVK-IRIS pin mux file ,board-specific configuration files.

### BT_802_15_4_Calibration_Files

This directory (**BT_802_15_4_Calibration_Files**) contains custom calibration data specifically for IRIS-W1 modules to ensure proper toggling of the RF CTRL switch. The default settings in the NXP SDK may not correctly manage this functionality. This is an important configuration file when we use BT/Wi-Fi applications.

### flash_config 

IRIS-W1 is built with different vendors of flash memory (Fidelex, Macronix). This directory holds configuration files for flash memory. It includes subdirectories for different flash memory types.

- **Fidelex_8MB:**  [Link](flash_config/Fidelex_8MB/) 
- **Macronix_8MB:** [Link](flash_config/Macronix_8MB/) 


**NOTE**: We can use the same flash file, and .bin files for the **Fidelix 16 MB** variant as for the **8 MB** variant.

### flash_drv

This directory (**flash_drv**) contains mflash drv files. Similar to the configuration directory, it includes subdirectories for different flash memory types.

- **Fidelex_8MB:**  [Link](flash_drv/Fidelex_8MB/) 
- **Macronix_8MB:** [Link](flash_drv/Macronix_8MB/) 

**NOTE**: We can use the same flash file, and .bin files for the **Fidelix 16 MB** variant as for the **8 MB** variant.

**NOTE:** please check [this](../EVK-IRIS-W1/examples/README.md) to indetifty vendor type on module.

### labtool 

This document provides guidance on the usage of RW61x manufacturing software (Labtool) application. Labtool is a software application used to control and run various RF and regulatory compliance tests.

### wifi_Calibration

This directory (**wifi_Calibration**) contains calibration data specifically for IRIS-W1 modules.

### wifi_txpower_cfg

This directory (**wifi_txpower_cfg**) provide infomation and example header file for setting the txpower limit specifically for IRIS-W1 modules.
