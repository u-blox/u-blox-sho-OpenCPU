# u-blox OTP component and RF calibration example

This example contains components and example code to access the OTP in all u-blox NINA-W10X openCPU modules and code to configure the ESP32 radio to comply with regulation for the NINA-W10X modules. The OTP is part of the flash chip and cointains information written in module production. 

For more information please refer to NINA-W1 series - [System Integration Manual](https://www.u-blox.com/docs/UBX-17005730)

- RF_FREQ_CALIBRATION - Measured in our production, individual for all modules. 
- 4 u-blox MAC addresses: WiFI Station, WiFi AP, Ethernet and Bluetooth.
- UUID - Unique ID for the unit.
- SERIAL - Serial number of the module.
- TYPE_CODE - The module type code as seen on the module lable.

The application shows example code to read out above values from the flash OTP, it also starts WiFi station to show how to apply RF calibration using u-blox calibration values to comply with regulations.

## Current ESP-IDF version
v5.1

### To clone the current version

`git clone https://github.com/u-blox/u-blox-sho-OpenCPU.git`

## Older esp-idf version

### To clone NINA-W1 - esp-idf v4.4 or older

`git clone -b nina_w1_v4.4 https://github.com/u-blox/u-blox-sho-OpenCPU.git u-blox-sho-OpenCPU_nina_w1_v4.4`

## Applying the RF calibration

### esp-idf 5.1.x

Apply the patches found on `patches` folder to the ESP-IDF installation path, for example:

`patch -p2 -i ./NINA-W1-OutputPower/patches/ubx_phy_cal_esp_idf_5_1.patch -d ./v5.1_release/esp-idf/components/`

### esp-idf 4.0.x, 4.3.x and 4.4.x

Apply the patches found on `patches` folder to the ESP-IDF installation path, for example:

`patch -p2 -i ./otp-component-example-esp/patches/ubx_phy_cal_esp_idf_4_4.patch -d ./v4.4_release/esp-idf/components/`

### Verifying patches

After patching the esp-idf run the application and look for below print:

`W (362) ubx_phy_cal: rf freq calibration enabled, value_otp = -1(ppm), value_set = 0(8kHz)`

f it shows that means the RF calibration with updated values work correctly.

**Note:** Any questons about RF calibration? See [RF calibration section on the Espressif documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/RF_calibration.html#full-calibration)

## Compiling

Set the device target esp32 by running the command bellow:

`idf.py set-target esp32`

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