# blhost Automation Script (EVK-IRIS-W1)

This Windows batch script helps to recover EVK-IRIS-W1 from an abnormal state, using `blhost.exe`. (**NOTE** : script supports only EVK-IRIS-W1)

## Prerequisites

- Windows operating system
- `blhost.exe` (Ensure you have the executable and its path)
- A compatible device connected to a COM port
- Put IRIS in **ISP boot** mode. (refer EVK-IRIS-USER_GUIDE) (DIP Switch **SW3**)

## Usage

1. Download script:

   ```sh
   git clone https://github.com/u-blox/u-blox-sho-OpenCPU/tree/master/MCUXpresso/IRIS-W1/extra
   ```

2.  **Open Command Prompt** and navigate to the directory containing the script.
   - Press `Win + R`, type `cmd`, and press `Enter`.

2. **Navigate to the Script Directory**:
   - Use the `cd` command to navigate to the directory where `script.bat` is saved.
     ```cmd
     cd path\to\script\directory
     ```
3. **Run the Script**:
   - Type the following command and press `Enter`:
     ```cmd
     IRIS_blhost.bat
     ```

4. **Follow the Prompts**:
   - **Select the Module Variant**:
     - The script will display a menu to choose between Macrionix and Fieldex.
     - Enter `1` for Macrionix or
     - Enter `2` for Fieldex and 
     - press `Enter`.
       
   - **Enter the COM Port Number**:
     - Enter the COMXX port number of the connected EVK (e.g., `COM1`) and press `Enter`.
       
   - **Enter the Path to `blhost.exe`**:
     - Enter the full path to `blhost.exe` (e.g., `C:\path\to\blhost.exe`) and press `Enter`.
       
    ```plaintext
    Enter COM port number (e.g., COM1): COM3
    Enter path to blhost.exe (e.g., C:\path\to\blhost.exe): C:\tools\blhost.exe
    ```
   - **step for FCB_FID .bin file (only required with Fidelex)** :
    
    ```plaintext
    Enter the path to FCB_FID.bin (e.g., C:\path\to\FCB_FID.bin)
    ```
   - **step to flash rw61x_sb_wifi_XX.bin file (Radio Firmware, only required with (Wifi/Bluetooth/802.15.4)) ** :
    
    ```plaintext
    For **rw61x_sb_wifi_a1.bin**: Enter the path to hello_world_F8.bin (e.g., C:\path\to\rw61x_sb_wifi_a1.bin )
    ```
   - **step to flash hello_world.bin file ** :
    
    ```plaintext
    For **Macronix**: Enter the path to hello_world_M8.bin (e.g., C:\path\to\hello_world_M8.bin )
    For **Fidelix**: Enter the path to hello_world_F8.bin (e.g., C:\path\to\hello_world_F8.bin )
    ```

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
     - Radio Firmware (`.bin` path, e.g, rw61x_sb_wifi_aXX.bin) (this is require only with wifi/Bluetooth/802.15.4 FW)
     - Application Firmware ( `.bin` path of application, e.g, hello_world,wifi_cli,. _)

4. **Optional: Reset and Verification**
   - After successful flashing, disconnect USB-IRIS-W1 (as prompted).
   - Refer to the device's user manual for instructions on switching back to QSPI mode and verifying the firmware.

**Troubleshooting**

- **COM Port:** Verify selection in step 3 using Device Manager (Windows) or system settings (other OSes).
- **Flashing Errors:** Refer to `blhost` script documentation or MCUXpresso IDE error messages for troubleshooting.


## Troubleshooting

- Ensure the COM port number is correct and the device is connected.
- Verify the path to `blhost.exe` is correct.
- Check if `blhost.exe` has the necessary permissions to execute.

## Download blhost from NXP
- [blhost](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcu-bootloader-for-nxp-microcontrollers:MCUBOOT?_gl=1*ge4tj9*_ga*MTY1NjE5NjY3Ni4xNzE1MDY1NjE5*_ga_WM5LE0KMSH*MTcxNTA2NTYxOS4xLjEuMTcxNTA2NTYyMC4wLjAuMA..)
