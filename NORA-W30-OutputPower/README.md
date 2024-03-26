# u-blox NORA-W30 openCPU output power settings

1. Add the file **rtw_opt_rf_para_rtl8721d_uCX_cert_v2.c** to the SDK folder:<br>
**{SDK Base}/component/common/drivers/wlan/realtek/src/core/option/**<br>
Include the file in the build, and remove the default file.

2. For a GCC build of the Realtek example project:<br>
**{SDK Base}/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp/asdk/make/wlan/option/Makefile**<br>
Comment out:  **CSRC = $(DIR)/rtw_opt_rf_para_rtl8721d.c**<br>
Added in place of: **CSRC = $(DIR)/rtw_opt_rf_para_rtl8721d_uCX_cert_v2.c**

![alt text](image.png)
