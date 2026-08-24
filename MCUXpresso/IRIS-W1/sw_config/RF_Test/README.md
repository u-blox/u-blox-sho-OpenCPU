# IRIS-W1 RF Test Applications

This guide describes the recommended Radio test & verification of IRIS-W1 modules. use the standard NXP SDK examples and shell applications listed below.

## Recommendation at a glance

| Radio | Recommended application | Main purpose |
|---|---|---|
| Wi-Fi | `wifi_test_mode` | Wi-Fi RF tests |
| Bluetooth Low Energy | `EdgeFast BLE shell application` | BLE RF tests |
| 802.15.4 | `ot_cli` | OpenThread CLI and NXP vendor RF test commands |


## What each application is for

### Wi-Fi: `wifi_test_mode`

Use the RW612 SDK `wifi_test_mode` example for Wi-Fi RF verification. This is the recommended choice when the manufacturing (MFG) environment is not required.

The RF test mode is expected to provide the following Wi-Fi RF test capabilities:

- Band, channel, and bandwidth selection
- Data rate and MCS selection
- Transmit power configuration
- Continuous-wave (CW) and modulated transmission
- Receive sensitivity, packet error rate (PER), and RSSI measurements
- 802.11ax high-efficiency (HE) testing

Refer to section 4.9.1 of the NXP manual [Wi-Fi and Bluetooth Demo Applications for RW61x (UM11799)](https://www.nxp.com/docs/en/user-manual/UM11799.pdf) for the supported commands and test procedure.

For Wi-Fi MAC-address retrieval, the existing [read_MAC_address example](../../example_code/read_MAC_address/main.c) can be used with the Wi-Fi test-mode APIs.

### Bluetooth Low Energy: EdgeFast BLE shell

Use the EdgeFast BLE shell application for BLE RF testing. It supports BLE transmit and receive tests, including:

- Transmit power
- Packet and payload configuration
- Packet error or receive measurements

Refer to section 6.11.1.2 of [UM11799](https://www.nxp.com/docs/en/user-manual/UM11799.pdf) for the BLE RF test commands and procedure.

### 802.15.4: `ot_cli`

Use the NXP SDK `ot_cli` application for 802.15.4 RF testing. The application exposes NXP vendor commands for RF test mode.

Refer to section 3.1.5.2 of [OpenThread Border Router and CLI Demo Applications for RW61x (UM11861)](https://www.nxp.com/docs/en/user-manual/UM11861.pdf) for the vendor commands and test procedure.

## Suggested workflow

1. Identify the module's RW610 or RW612 chipset variant and flash vendor.
2. Select the matching IRIS-W1 flash configuration, flash driver, and linker script from the neighbouring `sw_config` folders.
3. Import the corresponding NXP SDK example into MCUXpresso IDE.
4. Apply the IRIS-W1 board, flash, and wireless calibration files described in the [IRIS-W1 setup guide](../../EVK-IRIS-W1/README.md).
5. Build and flash the application using the EVK's onboard debugger or an external debugger for the USB board.
6. Flash the required Wi-Fi or Bluetooth controller firmware at the addresses documented in the [EVK-IRIS-W1 setup guide](../../EVK-IRIS-W1/README.md).
7. Connect a UART console, run the radio-specific RF commands from the NXP manual, and record tester results such as output power, sensitivity, PER, and RSSI.

## Calibration versus RF verification

NXP support distinguishes routine RF verification from RF calibration:

- Use `wifi_test_mode`, the EdgeFast BLE shell, or `ot_cli` for RF verification and functional measurements.
- The NXP MFG environment remains necessary when performing RF calibration.


## Note

> **NXP note:** Labtool is mainly used by the manufacturing / calibration process. It is not the standard path for routine RF verification. For normal RF testing, use the NXP RF test applications listed in the [RF_Test guide](/MCUXpresso/IRIS-W1/sw_config/RF_Test/README.md).

