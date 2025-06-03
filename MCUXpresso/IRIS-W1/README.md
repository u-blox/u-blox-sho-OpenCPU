# u-blox IRIS-W1 Module

This repository contains setup information, configuration files, and example binaries for the u-blox IRIS-W1 module.

## Folder Structure

```shell
.
├── EVK-IRIS-W1
├── USB-IRIS-W1
├── compiled_binaries
├── example_code
├── images
├── recovery_tool
│   └── blhost
├── sw_config
│   ├── App_note_15_4_Radio
│   ├── board_file
│   ├── BT_802_15_4_Calibration_Files
│   ├── flash_config
│   ├── flash_drv
│   ├── labtool
│   ├── README.md
│   ├── wifi_Calibration
│   └── wifi_txpower_cfg
└── README.md
```

### [EVK-IRIS-W1](/MCUXpresso/IRIS-W1/EVK-IRIS-W1/README.md)

Contains step-by-step instructions for setting up, building, flashing, and running applications on the **EVK-IRIS-W1** development board.

### [USB-IRIS-W1](/MCUXpresso/IRIS-W1/USB-IRIS-W1/README.md)

Contains step-by-step instructions for setting up, building, flashing, and running applications on the **USB-IRIS-W1** development board.

### [compiled_binaries](/MCUXpresso/IRIS-W1/compiled_binaries/)

Contains pre-compiled binaries to quickly test the IRIS development boards / modules.

### [example_code](/MCUXpresso/IRIS-W1/example_code/README.md)

Contains instructions to retrieve key device identifiers such as the Serial Number, Module Type, and Wi-Fi MAC Address from an IRIS module.

### [recovery_tool](/MCUXpresso/IRIS-W1/recovery_tool/blhost/)

Contains tools for recovering the module from an unknown state using the `blhost` utility.

- **blhost**: Utility for performing blhost operations.
- **IRIS_blhost.bat**: Windows batch script for IRIS module recovery.

> **Note:** Use the correct `blhost` script depending on the flash vendor variant.

### [sw_config](/MCUXpresso/IRIS-W1/sw_config/README.md)

Contains software configuration files and calibration data.

1. **App_note_15_4_Radio**:
   Application notes and configuration files for 802.15.4 radios (sourced from the NXP repository).

2. **board_files**:
   Board-specific files for the EVK-IRIS-W1 (e.g., LEDs, switches).

3. **BT_802_15_4_Calibration_Files**:
   Calibration data for Bluetooth and 802.15.4.

4. **flash_config**:
   Flash memory configuration files.

5. **flash_drv**:
   Flash memory drivers.

6. **labtool**:
   Tools and utilities for radio testing in lab environments.

7. **wifi_Calibration**:
   Wi-Fi calibration data.

8. **wifi_txpower_cfg**:
   Wi-Fi transmit power configuration files and examples.

## Identifying Module Flash Memory

### IRIS-W1:

- Modules manufactured from build version **2346** (week 46 of 2023) onward use **Fidelix** flash memory.
- Versions **2345** and earlier use **Macronix** flash memory.

> **Note:** The same flash configuration and `binary` files used for the **8 MB** Fidelix variant are also compatible with the **16 MB** variant.

## Documentation

For detailed information on using the EVK-IRIS-W1 and USB-IRIS-W1 and its hardware configuration options, refer to the [EVK-IRIS-W1 User Guide](https://www.u-blox.com/en/product/evk-iris-w1?legacy=Current#Documentation-&-resources) and [USB-IRIS-W1 User Guide](https://www.u-blox.com/en/product/usb-iris-w1?legacy=Current#Documentation-&-resources) respectively on the u-blox portal.