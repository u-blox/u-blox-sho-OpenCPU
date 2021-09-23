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
#ifndef OTP_READER_H
#define OTP_READER_H

#include "esp_err.h"
#include "otp_defs.h"
#include "esp_attr.h"
#include "esp_err.h"
#include "soc/spi_reg.h"
#include "esp_spi_flash.h"

#define OTP_SPI_MAX_XFER_SIZE  (64)
#define OTP_SPI_HOST_ID        (1)
#define OTP_RDID               (0x9F)

typedef struct
{
    esp_err_t (*otp_chip_read)(uint32_t offset, uint8_t *buffOut, uint32_t buffLen);
} otp_ops_t;


typedef struct
{
    char *otp_part_name;
    uint32_t otp_base_address;
    uint32_t otp_size;
    otp_ops_t *otp_ops;
} otp_device_t;

/**
* @brief Read device specific rf frequency calibration value from otp.
*
* @param freq_calibration pointer to rf frequency calibration
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t otp_read_rf_freq_calibration(int8_t* freq_calibration);

/**
* @brief Read device specific wifi station mac address from otp
*
* @param mac pointer to mac address 
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t otp_read_mac_wifi_sta(uint8_t mac[6]);

/**
* @brief Read device specific wifi access point mac address from otp
*
* @param mac pointer to mac address
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t otp_read_mac_wifi_ap(uint8_t mac[6]);

/**
* @brief Read device specific ethernet mac address from otp
*
* @param mac pointer to mac address
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t otp_read_mac_eth(uint8_t mac[6]);

/**
* @brief Read device specific bluetooth address from otp
*
* @param mac pointer to mac address
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t otp_read_mac_bt(uint8_t mac[6]);

/**
* @brief Read device universal unique identifier from otp
*
* @param uuid pointer to uuid
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t otp_read_uuid(uint8_t uuid[cbOTP_SIZE_UUID]);

/**
* @brief Read device type code from from otp
*
* @param type_code pointer to type_code
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t otp_read_type_code(uint8_t type_code[cbOTP_SIZE_TYPE_CODE]);

/**
 * Detect flash chip connected over SPI by reading Flash ID
 */
esp_err_t otp_probe(void);
/**
 * Read a OTP parameter
 * @param offset  The offset of the parameter to write
 * @param len     The length of the parameter to write
 * @param buf     Pointer to data to be written
 * @returns     The read length is returned. If the read fails 0 is returned
 */
uint32_t otp_read(uint32_t offset, uint8_t *buf, uint32_t len);

/**
 * @brief Perform SPI transfer
 *
 * The maximum total transfer size is 64 bytes.
 * SPI data buffer hardware is 16 32-bit size registers,
 *
 * return ESP_OK if operation succeeds, ESP_FAIL is not
 */
esp_err_t IRAM_ATTR otp_spi_xfer (uint8_t *cmd, uint32_t cmd_len,
                                        uint8_t *data_out, uint32_t data_out_len,
                                        uint8_t *data_in, uint32_t data_in_len);

void IRAM_ATTR otp_restore_spi_reg(uint32_t prev[]);
void IRAM_ATTR otp_save_spi_reg(uint32_t prev[]);
void IRAM_ATTR otp_spi_configure(void);

#endif //OTP_READER_H