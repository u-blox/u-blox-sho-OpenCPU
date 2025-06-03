
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
│   └── Macronix_8MB
│        └── flash_config.c
├── flash_drv
│   ├── Fidelex_8MB
│   │   ├── README.md
│   │   ├── SDK_2_16_100
│   │   │   └── mflash_drv.c
│   │   └── SDK_24_12_00
│   │        └── mflash_drv.c
│   └── Macronix_8MB
│        └── mflash_drv.c
├── labtool
│   ├── mcux_config.h
│   ├── Fidelex_8MB
│   ├── Macronix_8MB
│   ├── Single_antenna_calibration_data_text_files
│   └── README.md
├── README.md
├── wifi_Calibration
│   ├── README.md
│   ├── SDK_2_16_100
│   │   └── wifi_cal_data_ext.h
│   └── SDK_24_12_00
│       └── wifi_cal_data_rw61x_1ant.h
└── wifi_txpower_cfg
    ├── README.md
    └── wlan_txpwrlimit_cfg_WW_rw610.h
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

> **Note:** Both **Fidelix 8MB** and **Fidelix 16MB** variants use the same configuration files.

---

### [`flash_drv/`](/MCUXpresso/IRIS-W1/sw_config/flash_drv/)
Includes **flash driver (mflash)** files for different flash types:

- [`Fidelex_8MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Fidelex_8MB/)
- [`Macronix_8MB/`](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Macronix_8MB/)

Supports multiple SDK versions.

> **Note:** The same configurational driver files can be used for both **Fidelix 8MB** and **Fidelix 16MB** variants.

> 🔍 See [README.md](/MCUXpresso/IRIS-W1/README.md#identifying-module-flash-memory) for instructions on identifying the **Flash vendor** used in your module.

---

### [`labtool/`](/MCUXpresso/IRIS-W1/sw_config/labtool/)
Provides configuration and support files for the **RW61x Labtool** — a manufacturing software utility used for:
- RF control
- Calibration
- Regulatory compliance testing

Includes:
- `mcux_config.h`
- Calibration files

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
