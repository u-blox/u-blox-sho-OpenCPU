/*
 *  Copyright 2021 NXP
 *  All rights reserved.
 *
 *  SPDX-License-Identifier: BSD-3-Clause
 */

#define RW610
#define WIFI_BT_USE_IMU_INTERFACE

#if CONFIG_MONOLITHIC_WIFI
#define CONFIG_SOC_SERIES_RW6XX_REVISION_A2 1
#endif

#define WIFI_BT_TX_PWR_LIMITS "wlan_txpwrlimit_cfg_WW_rw610.h"
#define CONFIG_BT_SNOOP 1

/*
 * Please adjust the macros based on the radios supported by the chipset:
 *
 * For the RW612 chipset (IRIS-W10x-00B/IRIS-W10x-10B):
 *   Enable all three configurations:
 *     #define CONFIG_SUPPORT_WIFI 1
 *     #define CONFIG_SUPPORT_BLE 1
 *     #define CONFIG_SUPPORT_15D4 1
 *
 * For the RW610 chipset (IRIS-W10x-30B):
 *   Enable Wi-Fi and BLE configuration support, but disable 802.15.4 radio configuration:
 *     #define CONFIG_SUPPORT_WIFI 1
 *     #define CONFIG_SUPPORT_BLE 1
 *     #define CONFIG_SUPPORT_15D4 0
 */

#define CONFIG_SUPPORT_WIFI 1
#define CONFIG_SUPPORT_BLE 1
#define CONFIG_SUPPORT_15D4 1