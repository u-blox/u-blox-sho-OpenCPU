# Device Identifiers Retrieval Guide

This document outlines the procedures to retrieve key device identifiers such as the Serial Number, Module Type, and Wi-Fi MAC Address from an RW612-based IRIS module.

---

## Table of Contents

1. [Overview](#overview)
2. [Retrieving Type Number and Serial Number](#retrieving-type-number-and-serial-number)
   - [Steps](#steps-to-read-type-and-serial-number)
   - [Demo Output](#demo-output-for-type-and-serial-number)
3. [Retrieving Wi-Fi STA MAC Address](#retrieving-wi-fi-sta-mac-address)
   - [Method 1: Custom Demo Application](#method-1-custom-demo-application)
   - [Method 2: Using Existing Wi-Fi Test Mode Application](#method-2-using-existing-wi-fi-test-mode-application)
   - [Demo Output](#demo-output-for-mac-address)
4. [Precompiled Binaries](#precompiled-binaries)
5. [References](#references)

---

## Overview

When developing applications that require hardware-level information, you may need access to the following identifiers:

- **Serial Number**
- **Module Type Number**
- **Wi-Fi STA MAC Address**

This guide explains how to retrieve these identifiers using ROM API, Wi-Fi Test Mode APIs, and SDK example applications.

---

## Retrieving Type Number and Serial Number

These values are stored in E-Fuse and are programmed during module production:

- **Type Number**: Read from E-Fuse IDs 305–312
- **Serial Number**: Read from E-Fuse IDs 313–316

### Steps to Read Type and Serial Number

1. Navigate to:
   ```
   SDK/boards/rdrw612bga/driver_examples/romapi/otp/main.c
   ```
2. Replace existing content with [read_OTP_parameters](/MCUXpresso/IRIS-W1/example_code/read_OTP_parameters/main.c).
3. Compile the application.
4. Flash it onto the module.
5. Press the reset button.
6. The Serial Number and Type Number will be displayed on the UART Serial Console.

### Demo Output for Type and Serial Number

![Type and Serial Number Demo](/MCUXpresso/IRIS-W1/images/serial_type.png)

---

## Retrieving Wi-Fi STA MAC Address

You can retrieve the Wi-Fi MAC address using two different methods.

### Method 1: Custom Demo Application

1. Navigate to:
   ```
   SDK/boards/rdrw612bga/wifi_examples/wifi_test_mode/main.c
   ```
2. Replace with code from [read_MAC_address](/MCUXpresso/IRIS-W1/example_code/read_MAC_address/main.c).
3. Compile the application.
4. Flash the compiled binary along with:
   - `rw61x_sb_wifi_a2.bin` at address `0x08400000`
5. Press the reset button.
6. The Wi-Fi STA MAC Address will appear on the UART Serial Console.

> **Note:** The **API calls** used to retrieve **Wi-Fi STA MAC** Address are as follows:

1. Initialize the Wi-Fi driver and enable test mode:
   ```c
   wlan_init(wlan_fw_bin, wlan_fw_bin_len);
   wlan_set_rf_test_mode();
   ```
2. Retrieve the MAC address using:
   ```c
   wlan_get_rf_otp_mac_addr();
   ```

### Method 2: Using Existing Wi-Fi Test Mode Application

1. Navigate to:
   ```
   SDK/boards/rdrw612bga/wifi_examples/wifi_test_mode
   ```
2. Compile the test mode application.
3. Flash it along with `rw61x_sb_wifi_a2.bin` at address `0x08400000`.
4. Press the reset button and open the UART console.
5. Enter the following commands:
   ```
   wlan-set-rf-test-mode
   wlan-get-rf-otp-mac-addr
   ```
6. The MAC address will be printed to the console.

### Demo Output for MAC Address

![MAC Address Demo](/MCUXpresso/IRIS-W1/images/macdata.png)

---

## Precompiled Binaries

Use the following precompiled binaries for quick testing without developing custom applications:

- **Type & Serial Number**:
  [read_OTP](/MCUXpresso/IRIS-W1/compiled_binaries/Fidelex_8MB/read_OTP/)
- **Wi-Fi MAC Address**:
  [read_MAC](/MCUXpresso/IRIS-W1/compiled_binaries/Fidelex_8MB/read_MAC/)

> **Note:** These binaries are only compatible with **Fidelex memory boards**.

---

## References

- UM11799: *NXP Wi-Fi and Bluetooth Demo Applications for RW61x*, Located at [RW612 Product Page](https://www.nxp.com/products/wireless-connectivity/wi-fi-plus-bluetooth-plus-802-15-4/wireless-mcu-with-integrated-tri-radio-1x1-wi-fi-6-plus-bluetooth-low-energy-5-4-802-15-4:RW612)

