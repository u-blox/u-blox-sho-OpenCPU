/*
 * Copyright 2025 u-blox
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

#include "ubx_phy_cal.h"

#define FREQ_CHANNEL1_DIV_8kHz \
    ( 3 ) // 2.412GHz/(8kHz*10^6) = 0,3015 => ~0,3 (*10 to avoid double
          // calculations)

static const char * TAG = "ubx_phy_cal";

static esp_phy_init_data_t ubx_init_data;
static int8_t calibration_8kHz;

// phy_init_data.h will declare static 'phy_init_data' variable initialized with
// default init data
const esp_phy_init_data_t * esp_phy_get_init_data( void )
{
    ubx_init_data = phy_init_data;
    int8_t * init_data = ( int8_t * ) &ubx_init_data;

    // channel 1 and 11 < 16.5dBm
    // Others < 17dBm for RED

// #if ESP_IDF_VERSION_MAJOR == 5 && ESP_IDF_VERSION_MINOR == 1 && CONFIG_IDF_TARGET_ESP32C6

    // TX Power is in 0.25dBm steps, value = dBm * 4, encoded as hex.
    // For example, 15dBm * 4 = 60 (0x3C)
    // ESP32C6 datasheet values
    init_data[2] = 0x54; // target_power_qdb_1m_2m, 84 (0x54)/4=21dbm
    init_data[3] = 0x54; // target_power_qdb_5.5m_11m, 84 (0x54)/4=21dbm
    init_data[4] = 0x50; // target_power_qdb_6m_9m, 80 (0x50)/4=20dbm
    init_data[5] = 0x50; // target_power_qdb_12m_18m, 80 (0x50)/4=20dbm
    init_data[6] = 0x50; // target_power_qdb_24m_36m, 80 (0x50)/4=20dbm
    init_data[7] = 0x4C; // target_power_qdb_48m_54m, 76 (0x4C)/4=19db
    init_data[8] = 0x4C; // target_power_qdb_HT20&HE20_mcs0_mcs1, 76 (0x4C)/4=19dbm
    init_data[9] = 0x4C; // target_power_qdb_HT20&HE20_mcs2_mcs3, 76 (0x4C)/4=19dbm
    init_data[10] = 0x4C; // target_power_qdb_HT20&HE20_mcs4_mcs5, 76 (0x4C)/4=19dbm
    init_data[11] = 0x48; // target_power_qdb_HT20&HE20_mcs6_mcs7, 72 (0x48)/4=18dbm
    init_data[12] = 0x44; // target_power_qdb_HE20_mcs8, 68 (0x44)/4=17dbm
    init_data[13] = 0x3C; // target_power_qdb_HE20_mcs9, 60 (0x3C)/4=15dbm
    init_data[14] = 0x3C; // target_power_qdb_HE20_mcs10, 60 (0x3C)/4=15dbm
    init_data[15] = 0x3C; // target_power_qdb_HE20_mcs11, 60 (0x3C)/4=15dbm
    init_data[16] = 0x3C; // target_power_qdb_HT40_mcs0_mcs1, 76 (0x4C)/4=19dbm
    init_data[17] = 0x3C; // target_power_qdb_HT40_mcs2_mcs3, 76 (0x4C)/4=19dbm
    init_data[18] = 0x3C; // target_power_qdb_HT40_mcs4_mcs5, 76 (0x4C)/4=19dbm
    init_data[19] = 0x38; // target_power_qdb_HT40_mcs6_mcs7, 72 (0x48)/4=18dbm

    // init_data[20] reserved
    // init_data[21] reserved
    // init_data[22] reserved
    // init_data[23] reserved

    init_data[24] = 0x01; // FCC enable: 1 to enable power limits for channels 19-69

    // Power limits for 11b channels (in qdb, quarter dBm)
    // Ch1: 19.1dBm (0x4C), Ch2-5: 19.8dBm (0x4F), Ch6: 19.76dBm (0x4F), Ch7-10: 19.8dBm (0x4F), Ch11: 19.6dBm (0x4E)
    init_data[25] = 0x4C; // chan1_pwr_limit_11b
    init_data[26] = 0x4F; // chan2_pwr_limit_11b
    init_data[27] = 0x4F; // chan3_pwr_limit_11b
    init_data[28] = 0x4F; // chan4_pwr_limit_11b
    init_data[29] = 0x4F; // chan5_pwr_limit_11b
    init_data[30] = 0x4F; // chan6_pwr_limit_11b
    init_data[31] = 0x4F; // chan7_pwr_limit_11b
    init_data[32] = 0x4F; // chan8_pwr_limit_11b
    init_data[33] = 0x4F; // chan9_pwr_limit_11b
    init_data[34] = 0x4F; // chan10_pwr_limit_11b
    init_data[35] = 0x4E; // chan11_pwr_limit_11b
    init_data[36] = 0x4E; // chan12_pwr_limit_11b
    init_data[37] = 0x4E; // chan13_pwr_limit_11b
    init_data[38] = 0x4E; // chan14_pwr_limit_11b

    // Power limits for 11g channels (in qdb, quarter dBm)
    // Ch1: 15.39dBm (0x3E), Ch2: 18.73dBm (0x4B), Ch3-7: 18.9dBm (0x4C), Ch8: 18.81dBm (0x4B), Ch9-10: 15.8dBm (0x3F), Ch11: 19.6dBm (0x4E)
    init_data[39] = 0x3A; // chan1_pwr_limit_11g
    init_data[40] = 0x4A; // chan2_pwr_limit_11g
    init_data[41] = 0x4B; // chan3_pwr_limit_11g
    init_data[42] = 0x4B; // chan4_pwr_limit_11g
    init_data[43] = 0x4B; // chan5_pwr_limit_11g
    init_data[44] = 0x4B; // chan6_pwr_limit_11g
    init_data[45] = 0x4B; // chan7_pwr_limit_11g
    init_data[46] = 0x4B; // chan8_pwr_limit_11g
    init_data[47] = 0x3F; // chan9_pwr_limit_11g
    init_data[48] = 0x3E; // chan10_pwr_limit_11g
    init_data[49] = 0x3F; // chan11_pwr_limit_11g
    init_data[50] = 0x3F; // chan12_pwr_limit_11g
    init_data[51] = 0x3F; // chan13_pwr_limit_11g
    init_data[52] = 0x3F; // chan14_pwr_limit_11g

    // Power limits for 11n 20M channels (in qdb, quarter dBm)
    // Ch1: 16.08dBm (0x40), Ch2: 17.56dBm (0x46), Ch3-5: 17.7dBm (0x47), Ch6: 17.67dBm (0x47), Ch7: 17.7dBm (0x47), Ch8: 17.45dBm (0x46), Ch9-11: 15.7dBm (0x3F)
    init_data[53] = 0x3F; // chan1_pwr_limit_11n_cbw20
    init_data[54] = 0x45; // chan2_pwr_limit_11n_cbw20
    init_data[55] = 0x47; // chan3_pwr_limit_11n_cbw20
    init_data[56] = 0x47; // chan4_pwr_limit_11n_cbw20
    init_data[57] = 0x47; // chan5_pwr_limit_11n_cbw20
    init_data[58] = 0x47; // chan6_pwr_limit_11n_cbw20
    init_data[59] = 0x47; // chan7_pwr_limit_11n_cbw20
    init_data[60] = 0x46; // chan8_pwr_limit_11n_cbw20
    init_data[61] = 0x3F; // chan9_pwr_limit_11n_cbw20
    init_data[62] = 0x3F; // chan10_pwr_limit_11n_cbw20
    init_data[63] = 0x3F; // chan11_pwr_limit_11n_cbw20
    init_data[64] = 0x3F; // chan12_pwr_limit_11n_cbw20
    init_data[65] = 0x3F; // chan13_pwr_limit_11n_cbw20
    init_data[66] = 0x3F; // chan14_pwr_limit_11n_cbw20

    // Power limits for 11n 40M channels (in qdb, quarter dBm)
    // Ch3: 14.87dBm (0x3C), Ch4: 14.9dBm (0x3C), Ch5: 16.58dBm (0x42), Ch6: 16.68dBm (0x43), Ch7: 16.7dBm (0x43), Ch8: 16.7dBm (0x43), Ch9: 15.17dBm (0x3D)
    init_data[67] = 0x3B; // chan3_pwr_limit_11n_cbw40
    init_data[68] = 0x3C; // chan4_pwr_limit_11n_cbw40
    init_data[69] = 0x40; // chan5_pwr_limit_11n_cbw40
    init_data[70] = 0x40; // chan6_pwr_limit_11n_cbw40
    init_data[71] = 0x40; // chan7_pwr_limit_11n_cbw40
    init_data[72] = 0x40; // chan8_pwr_limit_11n_cbw40
    init_data[73] = 0x3D; // chan9_pwr_limit_11n_cbw40

// #else
//     #error Configuration are only valid and tested for ESP32C6 IDF v5.1
// #endif

    // Print the modified PHY init data
        ESP_LOGI(TAG, "loading PHY init data from application binary");

    return &ubx_init_data;
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
