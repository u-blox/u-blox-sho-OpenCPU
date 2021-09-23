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

#ifndef UBX_PHY_CALIBRATION
#define UBX_PHY_CALIBRATION

#include <stdbool.h>
#include "esp_err.h"
#include "esp_phy_init.h"

/**
* @brief Set the max WiFi output power. 
*        For setting to take affect this function must be called before first call to @esp_wifi_start.
*        Actual output power may be lower.
*        If not function is not called then max output power will be used.
*
* @param output_power Output power in dBm valid range is [0-14]
* @return ESP_OK if valid output power, ESP_FAIL if not
**/
esp_err_t ubx_wifi_set_max_output_power(uint32_t max_output_power_dbm);

/**
* @brief Called from esp-idf code to fetch the phy init data.
**/
const esp_phy_init_data_t* esp_phy_get_init_data(void);


#endif //UBX_PHY_CALIBRATION


