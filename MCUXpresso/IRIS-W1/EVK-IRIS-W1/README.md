# EVK-IRIS-W1 Setup Guide

This README provides step-by-step instructions for setting up, building, flashing, and running applications on the **EVK-IRIS-W1** development board using **MCUXpresso IDE** and the latest **NXP SDK**.

---

## 🛠️ Required Tools

- **MCUXpresso IDE**
  Download and install from the official [NXP website](https://www.nxp.com/mcuxpresso/ide).

- **NXP SDK (v25.03.00 or latest)**
  Download from [MCUXpresso SDK Portal](https://mcuxpresso.nxp.com/en/welcome) and import into MCUXpresso IDE.

- **SDK Documentation**
  Access the latest documentation at [MCUXpresso SDK API Reference](https://mcuxpresso.nxp.com/mcuxsdk/latest/html/index.html).

- **J-Link Software**
  Download from [Segger Downloads](https://www.segger.com/downloads/jlink/).

---

## 🚀 Getting Started with EVK-IRIS-W1

### 1. Import Example Project

- Import the `hello_world/FreeRTOS/wifi_cli` example into your MCUXpresso workspace.

### 2. Apply Pre-Setup Configuration

- Refer to [Pre-Setup Requirement](#️-pre-setup-requirement) for flash memory and calibration setup based on the u-blox module variant.

### 3. Build the Application

- Build the project using the standard build process in MCUXpresso IDE.

### 4. Connect EVK-IRIS-W1

- Connect the EVK-IRIS-W1 board to your PC via USB-C cable at USB 3-MCULINK port.
- Make sure the board is set to **QSPI Flash boot mode**, and that the **SW8** and **SW3** DIP switches are in their default positions.
- For more information related to documentation, refer to [Notes](#-notes).

### 5. Debugging (Onboard Debugger)

- By default onboard debugger (MCU-Link) has been enabled to program the module.
- Use MCUXpresso IDE’s debug option to flash and run the application.

---

## 📡 Flashing Wi-Fi / Bluetooth Firmware

Wi-Fi and Bluetooth firmware must be flashed separately from the main application.

### Firmware Flash Addresses

| Firmware | Binary Name | Flash Address |
|----------|-------------|----------------|
| Wi-Fi    | `rw610_sb_wifi_aXX.bin` | `0x08400000` |
| Bluetooth| `rw61x_sb_ble_aXX.bin` | `0x08540000` |

> **Note**: Firmware version (`aXX`) must match the module’s chipset variant. See [Identify Chipset Variant](#-identify-the-variant-of-the-chipset).

### Flashing Tools

- Use **J-Flash Lite** or the **JLink Commander** tool for flashing firmware.

**Firmware Location in SDK**:
```
SDK/components/conn_fwloader/fw_bin
```

### Using Internal Debugger / Onboard Debugger

- Connect EVK to your PC using a USB-C cable at USB 3-MCULINK port.
- Use **J-Flash Lite / J-Link Commander** to flash Wi-Fi/BT firmware binaries.

---

## 🔍 Identify the Variant of the Chipset

Use **J-Link Commander** to read the silicon variant:

```shell
J-Link> con
Device> RW610
TIF> S
Speed> <press enter>
J-Link> mem32 45001114 1
```

### Variant Hex Values

| Variant | Value    |
|---------|----------|
| A0      | `0x7000` |
| A1      | `0x7001` |
| A2      | `0x7002` |

---

## 🔧 Flashing the Application Firmware

Once Wi-Fi/BT firmware is flashed:

- Flash the application using MCUXpresso IDE or J-Flash Lite.
- [Pre-built binaries](/MCUXpresso/IRIS-W1/compiled_binaries/) can also be used based on the module's Flash memory. For more information, refer to [Identify Module's Flash Memory](/MCUXpresso/IRIS-W1/README.md#identifying-module-flash-memory).

---

## ⚙️ Pre-Setup Requirement

Use the [software configuration files](/MCUXpresso/IRIS-W1/sw_config/) based on your module’s memory variant and SDK version. Replace the **Files** located in the SDK Location with the corresponding files from the **Replacement Source**, as detailed in the table below.

| File Type | SDK Location | Replacement Source |
|-----------|--------------|--------------------|
| `flash_config.c` | `boards/rdrw612bga/flash_config` | [flash_config](/MCUXpresso/IRIS-W1/sw_config/flash_config/) |
| `mflash_drv.c` | `components/flash/mflash/rdrw612bga` | [flash_drv](/MCUXpresso/IRIS-W1/sw_config/flash_drv/) |
| `wifi_cal_data_rw61x_1ant.h` | `middleware/wifi_nxp/incl` | [wifi_Calibration](/MCUXpresso/IRIS-W1/sw_config/wifi_Calibration/) |
| `fwk_platform_ble.c` | `middleware/wireless/framework/platform/rw61x` | [BT_802_15_4_Calibration_Files](/MCUXpresso/IRIS-W1/sw_config/BT_802_15_4_Calibration_Files/) |
| `fwk_config.h` | `middleware/wireless/framework/platform/rw61x/configs` | [BT_802_15_4_Calibration_Files](/MCUXpresso/IRIS-W1/sw_config/BT_802_15_4_Calibration_Files/) |

> **Note**: The same flash configuration and binary files used for the 8 MB Fidelix variant are also compatible with the 16 MB Fidelix variant.

---

## 🆔 Retrieving Device Identifiers

Each module has a pre-programmed **Serial Number**, **Module Type**, and **Wi-Fi MAC Address**.

➡️ **[View full guide on retrieving identifiers](/MCUXpresso/IRIS-W1/example_code/README.md)**

---

## 🛠️ Recovery Options

If the IRIS-W1 becomes unresponsive, use the `blhost` tool to restore functionality.
🔗 [Recovery Instructions](/MCUXpresso/IRIS-W1/recovery_tool/blhost/)

---

## 📘 Notes

- For detailed information on using the EVK-IRIS-W1 and its hardware options, please refer to the **EVK User Guide** available on the [IRIS-W1-EVK Product Page](https://www.u-blox.com/en/product/evk-iris-w1?legacy=Current#Documentation-&-resources).

- For additional help, refer to the official SDK documentation or contact the support team.
