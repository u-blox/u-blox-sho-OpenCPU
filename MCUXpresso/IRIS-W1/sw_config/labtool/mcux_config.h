/*
 * Copyright 2025 NXP
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#ifndef _MCUX_CONFIG_H_
#define _MCUX_CONFIG_H_

#define CONFIG_DEMO_PANEL_ADAFRUIT_2_8_SUPPORT 1
#define CONFIG_DEMO_PANEL_ADAFRUIT_2_8_SUPPORT 1
#define CONFIG_DEMO_PANEL_LCD_PAR_S035_SUPPORT 1
#define CONFIG_DEMO_PANEL_LCD_PAR_S035_SUPPORT 1
#define DEMO_PANEL 7
#define CONFIG_DEMO_PANEL_ADAFRUIT_2_8 1
// #define CONFIG_DEMO_PANEL_LCD_PAR_S035 0
#define CONFIG_FLASH_BASE_ADDRESS 0x08000000
#define CONFIG_IFLASH_TEST_USE_SECTOR_INDEX_FROM_END 1
#define CONFIG_IFLASH_TEST_USE_ADDRESS 0x0
// #define CONFIG_IFLASH_EXPLICIT_DEVICE_CONFIG_VALUES 0
#define DEBUG_CONSOLE_SYNCHRONIZATION_MODE 0
// #define SERIAL_MANAGER_NON_BLOCKING_MODE 0
// #define CONFIG_DBI_USE_MIPI_PANEL 0
// #define CONFIG_STREAM_FLASH 0
#define CONFIG_LV_ATTRIBUTE_MEM_ALIGN 
#define CONFIG_LV_ATTRIBUTE_LARGE_CONST 
// #define CONFIG_BOOT_CUSTOM_DEVICE_SETUP 0
// #define CONFIG_FREERTOS_USE_CUSTOM_CONFIG_FRAGMENT 0
// #define MPU_SUPPORT 0
// #define USE_PERCEPIO_TRACELYZER 0

/*
 * Configure the following macros based on the radios supported by your target chipset:
 *
 * For RW612 (IRIS-W10x-00B / IRIS-W10x-10B):
 *   - Enable monolithic support of MFG firmware.
 *   - Supports Wi-Fi, BLE, and 802.15.4.
 *   - Enable all radio features and use a monolithic firmware combining Wi-Fi, BLE, and 802.15.4.
 *
 *     #define CONFIG_MFG_MONOLITHIC      1
 *
 *     #define CONFIG_SUPPORT_WIFI        1
 *     #define CONFIG_SUPPORT_BLE         1
 *     #define CONFIG_SUPPORT_15D4        1
 *
 *     #define CONFIG_MONOLITHIC_WIFI     1
 *     #define CONFIG_MONOLITHIC_BLE      0
 *     #define CONFIG_MONOLITHIC_BLE_15_4 1
 *
 * For RW610 (IRIS-W10x-30B):
 *   - Enable monolithic support of MFG firmware.
 *   - Supports only Wi-Fi and BLE.
 *   - Enable Wi-Fi and BLE support, disable 802.15.4, and use a monolithic Wi-Fi + BLE firmware.
 *
 *     #define CONFIG_MFG_MONOLITHIC      1
 *
 *     #define CONFIG_SUPPORT_WIFI        1
 *     #define CONFIG_SUPPORT_BLE         1
 *     #define CONFIG_SUPPORT_15D4        0
 *
 *     #define CONFIG_MONOLITHIC_WIFI     1
 *     #define CONFIG_MONOLITHIC_BLE      1
 *     #define CONFIG_MONOLITHIC_BLE_15_4 0
 */

#define CONFIG_MFG_MONOLITHIC       1

#define CONFIG_SUPPORT_WIFI         1
#define CONFIG_SUPPORT_BLE          1
#define CONFIG_SUPPORT_15D4         1

#define CONFIG_MONOLITHIC_WIFI      1
#define CONFIG_MONOLITHIC_BLE       0
#define CONFIG_MONOLITHIC_BLE_15_4  1

#endif /* _MCUX_CONFIG_H_ */
