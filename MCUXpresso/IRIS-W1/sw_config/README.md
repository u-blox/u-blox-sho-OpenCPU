
# IRIS-W1 Software Configuration and Calibration

This repository contains essential software configuration files, calibration data, and board-specific settings for the **IRIS-W1** module. These files ensure proper operation of wireless subsystems and flash memory support for various vendors.

---

## 📁 Folder Structure

```shell
.
├── App_note_15_4_Radio
│   └── README.md
├── board_files
├── BT_802_15_4_Calibration_Files
│   ├── README.md
│   ├── SDK_2_16_000
│   │   ├── fwk_config.h
│   │   └── fwk_platform_ble.c
│   │── SDK_2_16_100
│   │   ├── fwk_config.h
│   │   └── fwk_platform_ble.c
│   └── SDK_24_12_00
│       ├── fwk_config.h
│       └── fwk_platform_ble.c
├── flash_config
│   ├── Fidelex_8MB
│   │   └── flash_config.c
│   ├── Macronix_8MB
│   │   └── flash_config.c
│   └── Macronix_16MB
│       └── flash_config.c
├── flash_drv
│   ├── Fidelex_8MB
│   │   ├── README.md
│   │   ├── SDK_2_16_100
│   │   │   ├── mflash_drv.c
│   │   │   └── mflash_drv.h
│   │   └── SDK_24_12_00
│   │        ├── mflash_drv.c
│   │        └── mflash_drv.h
│   ├── Macronix_8MB
│   │   ├── README.md
│   │   ├── SDK_2_16_100
│   │   │   ├── mflash_drv.c
│   │   │   └── mflash_drv.h
│   │   └── SDK_24_12_00
│   │        ├── mflash_drv.c
│   │        └── mflash_drv.h
│   └── Macronix_16MB
│       ├── README.md
│       └── SDK_24_12_00
│           ├── mflash_drv.c
│           └── mflash_drv.h
├── RF_Test
│   └── README.md
├── Linker_Scripts
│   ├── README.md
│   ├── ARMGCC
│   │   ├── README.md
│   │   ├── Flash_8MB
│   │   │   └── RW612_flash.ld
│   │   └── Flash_16MB
│   │       └── RW612_flash.ld
│   └── MCUXpressoIDE
│       └── README.md
├── wifi_Calibration
│   ├── README.md
│   ├── SDK_2_16_100
│   │   └── wifi_cal_data_ext.h
│   └── SDK_24_12_00
│       └── wifi_cal_data_rw61x_1ant.h
├── wifi_txpower_cfg
│   ├── README.md
│   └── wlan_txpwrlimit_cfg_WW_rw610.h
└── README.md
```

---

## 📘 Directory Overview

### [`App_note_15_4_Radio/`](/MCUXpresso/IRIS-W1/sw_config/App_note_15_4_Radio/)
Contains application notes and guidance for using the 802.15.4 radio subsystem.

---

### [`board_files/`](/MCUXpresso/IRIS-W1/sw_config/board_files/)
Includes EVK-IRIS pin mux and other board-specific configuration files.

---

### [`BT_802_15_4_Calibration_Files/`](/MCUXpresso/IRIS-W1/sw_config/BT_802_15_4_Calibration_Files/)
Houses **custom calibration data for Bluetooth and 802.15.4 radios** tailored for the IRIS-W1 module.

> 🛠️ These files override default NXP SDK settings to ensure correct toggling of the RF CTRL switch during radio operation.

Structure:
- Supports multiple SDK versions (e.g., `SDK_2_16_100`, `SDK_24_12_00`)
- Contains `fwk_config.h` and `fwk_platform_ble.c` files

---

### [`flash_config/`](/MCUXpresso/IRIS-W1/sw_config/flash_config/)
Contains configuration files for different **flash memory vendors** used in IRIS-W1 modules:

- [`Fidelex_8MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_config/Fidelex_8MB/)
- [`Macronix_8MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_config/Macronix_8MB/)
- [`Macronix_16MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_config/Macronix_16MB/)

> **Note:** Both **Fidelix 8MB** and **Fidelix 16MB** variants use the same configuration files.

---

### [`flash_drv/`](/MCUXpresso/IRIS-W1/sw_config/flash_drv/)
Includes **flash driver (mflash)** files for different flash types:

- [`Fidelex_8MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Fidelex_8MB/)
- [`Macronix_8MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Macronix_8MB/)
- [`Macronix_16MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Macronix_16MB/)


Supports multiple SDK versions.

> **Note:** The same configurational driver files can be used for both **Fidelix 8MB** and **Fidelix 16MB** variants.

> 🔍 See [README.md](/MCUXpresso/IRIS-W1/README.md#identifying-module-flash-memory) for instructions on identifying the **Flash vendor** used in your module.

---

### [`RF_Test/`](RF_Test/)
Provides the recommended RF test workflow using standard NXP SDK applications instead of the old Labtool bundle:

- `wifi_test_mode` for Wi-Fi RF verification
- EdgeFast BLE shell for Bluetooth Low Energy RF testing
- `ot_cli` for 802.15.4 RF testing through NXP vendor commands

The NXP manufacturing environment is still required for RF calibration. See the [RF test guide](RF_Test/README.md) for the distinction between verification and calibration.

---

### [`Linker_Scripts/`](Linker_Scripts/)
Contains linker files for the different **flash memory densities** used in IRIS-W1 modules, split by build environment:

- [`ARMGCC/`](Linker_Scripts/ARMGCC/) — `.ld` scripts for `armgcc` builds (`Flash_8MB`, `Flash_16MB`)
- [`MCUXpressoIDE/`](Linker_Scripts/MCUXpressoIDE/) — `.ldt` linker templates for MCUXpresso IDE projects

> **Note:** Update the linker configuration whenever `flash_config.c` and `mflash_drv.c` are replaced, using the variant that matches your toolchain.

---

### [`wifi_Calibration/`](/MCUXpresso/IRIS-W1/sw_config/wifi_Calibration/)
Holds **Wi-Fi calibration headers** for different SDK versions and board configurations.

- `wifi_cal_data_ext.h`
- `wifi_cal_data_rw61x_1ant.h`

---

### [`wifi_txpower_cfg/`](/MCUXpresso/IRIS-W1/sw_config/wifi_txpower_cfg/)
Contains Wi-Fi **transmit power limit settings** in header format. These settings are essential for ensuring the module complies with regional regulatory standards.

- `wlan_txpwrlimit_cfg_WW_rw610.h`

---

## 🔗 Additional Notes

- Be sure to select the correct SDK version and flash memory variant when integrating these files into your project.

---

## 📞 Support

For more details, refer to NXP documentation or contact u-blox support.
