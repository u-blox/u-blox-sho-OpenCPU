# u-blox RF calibration example

This example contains component and example code to configure the NORA-W10X module radio to comply with regulations.

For more information please refer to NORA-W1 series - [System Integration Manual](https://www.u-blox.com/docs/UBX-22005601)

## Current ESP-IDF version
v5.1

### To clone the current version

`git clone https://github.com/u-blox/u-blox-sho-OpenCPU.git`

## Older esp-idf version

### To clone NORA-W1 - esp-idf v4.4 or older

`git clone -b nora_w1_v4.4 https://github.com/u-blox/u-blox-sho-OpenCPU.git u-blox-sho-OpenCPU_nora_w1_v4.4`

## Applying the RF calibration

### esp-idf 5.1.x

Apply the patches found on `patches` folder to the ESP-IDF installation path, for example:

`patch -p2 -i ./NINA-W1-OutputPower/patches/ubx_phy_cal_esp_idf_5_1.patch -d ./v5.1_release/esp-idf/components/`

### esp-idf 4.4.x

Apply the patches found on `patches` folder to the ESP-IDF installation path, for example:

`patch -p2 -i ./NORA-W1-OutputPower/patches/ubx_phy_cal_esp_idf_4_4.patch -d ./v4.4/esp-idf/components/`

### Verifying patches

After patching the esp-idf run the application and look for below print:

`ubx_phy_cal: loading PHY init data from application binary`

f it shows that means the RF calibration with updated values work correctly.

**Note:** Any questons about RF calibration? See [RF calibration section on the Espressif documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/RF_calibration.html#full-calibration)

## Compiling

Set the device target esp32 by running the command bellow:

`idf.py set-target esp32-s3`

Open the project configuration menu:

`idf.py menuconfig`

In the `u-blox OTP and RF calibration Example Configuration` menu:
- Set the Wi-Fi configuration.
    - Set `WiFi SSID`.
    - Set `WiFi Password`.

### Build and Flash

Put the u-blox board on the boot mode:
- Hold the boot button, press the Reset button, and release the Boot button.

Build the project and flash it to the board, then run the monitor tool to view the serial output. To do that, open a terminal console and run the command below:

`idf.py -p PORT flash monitor`

**Note:** Replace the parameter PORT for the device COM port connect to the computer.

(To exit the serial monitor, type `Ctrl-]`.)