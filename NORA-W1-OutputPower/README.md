# u-blox RF calibration example

This example contains component and example code to configure the NORA-W10X module radio to comply with regulations.

For more information please refer to NORA-W1 series - [System Integration Manual](https://www.u-blox.com/docs/UBX-22005601)

## Applying the RF calibration

### esp-idf 4.4.x

Apply the patches found on `patches` folder to the ESP-IDF installation path, for example:

`patch -p2 -i ./NORA-W1-OutputPower/patches/ubx_phy_cal_esp_idf_4_4.patch -d ./v4.4.3/esp-idf/components/`

### Verifying patches

After patching the esp-idf run the application and look for below print:

`ubx_phy_cal: loading PHY init data from application binary`

If it shows that means the RF calibration with updated values work correctly.

## Compiling

### CMake

```
idf.py menuconfig # Select the WiFi SSID and PW
idf.py build
idf.py -p COMx flash monitor
```