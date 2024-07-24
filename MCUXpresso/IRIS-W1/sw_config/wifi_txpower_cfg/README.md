
# Integration of Wi-Fi Tx-Power Limits to Wi-Fi CLI Application

## Steps for Integration

1. **Download Instructions and Required Files**
   - Visit the [NXP website](https://www.nxp.com/webapp/sps/download/license.jsp?colCode=RW61x-Regulatory_Tx_PowerTableUtil.v2p5&appType=file1&DOWNLOAD_ID=null) (login required) to download the instructions and necessary files to integrate custom Tx-Power limits into the SDK.

2. **Create the Header File**
   - Use the provided Excel sheet `RW610_Sample_TX_PowerTable_US.xslx` and follow the instructions from NXP to generate a header file named `wlan_txpwrlimit_cfg_US_rw610.h`.

3. **Modify Configuration in Wi-Fi CLI**
   - In the `app_config.h` file of the Wi-Fi CLI application, change the line:
     ```c
     #define WIFI_BT_TX_PWR_LIMITS "wlan_txpwrlimit_cfg_WW_rw610.h"
     ```
     to:
     ```c
     #define WIFI_BT_TX_PWR_LIMITS "wlan_txpwrlimit_cfg_US_rw610.h"
     ```

By following these steps, you can successfully integrate custom Tx-Power limits into the Wi-Fi CLI application.
