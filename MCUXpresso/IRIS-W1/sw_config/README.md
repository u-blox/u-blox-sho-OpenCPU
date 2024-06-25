## software configuration 

This folder contains essential software configuration and calibration files for IRIS-W1 module

## Folder Structure

```shell
├── bt_Calibration  
├── flash_config
│   ├── Fidelex_8MB
│   └── Macronix_8MB
├── README.md
└── wifi_Calibration
````

### bt_Calibration

This directory (**bt_Calibration**) contains custom calibration data specifically tailored for IRIS-W1 modules to ensure proper toggling of the RF CTRL switch. The default settings in the NXP SDK may not correctly manage this functionality. this is important configuation file when we use BT/Wi-Fi applications.

### flash_config: 

IRIS-W1 has build with differnt vendor of flash memroy (Fidelex,Macronix) . This directory holds configuration files for flash memory. It includes subdirectories for different flash memory types.

**Fidelex_8MB:** Configuration files specific to the Fidelex 8MB flash memory.
**Macronix_8MB:** Configuration files specific to the Macronix 8MB flash memory.

**NOTE** : if you're unable indentify the flash memory vendor, please contact to u-blox support team.

### wifi_Calibration

This directory (**wifi_Calibration**) contains calibration data specifically for IRIS-W1 modules.
 
