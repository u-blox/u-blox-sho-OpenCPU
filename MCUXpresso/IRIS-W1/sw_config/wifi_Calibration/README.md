# Wi-Fi Calibration Data

This repository provides Wi-Fi calibration data files for different SDK versions of the RW612 chipset. Follow the instructions below to replace the necessary files in your SDK.

## SDK Versions 2.16.100 and Below

For SDK versions **2_16_100 and earlier**, replace the existing calibration file **wifi_cal_data_ext.h** located at:
SDK_2_xx_xxx_RD-RW612-BGA.zip\middleware\wifi_nxp\incl with the updated file available at: [wifi_cal_data_ext.h](/MCUXpresso/IRIS-W1/sw_config/wifi_Calibration/2_16_100/wifi_cal_data_ext.h).

## SDK Versions 24.12.00 and 25.03.00

**Step 1:**
For SDK versions **24_12_00 and 25.03.00**, replace the file **wifi_cal_data_rw61x_1ant.h** located at:
SDK_2x_xx_xxx_RD-RW612-BGA.zip\middleware\wifi_nxp\incl with the updated file available at: [wifi_cal_data_rw61x_1ant.h](/MCUXpresso/IRIS-W1/sw_config/wifi_Calibration/24_12_00/wifi_cal_data_rw61x_1ant.h).

**Step 2:**
To enable single-antenna WLAN calibration, define the **CONFIG_WLAN_CALDATA_1ANT** macro in the **wifi_config.h** file. For example, in the Wi-Fi CLI application, add this macro to SDK/boards/rdrw612bga/wifi_examples/wifi_cli/wifi_config.h file.

```c
#define CONFIG_WLAN_CALDATA_1ANT 1
```

## SDK Versions 25.06.00 and above

**Step 1:**
For SDK versions **25.06.00 and later**, replace the file **wifi_cal_data_override.h** located at:
SDK_2x_xx_xxx_RD-RW612-BGA.zip\middleware\wifi_nxp\incl with the updated file available at: [wifi_cal_data_override.h](/MCUXpresso/IRIS-W1/sw_config/wifi_Calibration/25_06_00/wifi_cal_data_override.h).

**Step 2:**
To override the default calibration data with the u-blox module’s single-antenna WLAN calibration, define the **OVERRIDE_CALIBRATION_DATA** macro in the **wifi_config.h** file. For example, in the Wi-Fi CLI application, add this macro to SDK/boards/rdrw612bga/wifi_examples/wifi_cli/wifi_config.h file.

```c
#define OVERRIDE_CALIBRATION_DATA "wifi_cal_data_override.h"
```

---

If you encounter any issues, please refer to the SDK documentation or reach out for support.