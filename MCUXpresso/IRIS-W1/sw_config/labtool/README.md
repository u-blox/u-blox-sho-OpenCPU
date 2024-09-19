
## labtool RF test (mfg)


Short note explain,  how to use the Labtool software application. The Wi-Fi, Bluetooth LE, and 802.15.4 radio Labtool commands are detailed along with some RF test examples.

### 1. Check Memory Type

Determine whether the board uses Fidelex or Macronix memory.

### 2. Download the Labtool Firmware

Obtain the latest Labtool firmware from the [NXP website](https://nxp.com): MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.16.0-18.80.6.p11 (Login required).

### 3. Replace UART Bridge Binaries

#### For Fidelex Memory:

1. Navigate to `MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.10.1-18.80.6.p11\FwImage\A2`.
2. Replace `uart_wifi_ble_bridge.bin` with `uart_bridge_FI_8MB.bin` from `Labtool\Fidelex 8MB\UART_BRIDGE`.

#### For Macronix Memory:

1. Navigate to `MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.10.1-18.80.6.p11\FwImage\A2`.
2. Replace `uart_wifi_ble_bridge.bin` with `uart_bridge_MX_8MB.bin` from `Labtool\Macronix 8MB\UART_BRIDGE`.

### 4. Update the J-Link Script

1. Locate `prog_flash_RW612_A2.jlink` in `MFG-RW61X-MF-BRG-U16-WIN-X86-2.0.0.10.1-18.80.6.p11-Macronix 8MB\FwImage\A2`.
2. Replace the line:
   ```
   loadbin uart_wifi_ble_bridge.bin,0x08000000
   ```
   with:
   - `loadbin uart_bridge_MX_8MB.bin,0x08000000` for Macronix memory.
   - `loadbin uart_bridge_FI_8MB.bin,0x08000000` for Fidelex memory.

### 5. Flash the Binaries

Run `prog_flash_RW612_A2.bat` to flash the Labtool binaries onto the module.

### 6. Power Cycle the Device

After flashing the binaries, power cycle the device.

### 7. Use the Labtool

Follow the instructions in the documentation (UM11801) to start using the Labtool.

### 8. Download the UM11801 Document

Access the [Manufacturing Software User Manual for RW61x](https://nxp.com) here (Login required).
