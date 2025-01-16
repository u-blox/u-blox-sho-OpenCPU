# Steps to Run the ot-cli Application on the u-blox Module (802.15.4 Applications)

This guide outlines the steps to compile and run the `ot-cli` application on the u-blox module.

## 1. Check the Memory Type

Identify the memory type on your board. Options include:

- **Fidelex**
- **Macronix**

The memory type determines the required binaries for later steps.

## 2. Compile the ot-cli Application

### 2.1. Clone the Repository

Run the following commands to obtain the source code:

```bash
git clone https://github.com/NXP/ot-nxp.git -b v1.4.0-pvw1
cd ot-nxp
git submodule update --init
./script/bootstrap
```

Refer to the [NXP/ot-nxp GitHub Repository](https://github.com/NXP/ot-nxp/blob/release/v1.4.0/src/rw/rw612/README.md) for more information.

### 2.2. Initialize and Update the SDK

Navigate to the SDK path and execute:

```bash
cd <path-to-ot-nxp>/third_party/github_sdk/
west init -l manifest --mf west.yml
west update
cd <path-to-ot-nxp>
git submodule update --init
```

### 2.3. Update Flash Configuration Files

Replace the following files with u-blox-specific versions:

- **flash_config.c**:  
  Location: `ot-nxp/boards/rw612/rw612_rd/`

Refer to this updated files.[this folder](../flash_config/)

- **mflash_drv.c**:  
  Location: `ot-nxp/third_party/github_sdk/core/components/flash/mflash/rdrw612bga/`

Refer to this updated files.[this folder](../flash_drv/)

### 2.4. Update Calibration Files

Replace the following files with u-blox-specific versions:

- **fwk_config.h**:  
  Location: `ot-nxp/third_party/github_sdk/middleware/wireless/framework/platform/rw61x/configs/`

- **fwk_platform_ble.c**:  
  Location: `ot-nxp/third_party/github_sdk/middleware/wireless/framework/platform/rw61x/`

Refer to this updated files.[SDK_2_16_100](../BT_802_15_4_Calibration_Files/SDK_2_16_100/), [SDK_2_16_000](../BT_802_15_4_Calibration_Files/SDK_2_16_000/)

### 2.5. Build the Application

Build the `ot-cli` application:

```bash
./script/build_rw612 ot_cli
```

### 2.6. Flash the Binaries

Flash the compiled binaries to the module:

- **ot_cli binary**: Address `0x08000400`  
- **Combo firmware**: Address `0x085e0000`

---

## 3. Set Annex Parameters

To develop a custom 802.15.4 radio application, it is essential to ensure that the calibration and EUI64 values are configured in accordance with the specifications of the IRIS modules.

This procedure prepares and deploys the `ot-cli` application on a u-blox module by configuring memory, updating files, and applying calibration setting.

### 3.1. Use Annex 100 for Calibration & Configure Annex 104 Parameters

Update the radio calibration settings for the u-blox module.

Example `ot-cli` commands:

- **Set EUI64 (MAC Address):**

```bash
radio_nxp seteui64 0xAA001122334455BB
```

- **Set TX Power Limit:**

```bash
radio_nxp txpwrlimit 15
```

