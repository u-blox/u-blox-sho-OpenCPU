# EVK-IRIS-W1 

This README provides instructions for setting up and running the "hello_world" and "Wi-Fi & BT"application using MCUXpresso IDE and the latest SDK. 

## Setup Instructions

1. **Install MCUXpresso IDE**: Make sure you have MCUXpresso IDE installed on your system. If not, download and install it from the official [NXP website](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcuxpresso-integrated-development-environment-ide:MCUXpresso-IDE).

2. **Download SDK**: Download the latest [SDK](https://mcuxpresso.nxp.com/en/welcome) version 2.15.0 from the NXP website and install it in MCUXpresso IDE.

3. **Import "hello_world" Example**:
   - Import the "hello_world" example into your MCUXpresso IDE project.
   
4. **Change flash_config.c File**:
   - Navigate to `/rdrw612bga_hello_world/flash_config/flash_config.c`.
   - Replace this file with the updated version of IRIS-W1 provided.

5. **Build the Application**:
   - Build the application within MCUXpresso IDE.

6. **Connect EVK to PC**:
   - Connect your EVK (Evaluation Kit) to your PC using a USB-C cable.

7. **Debugging**:
   - Use debug mode in MCUXpresso IDE to flash the application onto the EVK.
   - It will start at the main function. Use the play button to run the application.

## Flashing WiFi/BT Firmware

When using WiFi/BT applications, you need to flash WiFi/BT Firmware separately from the application .

### Flashing WiFi/BT Firmware

1. **Using J-Link Lite Tool**:
   - Use the J-Link Lite tool to flash the WiFi/BT Firmware.
   - Wi-Fi :- Flash `rw61x_sb_wifi.bin_v1.bin` at address `0x08400000` using J-Link Lite.
   - Bluetooth :- Flash `rw61x_sb_ble_a1.bin`, at address `0x08540000` using J-Link lite.


### Flashing Application Firmware

1. **Flashing the Application**:
   - After flashing the WiFi/BT Firmware, you can flash the application Firmware using the [same method mentioned above (Setup Instruction)](#setupinstructions).
   - Alternatively, pre-built application Firmware can be downloaded from the GitHub EVK section and flashed using J-Link Lite.

### **Pre-setup requirement** for Wi-Fi / BT / 802.15.4 application.

1. **Replacing Flash config file**: *Macronix (8 MB)*
     - Replace **flash_config.c** file located at **SDK_2_15_000_RD-RW612-BGA.zip\boards\rdrw612bga\flash_config\flash_config.c** in SDK
2. **Replacing mflash config file**: *Macronix (8 MB)*
     - Replace **mflash_drv.c** file located at **SDK_2_15_000_RD-RW612-BGA.zip\components\flash\mflash\rdrw612bga\mflash_drv.c** in SDK

### Note

If you encounter any issues or have further questions, please refer to the documentation or contact the support team for assistance.
