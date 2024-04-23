# u-blox NORA-W30 openCPU output power settings

1. Download one of the two files depending of the model of NORA-W30<br><br>
2. Add the file for NORA-W301: **rtw_opt_rf_para_rtl8721d_W301.c**<br>
or the file for NORA-W306: **rtw_opt_rf_para_rtl8721d_W306.c**<br>
to the SDK folder:<br>
**{SDK Base}/component/common/drivers/wlan/realtek/src/core/option/**<br>
Include the file in the build, and remove the default file.<br><br>
3. For a GCC build of the Realtek example project:<br>
**{SDK Base}/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp/asdk/make/wlan/option/Makefile**<br><br>
Comment out:<br>
**CSRC = $(DIR)/rtw_opt_rf_para_rtl8721d.c**<br><br>
Added in place for NORA-W301: **CSRC = $(DIR)/rtw_opt_rf_para_rtl8721d_W301.c**<br>
![image](https://github.com/u-blox/u-blox-sho-OpenCPU/assets/11769925/039ebdd9-ce00-4422-92f5-3bc55d3d520a)<br><br>
or added in place for NORA-W306: **CSRC = $(DIR)/rtw_opt_rf_para_rtl8721d_W306.c**<br>
![image](https://github.com/u-blox/u-blox-sho-OpenCPU/assets/11769925/cfe6d267-0c89-425c-9948-684b2c20e190)
4. A regulatory domain channel plan must be set during WLAN initialization to maintain regulatory compliance. The codes in Table below must be used for the appropriate regulatory domain to limit Wi-Fi channel selection and output power. The OEM integrator must not allow the channel plan to able to be changed.<br>
To set the regulatory domain channel plan, the following API call is used in Realtek SDK:<br>
 **wifi_change_channel_plan(channel_plan_code)**<br>
Example: **wifi_change_channel_plan(0x3F)** for FCC regulatory domain.<br>

|Regulatory domain|Channel plan code|
|-----------------|-----------------|
|FCC|0x3F|
|ISED|0x4A|
|ETSI|0x5E|
|MKK|0x7D|


