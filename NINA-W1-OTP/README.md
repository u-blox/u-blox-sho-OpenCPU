# u-blox OTP component and RF calibration example

This example contains components and example code to access the OTP in all u-blox NINA-W10X openCPU modules and code to configure the ESP32 radio to comply with regulation for the NINA-W10X modules. The OTP is part of the flash chip and cointains information written in module production. 

For more information please refer to NINA-W1 series - [System Integration Manual](https://www.u-blox.com/docs/UBX-17005730)

- RF_FREQ_CALIBRATION - Measured in our production, individual for all modules. 
- 4 u-blox MAC addresses: WiFI Station, WiFi AP, Ethernet and Bluetooth.
- UUID - Unique ID for the unit.
- SERIAL - Serial number of the module.
- TYPE_CODE - The module type code as seen on the module lable.

The application shows example code to read out above values from the flash OTP, it also starts WiFi station to show how to apply RF calibration using u-blox calibration values to comply with regulations.

## Applying the RF calibration

### esp-idf 4.0.x and 4.3.x

Apply the patches found on `patches` folder to the ESP-IDF installation path, for example:

`patch -p2 -i ./otp-component-example-esp/patches/ubx_phy_cal_esp_idf_4_3.patch -d ./v4.3_release/esp-idf/components/`

### Verifying patches

After patching the esp-idf run the application and look for below print:

`W (362) ubx_phy_cal: rf freq calibration enabled, value_otp = -1(ppm), value_set = 0(8kHz)`

If it shows that means the RF calibration with updated values work correctly.

## Compiling

### CMake

```
idf.py menuconfig # Select the WiFi SSID and PW
idf.py build
idf.py -p COMx flash monitor
```