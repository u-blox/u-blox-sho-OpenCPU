# blhost Automation Script

This Windows batch script helps to recover EVK-IRIS-W1 from a abnormal state, using `blhost.exe`.

 

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
   Enter path to Enter path to FCB_FID.bin (e.g., C:\path\to\FCB_FID.bin)
    ```
  


## Troubleshooting

- Ensure the COM port number is correct and the device is connected.
- Verify the path to `blhost.exe` is correct.
- Check if `blhost.exe` has the necessary permissions to execute.

## Download blhost from NXP
- [blhost](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcu-bootloader-for-nxp-microcontrollers:MCUBOOT?_gl=1*ge4tj9*_ga*MTY1NjE5NjY3Ni4xNzE1MDY1NjE5*_ga_WM5LE0KMSH*MTcxNTA2NTYxOS4xLjEuMTcxNTA2NTYyMC4wLjAuMA..)
