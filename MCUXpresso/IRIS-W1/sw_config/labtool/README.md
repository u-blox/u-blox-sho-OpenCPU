# Labtool RF test (mfgtool)

This guide provides step-by-step instructions for setting up and using the Labtool RF Test (mfgtool) with u-blox IRIS modules. It includes details on selecting the correct memory type, downloading and flashing Labtool firmware, replacing UART bridge binaries, and performing RF tests using Wi-Fi, BLE, and 802.15.4 radio commands. Ideal for validating RF functionality during manufacturing or development.

### 1. Check Memory Type

Determine whether the board uses Fidelix or Macronix memory.

### 2. Download the Labtool Firmware

Obtain the latest Labtool firmware from the [NXP website](https://nxp.com): MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.xxx.xx.x.x.x (Login required).

**NOTE:** The provided binaries are compiled using the uart_wifi_bridge application from SDK version 25.03.00 and have been tested with Labtool version MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.35.0-18.80.6.p34 for various memory models. With newer Labtool versions (beyond MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.35.0-18.80.6.p34), these binaries may or may not function correctly.

If the binaries fail to work, please follow the below steps to compile from source, always use the latest SDK version to compile uart_wifi_bridge binaries when working with the latest Labtool version. [Steps for building UART_Bridge Binaries](#steps-for-building-uart_bridge-binaries)

### 3. Replace UART Bridge Binaries



| Flash Type         | RW610                              | RW612                                         |
|---------------------|--------------------------------------------------|--------------------------------------------------|
| **Fidelix (8/16 MB)** |  [IRIS-W10x-30B](Fidelex_8MB/UART_Bridge_bin/RW610/) | [IRIS-W10x-00B/IRIS-W10x-10B](Fidelex_8MB/UART_Bridge_bin/RW612)     |
|  **Macronix (8 MB)** |  |  [IRIS-W10x-00B](Macronix_8MB/UART_Bridge_bin/RW612/) |


#### For Fidelix Memory:

 **RW612 (IRIS-W10x-00B/IRIS-W10x-10B)**

1. Replace **uart_wifi_ble_15d4_bridge_monolthic_a2.bin** located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\RD_Board\FreeRTOS
with **[uart_wifi_ble_15d4_bridge_monolthic_a2_fi8.bin](/MCUXpresso/IRIS-W1/sw_config/labtool/Fidelex_8MB/UART_Bridge_bin/RW612/uart_wifi_ble_15d4_bridge_monolthic_a2_fi8.bin)**.
2. Rename the binary to **uart_wifi_ble_15d4_bridge_monolthic_a2.bin**

 **RW610 (IRIS-W10x-30B)**
1. Replace uart_wifi_ble_bridge_monolthic_a2.bin located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\RD_Board\FreeRTOS
with **[uart_wifi_ble_bridge_monolthic_a2_fi8.bin](/MCUXpresso/IRIS-W1/sw_config/labtool/Fidelex_8MB/UART_Bridge_bin/RW610/uart_wifi_ble_bridge_monolthic_a2_fi8.bin)**.
2. Rename the binary to **uart_wifi_ble_bridge_monolthic_a2.bin**.


#### For Macronix Memory:

**RW612 (IRIS-W10x-00B)**
1. Replace **uart_wifi_ble_15d4_bridge_monolthic_a2.bin** located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\RD_Board\FreeRTOS
with **[uart_wifi_ble_15d4_bridge_monolthic_a2_mx8.bin](/MCUXpresso/IRIS-W1/sw_config/labtool/Macronix_8MB/UART_Bridge_bin/RW612/uart_wifi_ble_15d4_bridge_monolthic_a2_mx8.bin)**.
2. Rename the binary to **uart_wifi_ble_15d4_bridge_monolthic_a2.bin**.

### 4. Flash the Binaries

**RW612 (IRIS-W10x-00B/IRIS-W10x-10B):**
- Run the **prog_flash_RW612_A2-monolthic.bat** script located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\RD_Board\FreeRTOS to flash the Labtool binaries onto the module.

**RW610 (IRIS-W10x-30B):**
- Run the **prog_flash_RW610_A2-monolthic.bat** script located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\RD_Board\FreeRTOS to flash the Labtool binaries onto the module.

### 5. Power Cycle the Device

After flashing the binaries, power cycle the device.

### 6. Use the Labtool

Follow the instructions in the documentation (UM11801) to start using the Labtool.

### 7. Load Calibration Data

Follow the instructions in the [README](/MCUXpresso/IRIS-W1/sw_config/labtool/Single_antenna_calibration_data_text_files/README.md) which details the procedure to load the calibration data for operating radio properly.

### 8. Download the UM11801 Document

Access the [Manufacturing Software User Manual for RW61x](https://nxp.com) here (Login required).


# Steps for building UART_Bridge Binaries

This guide outlines the steps for creating UART bridge binaries for u-blox modules using the SDK and Labtool.

---

## Prerequisites

Before starting, ensure you have:
- Access to the SDK for the target u-blox module (RW610 or RW612).
- Labtool software.

---

## Steps

### 1. Update Flash Configuration Files

#### Replace `flash_config.c`
- Navigate to: `SDK\boards\rdrw612bga\flash_config`
- Replace `flash_config.c` with the u-blox-specific version, available at: [flash_config](/MCUXpresso/IRIS-W1/sw_config/flash_config/).

#### Replace `mflash_drv.c`
- Navigate to: `SDK\components\flash\mflash\rdrw612bga`
- Replace `mflash_drv.c` with the u-blox-specific version, available at: [flash_drv](/MCUXpresso/IRIS-W1/sw_config/flash_drv/).

---

### 2. Add Radio Support Macros in `mcux_config.h`

#### Navigate to `mcux_config.h`
- Path: `SDK\boards\rdrw612bga\wifi_examples\uart_wifi_bridge`

#### Add Macros Based on the Radio Support Configuration

##### RW612 Chipset (IRIS-W10x-00B/IRIS-W10x-10B):
Enable all radio features and use a monolithic MFG firmware combining Wi-Fi, BLE, and 802.15.4:
```c
#define CONFIG_MFG_MONOLITHIC       1

#define CONFIG_SUPPORT_WIFI         1
#define CONFIG_SUPPORT_BLE          1
#define CONFIG_SUPPORT_15D4         1

#define CONFIG_MONOLITHIC_WIFI      1
#define CONFIG_MONOLITHIC_BLE       0
#define CONFIG_MONOLITHIC_BLE_15_4  1
```

##### RW610 Chipset (IRIS-W10x-30B):
Enable Wi-Fi and BLE support, disable 802.15.4, and use a monolithic Wi-Fi + BLE MFG firmware:
```c
#define CONFIG_MFG_MONOLITHIC       1

#define CONFIG_SUPPORT_WIFI         1
#define CONFIG_SUPPORT_BLE          1
#define CONFIG_SUPPORT_15D4         0

#define CONFIG_MONOLITHIC_WIFI      1
#define CONFIG_MONOLITHIC_BLE       1
#define CONFIG_MONOLITHIC_BLE_15_4  0
```

---

### 3. Reference Example `mcux_config.h`

Refer to the pre-configured `mcux_config.h` for RW612 in the GitHub repository [mcux_config.h](mcux_config.h). Use it as a guide to create the corresponding configuration file for RW610.

---

### 4. Build the `uart_wifi_bridge` Example

1. Build the `uart_wifi_bridge` application example in your development environment.
2. Replace the compiled binary with the appropriate binary located in the Labtool folder:
   - Path: `Labtool\FwImage\RD_Board\FreeRTOS`

#### Binary Selection
- For RW610: Use `uart_wifi_ble_bridge_monolthic_a2.bin`.
- For RW612: Use `uart_wifi_ble_15d4_bridge_monolthic_a2.bin`.

---

## Notes
- Always refer to the latest documentation and repository updates for additional details.
- Verify compatibility of the binaries with your specific module before deployment.
---

For additional support, visit the [u-blox support portal](https://www.u-blox.com/en/support).

--