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

#ifndef UBX_PHY_CALIBRATION
#define UBX_PHY_CALIBRATION

#include "esp_phy_init.h"
#include "phy_init_data.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_idf_version.h"

void ubx_phy_cal_init(void);
const esp_phy_init_data_t * esp_phy_get_init_data( void );

#endif //UBX_PHY_CALIBRATION
