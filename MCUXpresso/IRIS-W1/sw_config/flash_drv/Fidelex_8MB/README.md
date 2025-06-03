# Flash driver

This repository provides MFlash driver files corresponding to Fidelex memory for different SDK versions of the RW612 chipset. Follow the instructions below to replace the necessary files in your SDK.

## SDK Versions 2.16.100 and Below

For SDK versions **2_16_100 and earlier**, replace the existing flash driver file **mflash_drv.c** located at:
`SDK_2_xx_xxx_RD-RW612-BGA\components\flash\mflash\rdrw612bga` with the updated file available at: [mflash_drv.c](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Fidelex_8MB/SDK_2_16_100/mflash_drv.c).

## SDK Versions 24.12.00 and Above

For SDK versions **24_12_00 and later**, replace the file **mflash_drv.c** located at:
`SDK_2x_xx_xxx_RD-RW612-BGA\components\flash\mflash\rdrw612bga` with the updated file available at: [mflash_drv.c](/MCUXpresso/IRIS-W1/sw_config/flash_drv/Fidelex_8MB/SDK_24_12_00/mflash_drv.c).

---

If you encounter any issues, please refer to the SDK documentation or reach out for support.