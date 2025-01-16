# Recovery script & blhost (EVK-IRIS-W1)

This Windows batch script helps to recover EVK-IRIS-W1 from an abnormal state, using `blhost.exe`.

## Prerequisites

- Windows operating system
- `blhost.exe` (Ensure you have the executable and its path)
- A compatible device connected to a COM port
- Put IRIS in **ISP boot** mode. (refer EVK-IRIS-USER_GUIDE) (DIP Switch **SW3**)
- Connect EVK-IRIS to PC (USB-3 , same as MCU-Link Pro port)

## Usage

1. Download script:

   ```sh
   git clone https://github.com/u-blox/u-blox-sho-OpenCPU/tree/master/MCUXpresso/IRIS-W1/recovery_tool/blhost
   ```

2.  **Open Command Prompt** and navigate to the directory containing the script.
   - Press `Win + R`, type `cmd`, and press `Enter`.

2. **Navigate to the Script Directory**:
     
     ```cmd
     cd path\to\script\directory
     ```
3. **Run the Script**:
     
     ```cmd
     IRIS_blhost.bat
     ```

4. **Follow the Prompts**:
   - **Select the Module Variant**:
     - The script will display a menu to choose between Macrionix and Fieldex.
     ```plaintext
     - Enter `1` for Macrionix or
     - Enter `2` for Fieldex and 
     - press `Enter`.
     ```
       
   - **Enter the COM Port Number**:
     - Enter the COMXX port number of the connected EVK (e.g., `COM1`) and press `Enter`.

    ```plaintext
       Enter COM port number (e.g., COM1): COM3
    ```   

   - **Enter the Path to `blhost.exe`**:
     - Enter the full path to `blhost.exe` (e.g., `C:\path\to\blhost.exe`) and press `Enter`.
       
    ```plaintext
    Enter path to blhost.exe (e.g., C:\path\to\blhost.exe): C:\tools\blhost.exe 
    ```

   - **Enter the Path of .bin file**:
	FCB_FID.bin (**this step is only for Fidelix** ,  [FCB_FID.bin](recovery_bin/Fidelix/) )
    ```plaintext
    Enter path to FCB_FID.bin (**this step is only for Fidelix** ,  [FCB_FID.bin](recovery_bin/Fidelix/) )
    ```
 
   - **Enter the Path of Application .bin file**:
    For **Macronix**: Enter the path to hello_world.bin (e.g., C:\path\to\hello_world.bin  [hello_world.bin](recovery_bin/Macronix_8MB) )
    For **Fidelix**: Enter the path to hello_world.bin (e.g., C:\path\to\hello_world.bin [hello_world.bin](recovery_bin/Fidelix) )
    
    ```plaintext
    Enter path to application .bin ( e.g hello_world.bin [hello_world.bin](recovery_tool\) )    
    ```    
5. **Reset and Verification**
   - After successful flashing, disconnect EVK-IRIS-W1 
   - switching back to QSPI mode and verifying the firmware. (check the logs on the UART console. If they see some prints of hello_world messages on the console, then we can say that the recovery step is successful and the module gonna work as expected after recovery process.)
    
# blhost Automation Script for flashing **(USB-IRIS-W1)**

This guide outlines using the `blhost` script to flash firmware onto a USB-IRIS-W1.

**Requirements**

- USB-IRIS-W1 board
- MCUXpresso IDE (latest version recommended)
- `IRIS_blhost.bat` script

**Steps**

1. **Hardware Setup**
   - Connect USB-IRIS-W1 (ISP mode) via USB. (check USB-IRIS-W1 USerGuide for DIP Switch setting)

2. **Firmware Conversion**
   - Build your firmware application.
   - Use MCUXpresso IDE's Binary Utilities (consult IDE docs for specific steps) to convert the generated `.hex` file to a `.bin` file.

3. **Flashing Process**
   - Run `IRIS_blhost.bat`.
   - Follow on-screen prompts to select:
     - Flash Memory (e.g., Macrionix , Fieldex )
     - COM Port (connected to USB-IRIS-W1)
     - blhost Application Location (`.exe` file path)
     - Application Firmware ( `.bin` path of application, e.g, hello_world,wifi_cli,. _)

4. **Reset**
   - After successful flashing, disconnect USB-IRIS-W1 (as prompted).
   - Refer to the device's user manual for instructions on switching back to QSPI mode and verifying the firmware. (check the logs on the UART console. If they see some prints of hello_world messages on the console, then we can say that the recovery step is successful and the module gonna work as expected after recovery process.)

**Troubleshooting**

- **COM Port:** Verify selection in step 3 using Device Manager (Windows) or system settings 
- **Flashing Errors:** Refer to `blhost` script documentation or MCUXpresso IDE error messages for troubleshooting.


## Troubleshooting

- Ensure the COM port number is correct and the device is connected.
- Verify the path to `blhost.exe` is correct.
- Check if `blhost.exe` has the necessary permissions to execute.

## Download blhost from NXP
- [blhost](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcu-bootloader-for-nxp-microcontrollers:MCUBOOT?_gl=1*ge4tj9*_ga*MTY1NjE5NjY3Ni4xNzE1MDY1NjE5*_ga_WM5LE0KMSH*MTcxNTA2NTYxOS4xLjEuMTcxNTA2NTYyMC4wLjAuMA..)
