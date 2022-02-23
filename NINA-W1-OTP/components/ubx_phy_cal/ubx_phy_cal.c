/*
 * Copyright 2021 u-blox
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
#include "otp_reader.h"
#include "esp_log.h"
#include "phy_init_data.h"

/*===========================================================================
* DEFINES
*=========================================================================*/
#define MIN_TX_POWER                  0
#define MAX_TX_POWER                  14

#define PHY_FREQ_OFFSET_ENABLE  (105)
#define PHY_FREQ_OFFSET_VALUE   (106)
#define FREQ_CHANNEL1_DIV_8kHz  (3) // 2.412GHz/(8kHz*10^6) = 0,3015 => ~0,3 (*10 to avoid double calculations)

/*===========================================================================
* DECLARATIONS
*=========================================================================*/
static const char* TAG = "ubx_phy_cal";

static esp_phy_init_data_t ubx_init_data;
static int8_t max_output_power = 127;

/*===========================================================================
* FUNCTIONS
*=========================================================================*/

/**
  * Device specific rf calibration value is stored in flash otp area.
  * Read and apply configuration.
  */
static void apply_rf_frequency_calibration(int8_t init_data[])
{
    /*
        init_data takes the necessary correction in unit 8kHz:
        error_Hz = (err_ppm * rf_freq_ch_production)/10^6

        And then we want unit 8kHz and with correct sign:
        calibration_unit_8kHz = -error_Hz/8000

        For example, if the otp_ppm_error is -4, we should correct with: -round(-4 * FREQ_CHANNEL1_DIV_8kHz) = 1
    */
    int8_t freq_cal_val = 0;
    if (otp_read_rf_freq_calibration(&freq_cal_val) != ESP_OK) {
        freq_cal_val = 0;
        ESP_LOGW(TAG, "No RF calibration value is stored in flash, using 0 (no calibration)");
    }

    int8_t calibration_8kHz = -1 * freq_cal_val * FREQ_CHANNEL1_DIV_8kHz;

    // Round the calibration and divide by 10 to compensate for the *10 used to avoid double calculations
    if (calibration_8kHz < 0) {
        calibration_8kHz = (int8_t)((calibration_8kHz - 5) / 10);
    } else {
        calibration_8kHz = (int8_t)((calibration_8kHz + 5) / 10);
    }

    init_data[PHY_FREQ_OFFSET_VALUE] = calibration_8kHz;
    init_data[PHY_FREQ_OFFSET_ENABLE] = 1;
    ESP_LOGW(TAG, "rf freq calibration enabled, value_otp = %d(ppm), value_set = %d(8kHz)", freq_cal_val, calibration_8kHz);
}

// phy_init_data.h will declare static 'phy_init_data' variable initialized with default init data
const esp_phy_init_data_t* esp_phy_get_init_data()
{
    ubx_init_data = phy_init_data;
    int8_t *init_data = (int8_t *)&ubx_init_data;

    init_data[50] = 0; //msc0
    init_data[51] = 0; //msc1
    init_data[52] = 0; //msc2
    init_data[53] = 0; //msc3
    init_data[54] = 0; //msc4
    init_data[55] = 1; //msc5
    init_data[56] = 3; //msc6
    init_data[57] = 4; //msc7

    init_data[58] = 1; //11B special rate enable
    init_data[59] = 2; //11B 1m, 2m
    init_data[60] = 2; //11B 5.5, 11m

    init_data[61] = 50;//2; //fcc enable 2: enable 62-80 bytes to set maximum power
    /*
    0: Maximum Power is (txpwr_qdb_0/4) dbm
    1: Maximum Power is (txpwr_qdb_1/4) dbm
    2: Maximum Power is (txpwr_qdb_2/4) dbm
    3: Maximum Power is (txpwr_qdb_3/4) dbm
    4: Maximum Power is (txpwr_qdb_4/4) dbm
    5: Maximum Power is (txpwr_qdb_5/4) dbm
    6: Maximum Power is ((txpwr_qdb_5/4) - 1) dbm
    7: Maximum Power is ((txpwr_qdb_5/4) - 2) dbm
    8: Maximum Power is ((txpwr_qdb_5/4) - 3) dbm
    9: Maximum Power is ((txpwr_qdb_5/4) - 4) dbm
    10: Maximum Power is ((txpwr_qdb_5/4) -5) dbm
    62 to 80
    bit[3:0] : set the maximum tx power of channel 1 in 11g/n mode. The setting range is 0~10.
    bit[7:4] : set the maximum tx power of channel 1 in 11b mode. The setting range is 0~10.
    */
    //20M
    init_data[62] = 0x53; //channel 1
    init_data[63] = 0x52;//channel 2
    init_data[64] = 0x30;//channel 3
    init_data[65] = 0x20;//channel 4
    init_data[66] = 0x20;//channel 5
    init_data[67] = 0x20;//channel 6
    init_data[68] = 0x20;//channel 7
    init_data[69] = 0x20;//channel 8
    init_data[70] = 0x20;//channel 9
    init_data[71] = 0x20;//channel 10
    init_data[72] = 0x22;//channel 11
    init_data[73] = 0x10;//channel 12
    init_data[74] = 0x10;//channel 13
    init_data[75] = 0xAA;//channel 14

    //40M
    init_data[76] = 0x44; //channel 3, 4
    init_data[77] = 0x44; //channel 5, 6
    init_data[78] = 0x44; //channel 7, 8
    init_data[79] = 0x44; //channel 9, 10
    init_data[80] = 0x44; //channel 11

    #if ESP_IDF_VERSION_MAJOR == 4 && ESP_IDF_VERSION_MINOR == 0
    init_data[44] = 56; //target power 0
    init_data[45] = 54; //target power 1
    init_data[46] = 48; //target power 2
    init_data[47] = 46; //target power 3
    init_data[48] = 42; //target power 4
    init_data[49] = 36; //target power 5

    #elif ESP_IDF_VERSION_MAJOR == 4 && ESP_IDF_VERSION_MINOR == 3
    init_data[44] = 62; //target power 0
    init_data[45] = 60; //target power 1
    init_data[46] = 54; //target power 2
    init_data[47] = 52; //target power 3
    init_data[48] = 48; //target power 4
    init_data[49] = 42; //target power 5

    #else
    #error Configuration are only valid and tested for ESP IDF v4.0 and v4.3
    #endif 
    apply_rf_frequency_calibration(init_data);

    ESP_LOGD(TAG, "loading PHY init data from application binary");
    return (esp_phy_init_data_t*)init_data;
}