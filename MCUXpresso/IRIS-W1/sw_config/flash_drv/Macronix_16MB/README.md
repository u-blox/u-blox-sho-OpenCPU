# Flash driver

This repository provides MFlash driver files corresponding to Macronix 16MB memory for different SDK versions of the RW612 chipset. Follow the instructions below to replace the necessary files in your SDK.


## SDK Versions 24.12.00 and Above

For SDK versions **24_12_00 and later**, replace the existing flash driver files **mflash_drv.c** and **mflash_drv.h** located at:
`SDK_2x_xx_xxx_RD-RW612-BGA\components\flash\mflash\rdrw612bga` with the updated files available at: [mflash_drv.c](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Macronix_16MB/SDK_24_12_00/mflash_drv.c) and [mflash_drv.h](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Macronix_16MB/SDK_24_12_00/mflash_drv.h) correspondingly.

---

If you encounter any issues, please refer to the SDK documentation or reach out for support.