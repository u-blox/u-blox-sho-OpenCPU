/*
 * Copyright 2023 u-blox
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "esp_phy_init.h"
#include "phy_init_data.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_idf_version.h"
#include "ubx_phy_cal.h"

#define FREQ_CHANNEL1_DIV_8kHz \
    ( 3 ) // 2.412GHz/(8kHz*10^6) = 0,3015 => ~0,3 (*10 to avoid double
          // calculations)

static const char * TAG = "ubx_phy_cal";

static esp_phy_init_data_t ubx_init_data;
static int8_t calibration_8kHz;
static bool initializedCalVal = false;

// phy_init_data.h will declare static 'phy_init_data' variable initialized with
// default init data
const esp_phy_init_data_t * esp_phy_get_init_data( void )
{
    ubx_init_data = phy_init_data;
    int8_t * init_data = ( int8_t * ) &ubx_init_data;

    // channel 1 and 11 < 16.5dBm
    // Others < 17dBm for RED

#if ESP_IDF_VERSION_MAJOR == 4 && ESP_IDF_VERSION_MINOR == 4 && CONFIG_IDF_TARGET_ESP32S3

    // TX Power is in 0.25dBm steps, ie 60 = (60/4) = 15dBm
    init_data[2] = 0x50; // target_power_qdb_1m_2m
    init_data[3] = 0x50; // target_power_qdb_5.5m_11m
    init_data[4] = 0x50; // target_power_qdb_6m_9m
    init_data[5] = 0x4c; // target_power_qdb_12m_18m
    init_data[6] = 0x4c; // target_power_qdb_24m_36m
    init_data[7] = 0x48; // target_power_qdb_48m_54m
    init_data[8] = 0x4c; // target_power_qdb_HT20_mcs0_mcs1
    init_data[9] = 0x48; // target_power_qdb_HT20_mcs2_mcs3
    init_data[10] = 0x48; // target_power_qdb_HT20_mcs4_mcs5
    init_data[11] = 0x46; // target_power_qdb_HT20_mcs6_mcs7
    init_data[12] = 0x4a; // target_power_qdb_HT40_mcs0_mcs1
    init_data[13] = 0x46; // target_power_qdb_HT40_mcs2_mcs3
    init_data[14] = 0x46; // target_power_qdb_HT40_mcs4_mcs5
    init_data[15] = 0x44; // target_power_qdb_HT40_mcs6_mcs7

    // init_data[16] = 0; // power_cal_offset (?)

    init_data[18] = 0x01; // fcc enable 1: enable 19-69 bytes to set maximum power
    init_data[19] = 0x3E; // chan1_pwr_limit_11b
    init_data[20] = 0x40; // chan2_pwr_limit_11b
    init_data[21] = 0x40; // chan3_pwr_limit_11b
    init_data[22] = 0x40; // chan4_pwr_limit_11b
    init_data[23] = 0x40; // chan5_pwr_limit_11b
    init_data[24] = 0x40; // chan6_pwr_limit_11b
    init_data[25] = 0x40; // chan7_pwr_limit_11b
    init_data[26] = 0x40; // chan8_pwr_limit_11b
    init_data[27] = 0x40; // chan9_pwr_limit_11b
    init_data[28] = 0x40; // chan10_pwr_limit_11b
    init_data[29] = 0x3E; // chan11_pwr_limit_11b
    init_data[30] = 0x40; // chan12_pwr_limit_11b
    init_data[31] = 0x40; // chan13_pwr_limit_11b
    init_data[32] = 0x3E; // chan14_pwr_limit_11b
    init_data[33] = 0x3E; // chan1_pwr_limit_11g
    init_data[34] = 0x40; // chan2_pwr_limit_11g
    init_data[35] = 0x40; // chan3_pwr_limit_11g
    init_data[36] = 0x40; // chan4_pwr_limit_11g
    init_data[37] = 0x40; // chan5_pwr_limit_11g
    init_data[38] = 0x40; // chan6_pwr_limit_11g
    init_data[39] = 0x40; // chan7_pwr_limit_11g
    init_data[40] = 0x40; // chan8_pwr_limit_11g
    init_data[41] = 0x40; // chan9_pwr_limit_11g
    init_data[42] = 0x40; // chan10_pwr_limit_11g
    init_data[43] = 0x3E; // chan11_pwr_limit_11g
    init_data[44] = 0x40; // chan12_pwr_limit_11g
    init_data[45] = 0x40; // chan13_pwr_limit_11g
    init_data[46] = 0x40; // chan14_pwr_limit_11g
    init_data[47] = 0x3E; // chan1_pwr_limit_11n_cbw20
    init_data[48] = 0x3C; // chan2_pwr_limit_11n_cbw20
    init_data[49] = 0x3C; // chan3_pwr_limit_11n_cbw20
    init_data[50] = 0x3F; // chan4_pwr_limit_11n_cbw20
    init_data[51] = 0x36; // chan5_pwr_limit_11n_cbw20
    init_data[52] = 0x36; // chan6_pwr_limit_11n_cbw20
    init_data[53] = 0x38; // chan7_pwr_limit_11n_cbw20
    init_data[54] = 0x37; // chan8_pwr_limit_11n_cbw20
    init_data[55] = 0x3C; // chan9_pwr_limit_11n_cbw20
    init_data[56] = 0x3C; // chan10_pwr_limit_11n_cbw20
    init_data[57] = 0x3E; // chan11_pwr_limit_11n_cbw20
    init_data[58] = 0x3C; // chan12_pwr_limit_11n_cbw20
    init_data[59] = 0x3A; // chan13_pwr_limit_11n_cbw20
    init_data[60] = 0x40; // chan14_pwr_limit_11n_cbw20
    init_data[61] = 0x40; // chan3_pwr_limit_11n_cbw40
    init_data[62] = 0x40; // chan4_pwr_limit_11n_cbw40
    init_data[63] = 0x40; // chan5_pwr_limit_11n_cbw40
    init_data[64] = 0x40; // chan6_pwr_limit_11n_cbw40
    init_data[65] = 0x40; // chan7_pwr_limit_11n_cbw40
    init_data[66] = 0x40; // chan8_pwr_limit_11n_cbw40
    init_data[67] = 0x40; // chan9_pwr_limit_11n_cbw40
    init_data[68] = 0x40; // chan10_pwr_limit_11n_cbw40
    init_data[69] = 0x3E; // chan11_pwr_limit_11n_cbw40

#else
    #error Configuration are only valid and tested for ESP32S3 IDF v4.4
#endif

    ESP_LOGI(TAG, "loading PHY init data from application binary");

    return ( esp_phy_init_data_t * ) init_data;
}

void ubx_phy_cal_init( void )
{
    /*
        init_data takes the necessary correction in unit 8kHz:
        error_Hz = (err_ppm * rf_freq_ch_production)/10^6

        And then we want unit 8kHz and with correct sign:
        calibration_unit_8kHz = -error_Hz/8000

        For example, if the ppm_error is -4, we should correct with: -round(-4 *
        FREQ_CHANNEL1_DIV_8kHz) = 1
    */
    int8_t freq_cal_val = 0;

    calibration_8kHz = -1 * freq_cal_val * FREQ_CHANNEL1_DIV_8kHz;

    // Round the calibration and divide by 10 to compensate for the *10 used to
    // avoid double calculations
    if( calibration_8kHz < 0 )
    {
        calibration_8kHz = ( int8_t ) ( ( calibration_8kHz - 5 ) / 10 );
    }
    else
    {
        calibration_8kHz = ( int8_t ) ( ( calibration_8kHz + 5 ) / 10 );
    }

    ESP_LOGI( TAG,
              "rf freq calibration enabled, efuse_value = %d(ppm), value_set = "
              "%d(8kHz)",
              freq_cal_val,
              calibration_8kHz );
}
