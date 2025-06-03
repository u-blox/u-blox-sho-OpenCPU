# 📡 Integration of Wi-Fi Tx-Power Limits for Wi-Fi Applications

This document outlines the steps required to integrate u-blox-specific Wi-Fi transmit power limits into your Wi-Fi application using the NXP SDK.

## 📁 Integration Steps

Follow these steps to update and apply region-specific Tx-power configurations:

1. Navigate to the folder:
   `SDK/components/wifi_bt_module/AzureWave/tx_pwr_limits/`

2. Replace the default power table file: `wlan_txpwrlimit_cfg_WW_rw610.h` with the **u-blox-specific** version i.e, available at: [wlan_txpwrlimit_cfg_WW_rw610.h](/MCUXpresso/IRIS-W1/sw_config/wifi_txpower_cfg/wlan_txpwrlimit_cfg_WW_rw610.h), that complies with your target region’s regulatory standards.

3. Ensure this update is completed **before building** your Wi-Fi application.

4. Compile and flash the updated Wi-Fi application onto the module.

5. Select the appropriate country/region code to activate the corresponding certified power table.
   For example, in the Wi-Fi CLI application:
   - Set the region code using:
     <details>
     <summary><b><code>wlan-set-regioncode</code></b></summary>

     <p style="color: grey;">

     <b>Usage:</b><br>
     <code>wlan-set-regioncode &lt;region-code&gt;</code><br><br>

     <b>where, region code =</b><br>
     <code>0x00</code> : World Wide Safe Mode<br>
     <code>0x10</code> : US FCC, Singapore<br>
     <code>0x30</code> : ETSI, Australia, Republic of Korea<br>
     <code>0xFF</code> : Japan<br>

     </p>
     </details>
   - View the configured region code using:
     ```
     wlan-get-regioncode
     ```
   - View the configured power limits per channel using:
     ```
     wlan-get-txpwrlimit <subband>
     ```

## 🌐 Supported Regions

The u-blox-specific power table currently includes certified configurations for:
- FCC (United States)
- ETSI (Europe)
- Japan (JP)
- World Wide (WW)

Additional countries will be added as their certifications are completed.

## 🛠 Troubleshooting

If you experience issues or have questions:
- Refer to the official SDK documentation.
- Contact the u-blox support team for further assistance.
