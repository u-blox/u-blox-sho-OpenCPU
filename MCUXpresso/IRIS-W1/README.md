# u-blox IRIS-W1 Module

This repository contains the setup information and supported files for u-blox IRIS-W1 module:

## Folder Structure

```shell
.
├── EVK-IRIS-W1
├── images
├── README.md
├── recovery_tool
│   └── blhost
├── sw_config
│   ├── App_note_15_4_Radio
│   ├── board_file
│   ├── BT_802_15_4_Calibration_Files
│   ├── flash_config
│   ├── flash_drv
│   ├── labtool
│   ├── README.md
│   ├── wifi_Calibration
│   └── wifi_txpower_cfg
└── USB-IRIS-W1

```

### [EVK-IRIS-W1](EVK-IRIS-W1/README.md)

Contains setup information and example .bin files for the EVK-IRIS-W1 module.

### [recovery_tool](recovery_tool/blhost/)

**recovery_tool** recover the module from unknow-state using blhost utility.

- **blhost**: tools for blhost operations.
- **IRIS_blhost.bat**: Batch script for IRIS blhost operations.

**NOTE :** Use the appropriate blHost script based on the flash variant type(vendor).

### [sw_config](sw_config/README.md)

software configuration files.

1. **App_note_15_4_Radio**: 
	Application notes and configurations for 802.15.4 radios and build from NXP repo.
2. **board_file**: 
	EVK-IRIS-W1 board-specific files. (for onboard LEDs and SWs)
3. **BT_802_15_4_Calibration_Files**: 
	Bluetooth and 802.15.4 calibration data.
4. **flash_config**: 
	Configuration files for flash memory settings.
5. **flash_drv**:
	 Drivers related to flash memory operations.
6. **labtool**: 
	Radio test Tools and utilities for lab environments.
7. **wifi_Calibration**: 
	Wi-Fi calibration files and data.
8. **wifi_txpower_cfg**: 
	Wi-Fi transmission power configuration files with example files.


**NOTE :** flash_config.c and mflash_drv.c file same for EVK and USB IRIS-W1.Use the appropriate config. files based on the flash variant type(vendor). [this](EVK-IRIS-W1/examples/README.md)

### [USB-IRIS-W1](USB-IRIS-W1/README.md)

Contains setup information and exmaple files for the USB-IRIS-W1 module.
