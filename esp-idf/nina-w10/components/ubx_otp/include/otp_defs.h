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

#ifndef OTP_DEFS_H
#define OTP_DEFS_H


#define cbOTP_SIZE_RF_FREQ_CALIBRATION          (1)
#define cbOTP_SIZE_MAC                          (6)
#define cbOTP_SIZE_UUID                         (16)
#define cbOTP_SIZE_SERIAL                       (8)
#define cbOTP_SIZE_TYPE_CODE                    (16)


#define cbOTP_OFFSET_RF_FREQ_CALIBRATION        (0)
#define cbOTP_OFFSET_MAC_WLAN                   (cbOTP_OFFSET_RF_FREQ_CALIBRATION + cbOTP_SIZE_RF_FREQ_CALIBRATION) //1
#define cbOTP_OFFSET_MAC_WLAN_AP                (cbOTP_OFFSET_MAC_WLAN + cbOTP_SIZE_MAC) // 7
#define cbOTP_OFFSET_MAC_ETHERNET               (cbOTP_OFFSET_MAC_WLAN_AP + cbOTP_SIZE_MAC) // 13
#define cbOTP_OFFSET_MAC_BLUETOOTH              (cbOTP_OFFSET_MAC_ETHERNET + cbOTP_SIZE_MAC) // 19
#define cbOTP_OFFSET_UUID                       (cbOTP_OFFSET_MAC_BLUETOOTH + cbOTP_SIZE_MAC) // 25
#define cbOTP_OFFSET_FEATURE_MASK               (cbOTP_OFFSET_UUID + cbOTP_SIZE_UUID) //41
#define cbOTP_OFFSET_SERIAL                     (cbOTP_OFFSET_FEATURE_MASK + 8) // 49
#define cbOTP_OFFSET_TYPE_CODE                  (cbOTP_OFFSET_SERIAL + cbOTP_SIZE_SERIAL) // 57

#endif