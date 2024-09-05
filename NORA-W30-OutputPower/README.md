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
`wifi_change_channel_plan(channel_plan_code);`<br>
Example: `wifi_change_channel_plan(0x3f);` for FCC regulatory domain.<br>

|Regulatory domain|Channel plan code|
|-----------------|-----------------|
|FCC|0x3F|
|ISED|0x4A|
|ETSI|0x5E|
|MKK|0x7D|

5. The change of channel plan should be done after the restart of Wi-Fi, in this example case Stattion (RTW_MODE_STA).

```
wifi_off();
vTaskDelay(20);
if (wifi_on(RTW_MODE_STA) < 0){
    printf("\n\rERROR: Wifi on failed!");
    ret = RTW_ERROR;
    goto EXIT;
}

wifi_change_channel_plan(0x3f)
```

6. It is recommended to print the TX power values, to be sure the right values are used.

```
extern const u8 array_mp_8721d_txpwr_lmt_type1[] ;

void printallvalues(void)
{
    printf("Begin Tx Power Values \n");
    for (int i = 0; i < 70 ; i += 7) {
        printf("%d,%d,%d,%d,%d,%d,%d \n",  array_mp_8721d_txpwr_lmt_type1[i],
               array_mp_8721d_txpwr_lmt_type1[i + 1], array_mp_8721d_txpwr_lmt_type1[i + 2],
               array_mp_8721d_txpwr_lmt_type1[i + 3], array_mp_8721d_txpwr_lmt_type1[i + 4],
               array_mp_8721d_txpwr_lmt_type1[i + 5], array_mp_8721d_txpwr_lmt_type1[i + 6]);
    }
    printf("End Tx Power Values \n");
}
```

In the main(void) function, call the printallvalues() before wlan_network() function. 

```
printallvalues();
wlan_network();
```


