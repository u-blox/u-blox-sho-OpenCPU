
# IRIS-W1 Software Configuration and Calibration

This repository contains essential software configuration files, calibration data, and board-specific settings for the **IRIS-W1** module. These files ensure proper operation of wireless subsystems and flash memory support for various vendors.

---

## 📁 Folder Structure

```shell
.
├── app-note-15-4-radio
│   └── README.md
├── board-files
├── bt-802-15-4-calibration-files
│   ├── README.md
│   ├── SDK_2_16_000
│   │   ├── fwk_config.h
│   │   └── fwk_platform_ble.c
│   │── SDK_2_16_100
│   │   ├── fwk_config.h
│   │   └── fwk_platform_ble.c
│   └── sdk-24-12-00
│       ├── fwk_config.h
│       └── fwk_platform_ble.c
├── flash-config
│   ├── Fidelex_8MB
│   │   └── flash_config.c
│   ├── Macronix_8MB
│   │   └── flash_config.c
│   └── macronix-16mb
│       └── flash_config.c
├── flash-drv
│   ├── Fidelex_8MB
│   │   ├── README.md
│   │   ├── SDK_2_16_100
│   │   │   ├── mflash_drv.c
│   │   │   └── mflash_drv.h
│   │   └── SDK_24_12_00
│   │        ├── mflash_drv.c
│   │        └── mflash_drv.h
│   ├── macronix-8mb
│   │   ├── README.md
│   │   ├── SDK_2_16_100
│   │   │   ├── mflash_drv.c
│   │   │   └── mflash_drv.h
│   │   └── SDK_24_12_00
│   │        ├── mflash_drv.c
│   │        └── mflash_drv.h
│   └── macronix-16mb
│       ├── README.md
│       └── sdk-24-12-00
│           ├── mflash_drv.c
│           └── mflash_drv.h
├── rf-test
│   └── README.md
├── linker-scripts
│   ├── README.md
│   ├── armgcc
│   │   ├── README.md
│   │   ├── flash-8mb
│   │   │   └── RW612_flash.ld
│   │   └── flash-16mb
│   │       └── RW612_flash.ld
│   └── mcuxpresso-ide
│       ├── README.md
│       └── linkerscript
│           ├── end_text.ldt
│           ├── main_data.ldt
│           ├── main_text.ldt
│           └── symbols.ldt
├── wifi-calibration
│   ├── README.md
│   ├── SDK_2_16_100
│   │   └── wifi_cal_data_ext.h
│   └── SDK_24_12_00
│       └── wifi_cal_data_rw61x_1ant.h
├── wifi-txpower-cfg
│   ├── README.md
│   └── wlan_txpwrlimit_cfg_WW_rw610.h
└── README.md
```

---

## 📘 Directory Overview

### [`app-note-15-4-radio/`](/mcuxpresso/iris-w10/sw-config/app-note-15-4-radio/)
Contains application notes and guidance for using the 802.15.4 radio subsystem.

---

### [`board-files/`](/mcuxpresso/iris-w10/sw-config/board-files/)
Includes EVK-IRIS pin mux and other board-specific configuration files.

---

### [`bt-802-15-4-calibration-files/`](/mcuxpresso/iris-w10/sw-config/bt-802-15-4-calibration-files/)
Houses **custom calibration data for Bluetooth and 802.15.4 radios** tailored for the IRIS-W1 module.

> 🛠️ These files override default NXP SDK settings to ensure correct toggling of the RF CTRL switch during radio operation.

Structure:
- Supports multiple SDK versions (e.g., `sdk-2-16-100`, `sdk-24-12-00`)
- Contains `fwk_config.h` and `fwk_platform_ble.c` files

---

### [`flash-config/`](/mcuxpresso/iris-w10/sw-config/flash-config/)
Contains configuration files for different **flash memory vendors** used in IRIS-W1 modules:

- [`fidelex-8mb/`](/mcuxpresso/iris-w10/sw-config/flash-config/fidelex-8mb/)
- [`macronix-8mb/`](/mcuxpresso/iris-w10/sw-config/flash-config/macronix-8mb/)
- [`macronix-16mb/`](/mcuxpresso/iris-w10/sw-config/flash-config/macronix-16mb/)

> **Note:** Both **Fidelix 8MB** and **Fidelix 16MB** variants use the same configuration files.

---

### [`flash-drv/`](/mcuxpresso/iris-w10/sw-config/flash-drv/)
Includes **flash driver (mflash)** files for different flash types:

- [`fidelex-8mb/`](/mcuxpresso/iris-w10/sw-config/flash-drv/fidelex-8mb/)
- [`macronix-8mb/`](/mcuxpresso/iris-w10/sw-config/flash-drv/macronix-8mb/)
- [`macronix-16mb/`](/mcuxpresso/iris-w10/sw-config/flash-drv/macronix-16mb/)


Supports multiple SDK versions.

> **Note:** The same configurational driver files can be used for both **Fidelix 8MB** and **Fidelix 16MB** variants.

> 🔍 See [README.md](/mcuxpresso/iris-w10/README.md#identifying-module-flash-memory) for instructions on identifying the **Flash vendor** used in your module.

---

### [`rf-test/`](rf-test/)
Provides the recommended RF test workflow using standard NXP SDK applications instead of the old Labtool bundle:

- `wifi_test_mode` for Wi-Fi RF verification
- EdgeFast BLE shell for Bluetooth Low Energy RF testing
- `ot_cli` for 802.15.4 RF testing through NXP vendor commands

The NXP manufacturing environment is still required for RF calibration. See the [RF test guide](rf-test/README.md) for the distinction between verification and calibration.

---

### [`linker-scripts/`](linker-scripts/)
Contains linker files for the different **flash memory densities** used in IRIS-W1 modules, split by build environment:

- [`armgcc/`](linker-scripts/armgcc/) — `.ld` scripts for `armgcc` builds (`flash-8mb`, `flash-16mb`)
- [`mcuxpresso-ide/`](linker-scripts/mcuxpresso-ide/) — `.ldt` linker templates in `linkerscript/` for MCUXpresso IDE projects

**Important:** Each toolchain uses its own linker file. MCUXpresso IDE uses `.ldt` files. ARMGCC uses `.ld` files. Don't mix them.

---

### [`wifi-calibration/`](/mcuxpresso/iris-w10/sw-config/wifi-calibration/)
Holds **Wi-Fi calibration headers** for different SDK versions and board configurations.

- `wifi_cal_data_ext.h`
- `wifi_cal_data_rw61x_1ant.h`

---

### [`wifi-txpower-cfg/`](/mcuxpresso/iris-w10/sw-config/wifi-txpower-cfg/)
Contains Wi-Fi **transmit power limit settings** in header format. These settings are essential for ensuring the module complies with regional regulatory standards.

- `wlan_txpwrlimit_cfg_WW_rw610.h`

---

## 🔗 Additional Notes

- Be sure to select the correct SDK version and flash memory variant when integrating these files into your project.

---

## 📞 Support

For more details, refer to NXP documentation or contact u-blox support.
