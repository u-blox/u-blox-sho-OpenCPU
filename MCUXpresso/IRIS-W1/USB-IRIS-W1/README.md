# USB-IRIS-W1

This README provides instructions for setting up and running the application using MCUXpresso IDE with the latest SDK.

## Required Tools

**Install MCUXpresso IDE**: Ensure that MCUXpresso IDE is installed on your system. If not, download and install it from the official [NXP website](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcuxpresso-integrated-development-environment-ide:MCUXpresso-IDE).

**Download SDK**: Download the latest [SDK](https://mcuxpresso.nxp.com/en/welcome) (current version: 2.15.0) from the NXP website and install it in MCUXpresso IDE.

**J-Link Tool**: Download the J-Link tool from Segger [here](https://www.segger.com/downloads/jlink/).

## Instructions for Building and Flashing the Application on USB-IRIS-W1

1. **Example Project**:
   - Import the example (hello_world/FreeRTOS/wifi_cli) into your MCUXpresso IDE project.
   
2. **Update Pre-Setup Requirements**:
   - Check [this section](#pre-setup-requirement) to set up flash configuration.

3. **Build the Application**:
   - Follow the standard build procedure in MCUXpresso IDE.

4. **Plug the USB-IRIS-W1 into PC**: (Make sure about the boot mode, should be in QSPI mode) 

5. **Debugging**:
   - Use debug mode in MCUXpresso IDE to flash the application onto the EVK.
   - The application will start at the main function. Use the play button to run the application.

## Flashing Firmware

When using WiFi/BT applications, you need to flash the WiFi/BT Firmware separately from the application.

### Flashing WiFi/BT Firmware

**Using J-Link Lite Tool**:

   - Use the J-Link Lite tool to flash the WiFi/BT Firmware.
   - **WiFi**: Flash `rw61x_sb_wifi.bin_v1.bin` at address `0x08400000` using J-Link Lite.
   - **Bluetooth**: Flash `rw61x_sb_ble_a1.bin` at address `0x08540000` using J-Link Lite.

   you can find the latest Radio application Firmware in the SDK as well    
   
   ```sh
            ex. Wi-Fi Firmware location path ->  \rdrw612bga_wifi_cli\component\conn_fwloader\fw_bin
   ```

**NOTE:** The WiFi/BT Firmware version depends on the chipset variant. Please use the appropriate version (e.g., a1 chipset -> XXXXXX_a1.bin).
    
   ```sh
Use j-link commander to identify the chipset variant, follow the  setups

J-Link> con
Device> RW610
TIF>S
Speed><Enter>
CHIP_INFO @0x4500_1114 > **mem32 45001114 1**

Below is the hexadecimal representation of the chipset variant.
A0 : 0x7000
A1 : 0x7001
A2 : 0x7002

   ```



### Flashing Application Firmware

1. **Flashing the Application**:
   - After flashing the WiFi/BT Firmware, you can flash the application Firmware using the [same method mentioned above](#instructions-for-building-and-flashing-the-application-on-evk-iris-w1).
   - Alternatively, pre-built application Firmware can be downloaded from GitHub and flashed using J-Link Lite.

## Pre-Setup Requirement

Use the **flash_config.c** file from [this location](IRIS-W1/sw_config) as per the density and vendor preset on IRIS-W1 EVK.

1. **Replacing Flash Config File**:
     - Replace the **flash_config.c** file located at **SDK_2_xx_xxx_RD-RW612-BGA.zip\boards\rdrw612bga\flash_config\flash_config.c** in the SDK.
2. **Replacing MFlash Config File**: 
     - Replace the **mflash_drv.c** file located at **SDK_2_xx_xxx_RD-RW612-BGA.zip\components\flash\mflash\rdrw612bga\mflash_drv.c** in the SDK.

## Recovery of IRIS-W1

If you face any issues with IRIS-W1 and can't perform any operations, it might be in an unknown state. Use the blhost application to reset it. Find more information on [this page](IRIS-W1/tools/blhost/README.md).

## Note

If you encounter any issues or have further questions, please refer to the documentation or contact the support team for assistance.


