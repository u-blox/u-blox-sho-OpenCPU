# Labtool RF test (mfgtool)

Short note explain,  how to use the Labtool software application. The Wi-Fi, Bluetooth LE, and 802.15.4 radio Labtool commands are detailed along with some RF test examples.

### 1. Check Memory Type

Determine whether the board uses Fidelix or Macronix memory.

### 2. Download the Labtool Firmware

Obtain the latest Labtool firmware from the [NXP website](https://nxp.com): MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.xxx.xx.x.x.x (Login required).

**NOTE:** Note: The provided binaries are compiled using the uart_wifi_bridge application from SDK version 2.16.100 and have been tested with Labtool version MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.20.0-18.80.6.p16 for various memory models. With newer Labtool versions (beyond MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.20.0-18.80.6.p16), these binaries may or may not function correctly. 

If the binaries fail to work, please follow the below steps to compile from sourceo.always use the latest SDK version to compile uart_wifi_bridge binaries when working with the latest Labtool version.[Steps for build UART_Bridge Binaries](#Steps for build UART_Bridge Binaries) 

### 3. Replace UART Bridge Binaries



| Flash Type         | RW610                              | RW612                                         |
|---------------------|--------------------------------------------------|--------------------------------------------------|
| **Fidelix (8/16 MB)** |  [IRIS-W10x-30B](Fidelex_8MB/UART_Bridge_bin/RW610/) | [IRIS-W10x-00B/IRIS-W10x-10B](Fidelex_8MB/UART_Bridge_bin/RW612)     |
|  Macronix (8 MB) |  |  [IRIS-W10x-00B](Macronix_8MB/UART_Bridge_bin/RW612/) |


#### For Fidelix Memory:

 **RW612 (IRIS-W10x-00B/IRIS-W10x-10B)**

1. Replace **uart_wifi_ble_15d4_bridge.bin** located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\FreeRTOS
with **uart_wifi_ble_15d4_bridge_fi8.bin** (check table for link).
2. Rename the binary to **uart_wifi_ble_15d4_bridge.bin**

 **RW610 (IRIS-W10x-30B)**
1. Replace uart_wifi_ble_bridge.bin located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\FreeRTOS
with uart_wifi_ble_bridge_fi8.bin (check table for link).
2. Rename the binary to uart_wifi_ble_bridge.bin.


#### For Macronix Memory:

**RW612 (IRIS-W10x-00B)**
1. Replace **uart_wifi_ble_15d4_bridge.bin** located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\FreeRTOS
with **uart_wifi_ble_15d4_bridge_mx8.bin** (check table for link).
2. Rename the binary to uart_wifi_ble_15d4_bridge.bin.

### 4. Flash the Binaries

**RW612 (IRIS-W10x-00B/IRIS-W10x-10B):**
- Run the prog_flash_RW612_A2.bat script located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\FreeRTOS to flash the Labtool binaries onto the module.

**RW610 (IRIS-W10x-30B):**
- Run the prog_flash_RW610_A2.bat script located in MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x.xxx\FwImage\FreeRTOS to flash the Labtool binaries onto the module.

### 5. Power Cycle the Device

After flashing the binaries, power cycle the device.

### 6. Use the Labtool

Follow the instructions in the documentation (UM11801) to start using the Labtool.

### 7. Download the UM11801 Document

Access the [Manufacturing Software User Manual for RW61x](https://nxp.com) here (Login required).


# Steps for build UART_Bridge Binaries

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
- Replace `flash_config.c` with the u-blox-specific version from the GitHub repository[Link](../../sw_config/flash_config/).

#### Replace `mflash_drv.c`
- Navigate to: `SDK\components\flash\mflash\rdrw612bga`
- Replace `mflash_drv.c` with the u-blox-specific version from the GitHub repository[Link](../../sw_config/flash_config/).

---

### 2. Add Radio Support Macros in `app_config.h`

#### Navigate to `app_config.h`
- Path: `SDK\boards\rdrw612bga\wifi_examples\uart_wifi_bridge`

#### Add Macros Based on the Radio Support Configuration

##### RW612 Chipset (IRIS-W10x-00B/IRIS-W10x-10B):
Enable support for all radios:
```c
#define CONFIG_SUPPORT_WIFI 1
#define CONFIG_SUPPORT_BLE 1
#define CONFIG_SUPPORT_15D4 1
```

##### RW610 Chipset (IRIS-W10x-30B):
Enable Wi-Fi and BLE support only:
```c
#define CONFIG_SUPPORT_WIFI 1
#define CONFIG_SUPPORT_BLE 1
#define CONFIG_SUPPORT_15D4 0
```

---

### 3. Reference Example `app_config.h`

Refer to the pre-configured `app_config.h` for RW612 in the GitHub repository [app_config.h](app_config.h). Use it as a guide to create the corresponding configuration file for RW610.

---

### 4. Build the `uart_wifi_bridge` Example

1. Build the `uart_wifi_bridge` application example in your development environment.
2. Replace the compiled binary with the appropriate binary located in the Labtool folder:
   - Path: `Labtool\FwImage\FreeRTOS`

#### Binary Selection
- For RW610: Use `uart_wifi_ble_bridge.bin`.
- For RW612: Use `uart_wifi_ble_15d4_bridge.bin`.

---

## Notes
- Always refer to the latest documentation and repository updates for additional details.
- Verify compatibility of the binaries with your specific module before deployment.
---

For additional support, visit the [u-blox support portal](https://www.u-blox.com/en/support).

---

