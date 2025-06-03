# IRIS-W1 Calibration Data Loading Using Labtool

This guide explains how to load the calibration data onto the manufacturing firmware using the Labtool for the **IRIS-W1** module.

## Prerequisites

- Ensure you have the Labtool package:
  `MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x`
- Locate the `labtool` folder inside the package i.e, at `MFG-RW61X-MF-BRG-U16-WIN-X86-x.x.x.xx.x-xx.xx.x/labtool`.

## Step 1: Copy Calibration Text Files

Copy the following calibration data files ([Single_antenna_calibration_data_text_files](/MCUXpresso/IRIS-W1/sw_config/labtool/Single_antenna_calibration_data_text_files/)) for the **single antenna configuration** (specific to u-blox module) into the `labtool` folder:

- [Cal15_4DataFile.txt](/MCUXpresso/IRIS-W1/sw_config/labtool/Single_antenna_calibration_data_text_files/Cal15_4DataFile.txt)
- [CalBtDataFile.txt](/MCUXpresso/IRIS-W1/sw_config/labtool/Single_antenna_calibration_data_text_files/CalBtDataFile.txt)
- [CalWlanDataFile.txt](/MCUXpresso/IRIS-W1/sw_config/labtool/Single_antenna_calibration_data_text_files/CalWlanDataFile.txt)
- [PwrTble_Otp_Path0.txt](/MCUXpresso/IRIS-W1/sw_config/labtool/Single_antenna_calibration_data_text_files/PwrTble_Otp_Path0.txt)

## Step 2: Generate Configuration Files

1. Launch the Labtool.
2. In the Labtool interface, select **`Wi-Fi Tool`** by entering option **`1`**.
3. To check the firmware version, enter option **`88`**. Ensure that a valid firmware version is returned without any error codes. If errors occur, try re-flashing the firmware or power cycling the module.
4. Enter option **`53`** in the Labtool interface.
5. This command will generate and store the following `.conf` files in the `labtool` directory:
   - `15p4CalData_ext.conf`
   - `BtCalData_ext.conf`
   - `BtCalData_ext1.conf`
   - `WlanCalData_ext.conf`

> **Note**: Once generated, these configuration files remain valid and do not need to be regenerated unless the calibration data changes.

## Step 3: Load Configuration into IRIS-W1

1. Enter option **`22`** in the Labtool interface.
2. This will load the generated configuration and calibration data into the **IRIS-W1** module.

> ⚠️ The configuration and calibration data are **volatile**.
> They must be **reloaded** using option `22` **after each power cycle or reset**.

## Additional Resources

For detailed instructions on using the Labtool and operating the IRIS-W1 radio, refer to the official documentation:

- **UM11801 - Labtool User Manual** at [RW612 Product Page](https://www.nxp.com/products/wireless-connectivity/wi-fi-plus-bluetooth-plus-802-15-4/wireless-mcu-with-integrated-tri-radio-1x1-wi-fi-6-plus-bluetooth-low-energy-5-4-802-15-4:RW612).
