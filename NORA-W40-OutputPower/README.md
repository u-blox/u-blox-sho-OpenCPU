# u-blox RF calibration example

This example contains component and example code to configure the NORA-W40X module radio to comply with regulations.

For more information please refer to NORA-W40 series - [System Integration Manual](https://content.u-blox.com/sites/default/files/documents/NORA-W40_SIM_UBXDOC-465451970-3233.pdf)

## Current ESP-IDF version
v5.1

ESP32-C6 support was added in ESP-IDF v5.1, so NORA-W40 cannot be built with an older release.

### To clone the current version

`git clone https://github.com/u-blox/u-blox-sho-OpenCPU.git`

## Applying the RF calibration

### Using the Getting Started SDK

The calibration is applied for you, including a backup and a revert path:

`./ubx-sdk.sh nora-w4 --variant NORA-W401 --rf-config`

See `GettingStartedSDK/modules/README.md` for details.

### Manually, esp-idf 5.1.x

Apply the patches found on `patches` folder to the ESP-IDF installation path, for example:

`patch -p2 -i ./NORA-W40-OutputPower/patches/ubx_phy_cal_esp_idf_5_1.patch -d ./v5.1_release/esp-idf/components/`

### Verifying patches

After patching the esp-idf run the application and look for below print:

`ubx_phy_cal: loading PHY init data from application binary`

If it shows, the RF calibration with updated values works correctly.

**Note:** Any questions about RF calibration? See [RF calibration section on the Espressif documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/RF_calibration.html#full-calibration)

## Compiling

Set the device target by running the command below:

`idf.py set-target esp32c6`

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

**Note:** Replace PORT with the COM port the device is connected to.

(To exit the serial monitor, type `Ctrl-]`.)