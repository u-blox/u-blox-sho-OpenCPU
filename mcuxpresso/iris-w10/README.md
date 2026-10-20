# u-blox IRIS-W1 Module

This repository contains setup information, configuration files, and example binaries for the u-blox IRIS-W1 module.

## Folder Structure

```shell
.
├── EVK-IRIS-W1
├── USB-IRIS-W1
├── compiled-binaries
├── example-code
├── images
├── recovery-tool
│   └── blhost
├── sw-config
│   ├── app-note-15-4-radio
│   ├── board_file
│   ├── bt-802-15-4-calibration-files
│   ├── flash-config
│   ├── flash-drv
│   ├── rf-test
│   ├── linker-scripts
│   ├── wifi-calibration
│   ├── wifi-txpower-cfg
│   └── README.md
│
└── README.md
```

### [EVK-IRIS-W1](/mcuxpresso/iris-w10/evk-iris-w1/README.md)

Contains step-by-step instructions for setting up, building, flashing, and running applications on the **EVK-IRIS-W1** development board.

### [USB-IRIS-W1](/mcuxpresso/iris-w10/usb-iris-w1/README.md)

Contains step-by-step instructions for setting up, building, flashing, and running applications on the **USB-IRIS-W1** development board.

### [compiled-binaries](/mcuxpresso/iris-w10/compiled-binaries/)

Contains pre-compiled binaries to quickly test the IRIS development boards / modules.

### [example-code](/mcuxpresso/iris-w10/example-code/README.md)

Contains instructions to retrieve key device identifiers such as the Serial Number, Module Type, and Wi-Fi MAC Address from an IRIS module.

### [recovery-tool](/mcuxpresso/iris-w10/recovery-tool/blhost/)

Contains tools for recovering the module from an unknown state using the `blhost` utility.

- **blhost**: Utility for performing blhost operations.
- **IRIS_blhost.bat**: Windows batch script for IRIS module recovery.

> **Note:** Use the correct `blhost` script depending on the flash vendor variant.

### [sw-config](/mcuxpresso/iris-w10/sw-config/README.md)

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

6. **RF_Test**:
   Guidance for using the NXP SDK RF test applications for Wi-Fi, BLE, and 802.15.4.

7. **Linker_Scripts**:
   Linker scripts for ARMGCC (`.ld`) and linker templates for MCUXpresso IDE (`.ldt`).

8. **wifi_Calibration**:
   Wi-Fi calibration data.

9. **wifi_txpower_cfg**:
   Wi-Fi transmit power configuration files and examples.

## Identifying Module Flash Memory

### IRIS-W1:

- Modules manufactured from build version **2346** (week 46 of 2023) onward use **Fidelix** flash memory.
- Versions **2345** and earlier use **Macronix** flash memory.

> **Note:** The same flash configuration and `binary` files used for the **8 MB** Fidelix variant are also compatible with the **16 MB** variant.

## Documentation

For detailed information on using the EVK-IRIS-W1 and USB-IRIS-W1 and its hardware configuration options, refer to the [EVK-IRIS-W1 User Guide](https://www.u-blox.com/en/product/evk-iris-w1?legacy=Current#Documentation-&-resources) and [USB-IRIS-W1 User Guide](https://www.u-blox.com/en/product/usb-iris-w1?legacy=Current#Documentation-&-resources) respectively on the u-blox portal.