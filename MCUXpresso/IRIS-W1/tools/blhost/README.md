# blhost Automation Script

This Windows batch script helps to recover EVK-IRIS-W1 from a abnormal state, using `blhost.exe`. 

## Prerequisites

- Windows operating system
- `blhost.exe` (Ensure you have the executable and its path)
- A compatible device connected to a COM port
- Put IRIS in ISP boot mode. (refer EVK-IRIS-USER_GUIDE)

## Usage

1. Download script:

   ```sh
   git clone https://github.com/u-blox/u-blox-sho-OpenCPU/tree/master/MCUXpresso/IRIS-W1/extra
   ```

2. Open a command prompt and navigate to the directory containing the script.

3. Run the script:

   ```sh
   script.bat
   ```

4. When prompted, enter the COM port number and the path to `blhost.exe`.

   ```plaintext
   Enter COM port number (e.g., COM1): COM3
   Enter path to blhost.exe (e.g., C:\path\to\blhost.exe): C:\tools\blhost.exe
   ```


## Troubleshooting

- Ensure the COM port number is correct and the device is connected.
- Verify the path to `blhost.exe` is correct.
- Check if `blhost.exe` has the necessary permissions to execute.

## Download blhost from NXP
- [blhost](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcu-bootloader-for-nxp-microcontrollers:MCUBOOT?_gl=1*ge4tj9*_ga*MTY1NjE5NjY3Ni4xNzE1MDY1NjE5*_ga_WM5LE0KMSH*MTcxNTA2NTYxOS4xLjEuMTcxNTA2NTYyMC4wLjAuMA..)
