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

#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include "esp_err.h"
#include "esp_log.h"
#include "otp_defs.h"
#include "otp_reader.h"
#include "otp_is25lp.h"
#include "otp_mx25.h"


/*===========================================================================
* DEFINES
*=========================================================================*/
#define MX25R_JEDEC_ID      0x001528C2
#define MX25U_JEDEC_ID      0x003525C2
#define MX25U6432F_JEDEC_ID 0x003725C2
#define IS25W32_JEDEC_ID    0x0016709D
#define IS25L32_JEDEC_ID    0x0016609D
#define IS25W16_JEDEC_ID    0x0015709D
#define IS25L16_JEDEC_ID    0x0015609D

/*===========================================================================
* DECLARATIONS
*=========================================================================*/
typedef struct
{
    char *otp_part_name;
    uint32_t otp_jedec_id;
    uint32_t otp_base_address;
    uint32_t otp_size;
    esp_err_t (*otp_chip_probe)(otp_device_t *otpDev);
} otp_device_list_t;

static esp_err_t is_valid_parameter(uint8_t buf[], uint32_t len);
/*===========================================================================
 * DEFINITIONS
 *=========================================================================*/
static otp_device_list_t otp_list[] =
{
    //part name    //JEDED ID       //Start address  // size   // chip probe functions
    {"MX25R1635F", MX25R_JEDEC_ID,   0x00,            0x400,    otp_mx25_probe},
    {"MX25U1635F", MX25U_JEDEC_ID,   0x10,            0x200,    otp_mx25_probe},
    {"MX25U6432F", MX25U6432F_JEDEC_ID, 0x00,         0x400,    otp_mx25_probe},
    {"IS25WP032D", IS25W32_JEDEC_ID, 0x00,            0x400,    otp_is25lp_probe},
    {"IS25LP032D", IS25L32_JEDEC_ID, 0x00,            0x400,    otp_is25lp_probe},
    {"IS25WP016D", IS25W16_JEDEC_ID, 0x00,            0x400,    otp_is25lp_probe},
    {"IS25LP016D", IS25L16_JEDEC_ID, 0x00,            0x400,    otp_is25lp_probe}
};
static otp_device_t otp_device;
const spi_flash_guard_funcs_t *spi_flash_guard_funcs = NULL;
/*===========================================================================
* FUNCTIONS
*=========================================================================*/
void IRAM_ATTR otp_restore_spi_reg(uint32_t prev[])
{
    WRITE_PERI_REG(SPI_USER_REG(OTP_SPI_HOST_ID), prev[0]);
    WRITE_PERI_REG(SPI_USER1_REG(OTP_SPI_HOST_ID), prev[1]);
    WRITE_PERI_REG(SPI_USER2_REG(OTP_SPI_HOST_ID), prev[2]);
    WRITE_PERI_REG(SPI_CTRL_REG(OTP_SPI_HOST_ID), prev[3]);
    WRITE_PERI_REG(SPI_CTRL2_REG(OTP_SPI_HOST_ID), prev[4]);
    WRITE_PERI_REG(SPI_SLAVE_REG(OTP_SPI_HOST_ID), prev[5]);
    WRITE_PERI_REG(SPI_PIN_REG(OTP_SPI_HOST_ID), prev[6]);
    WRITE_PERI_REG(SPI_CLOCK_REG(OTP_SPI_HOST_ID), prev[7]);

    if (spi_flash_guard_funcs != NULL) {
        spi_flash_guard_funcs->end();
    }
}

void IRAM_ATTR otp_save_spi_reg(uint32_t prev[])
{
    prev[0] = READ_PERI_REG(SPI_USER_REG(OTP_SPI_HOST_ID));
    prev[1] = READ_PERI_REG(SPI_USER1_REG(OTP_SPI_HOST_ID));
    prev[2] = READ_PERI_REG(SPI_USER2_REG(OTP_SPI_HOST_ID));
    prev[3] = READ_PERI_REG(SPI_CTRL_REG(OTP_SPI_HOST_ID));
    prev[4] = READ_PERI_REG(SPI_CTRL2_REG(OTP_SPI_HOST_ID));
    prev[5] = READ_PERI_REG(SPI_SLAVE_REG(OTP_SPI_HOST_ID));
    prev[6] = READ_PERI_REG(SPI_PIN_REG(OTP_SPI_HOST_ID));
    prev[7] = READ_PERI_REG(SPI_CLOCK_REG(OTP_SPI_HOST_ID));
#ifndef BOOTLOADER_BUILD
    spi_flash_guard_funcs = spi_flash_guard_get();
#endif
}

void IRAM_ATTR otp_spi_configure(void)
{
    if (spi_flash_guard_funcs != NULL) {
        spi_flash_guard_funcs->start();
    }
    // Clean SPI registers
    WRITE_PERI_REG(SPI_USER_REG(OTP_SPI_HOST_ID), 0);
    WRITE_PERI_REG(SPI_USER1_REG(OTP_SPI_HOST_ID), 0);
    WRITE_PERI_REG(SPI_USER2_REG(OTP_SPI_HOST_ID), 0);
    WRITE_PERI_REG(SPI_CTRL_REG(OTP_SPI_HOST_ID), 0);
    WRITE_PERI_REG(SPI_CTRL2_REG(OTP_SPI_HOST_ID), 0);
    WRITE_PERI_REG(SPI_SLAVE_REG(OTP_SPI_HOST_ID), 0);
    WRITE_PERI_REG(SPI_PIN_REG(OTP_SPI_HOST_ID), 0);

    // Set SPI mode 0
    CLEAR_PERI_REG_MASK(SPI_PIN_REG(OTP_SPI_HOST_ID), SPI_CK_IDLE_EDGE);
    CLEAR_PERI_REG_MASK(SPI_USER_REG(OTP_SPI_HOST_ID), SPI_CK_OUT_EDGE);

    // Set bit order to MSB
    CLEAR_PERI_REG_MASK(SPI_CTRL_REG(OTP_SPI_HOST_ID), SPI_WR_BIT_ORDER | SPI_RD_BIT_ORDER);

    // Enable full-duplex communication
    SET_PERI_REG_MASK(SPI_USER_REG(OTP_SPI_HOST_ID), SPI_DOUTDIN);

    // Configure as master
    WRITE_PERI_REG(SPI_USER1_REG(OTP_SPI_HOST_ID), 0);
    SET_PERI_REG_BITS(SPI_CTRL2_REG(OTP_SPI_HOST_ID), (unsigned long)SPI_MISO_DELAY_MODE, 0, SPI_MISO_DELAY_MODE_S);
    CLEAR_PERI_REG_MASK(SPI_SLAVE_REG(OTP_SPI_HOST_ID), SPI_SLAVE_MODE);

    // Set clock to 1 Mhz
    WRITE_PERI_REG(SPI_CLOCK_REG(OTP_SPI_HOST_ID), 0x1FFE18);

    // Enable MOSI / MISO / CS
    SET_PERI_REG_MASK(SPI_USER_REG(OTP_SPI_HOST_ID), SPI_CS_SETUP | SPI_CS_HOLD | SPI_USR_MOSI | SPI_USR_MISO);
    SET_PERI_REG_MASK(SPI_CTRL2_REG(OTP_SPI_HOST_ID), ((0x4 & SPI_MISO_DELAY_NUM) << SPI_MISO_DELAY_NUM_S));

    // Don't use command / address phase
    CLEAR_PERI_REG_MASK(SPI_USER_REG(OTP_SPI_HOST_ID), SPI_USR_COMMAND);
    SET_PERI_REG_BITS(SPI_USER2_REG(OTP_SPI_HOST_ID), SPI_USR_COMMAND_BITLEN, 0, SPI_USR_COMMAND_BITLEN_S);

    CLEAR_PERI_REG_MASK(SPI_USER_REG(OTP_SPI_HOST_ID), SPI_USR_ADDR);
    SET_PERI_REG_BITS(SPI_USER1_REG(OTP_SPI_HOST_ID), SPI_USR_ADDR_BITLEN, 0, SPI_USR_ADDR_BITLEN_S);
}

esp_err_t IRAM_ATTR otp_spi_xfer(uint8_t *cmd, uint32_t cmd_len,
	uint8_t *data_out, uint32_t data_out_len,
	uint8_t *data_in, uint32_t data_in_len)
{
    uint8_t buffer[OTP_SPI_MAX_XFER_SIZE];          // Transfer buffer
    uint32_t *p_buffer = (uint32_t*)&buffer;     // 32-bit representation of transfer buffer

    uint32_t bytes = cmd_len + data_out_len + data_in_len;
    uint32_t read_offset = cmd_len + data_out_len;
    uint32_t idx = 0;

    if (bytes > sizeof(buffer)) {
        return ESP_FAIL;
    }
    for (uint32_t j = 0; j < bytes; j++) {
        if (cmd && (j < cmd_len)) {
	        buffer[j] = *cmd;
	        cmd++;
        }
        else if (data_out && (j < (cmd_len + data_out_len))) {
            buffer[j] = *data_out;
	        data_out++;
	    }
	    else {
		    buffer[j] = 0xFF;
	    }
    }

    // Wait for SPI bus ready
    while (READ_PERI_REG(SPI_CMD_REG(OTP_SPI_HOST_ID))&SPI_USR);
    // Load send buffer
    SET_PERI_REG_BITS(SPI_MOSI_DLEN_REG(OTP_SPI_HOST_ID), SPI_USR_MOSI_DBITLEN, bytes * 8 - 1, SPI_USR_MOSI_DBITLEN_S);
    SET_PERI_REG_BITS(SPI_MISO_DLEN_REG(OTP_SPI_HOST_ID), SPI_USR_MISO_DBITLEN, bytes * 8 - 1, SPI_USR_MISO_DBITLEN_S);

    for (idx = 0; (idx << 2) < bytes; idx++) {
        WRITE_PERI_REG(SPI_W0_REG(OTP_SPI_HOST_ID) + (idx << 2), p_buffer[idx]);
    }

    // Start transfer
    SET_PERI_REG_MASK(SPI_CMD_REG(OTP_SPI_HOST_ID), SPI_USR);
    // Wait for SPI bus ready
    while (READ_PERI_REG(SPI_CMD_REG(OTP_SPI_HOST_ID))&SPI_USR);

    if (data_in) {
        // Read data into buffer
        for (idx = 0; (idx << 2) < bytes; idx++) {
            p_buffer[idx] = READ_PERI_REG(SPI_W0_REG(OTP_SPI_HOST_ID) + (idx << 2));
        }

        for (uint32_t k = read_offset; k < bytes; k++) {
            *data_in = buffer[k];
            data_in++;
        }
    }

    return ESP_OK;
}

/**
 * Detect flash chip connected over SPI by reading Flash ID
 */
esp_err_t IRAM_ATTR otp_probe(void)
{
    uint32_t buff = 0;
    uint8_t cmd[] = {OTP_RDID};
    int32_t i;
    esp_err_t err = ESP_FAIL;
    uint32_t prev[8];

    otp_save_spi_reg(prev);
    otp_spi_configure();
    err = otp_spi_xfer(cmd, sizeof(cmd), NULL, 0, (uint8_t *)&buff, 3);
    otp_restore_spi_reg(prev);

    for (i = 0; i < sizeof(otp_list) / sizeof(otp_device_list_t); i++) {
        if (buff == otp_list[i].otp_jedec_id) {
            ESP_LOGI("OTP", "Detected OTP part %s\n", otp_list[i].otp_part_name);
            otp_device.otp_part_name    = otp_list[i].otp_part_name;
            otp_device.otp_base_address = otp_list[i].otp_base_address;
            otp_device.otp_size        = otp_list[i].otp_size;
            err = otp_list[i].otp_chip_probe(&otp_device);
            return err;
        }
    }

    ESP_LOGE("OTP", "No matching flash device found\n");
    return ESP_FAIL;
}

/**
 * Read a OTP parameter
 * @param offset  The offset of the parameter to write
 * @param len     The length of the parameter to write
 * @param buf     Pointer to data to be written
 * @returns     The read length is returned. If the read fails 0 is returned
 */
uint32_t otp_read(uint32_t offset, uint8_t *buf, uint32_t len)
{
    esp_err_t err = ESP_FAIL;
    otp_ops_t *otp_ops = otp_device.otp_ops;

    if (buf == NULL || len == 0) {
        return 0;
    }
    if ((otp_ops != NULL) && (otp_ops->otp_chip_read != NULL)) {
        err = otp_ops->otp_chip_read(otp_device.otp_base_address + offset, buf, len);
    }
    return ((err == ESP_OK) ? len : 0);
}

esp_err_t otp_read_rf_freq_calibration(int8_t* freq_calibration)
{
    esp_err_t ret;

    if (freq_calibration == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ret = otp_read(cbOTP_OFFSET_RF_FREQ_CALIBRATION, (uint8_t*)freq_calibration, 1);
    if (ret != cbOTP_SIZE_RF_FREQ_CALIBRATION) {
        freq_calibration = 0;
        ret = ESP_FAIL;
    } else {
        ret = ESP_OK;
    }

    return ret;
}

esp_err_t otp_read_mac_wifi_sta(uint8_t mac[cbOTP_SIZE_MAC])
{
    esp_err_t ret;

    if (mac == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ret = otp_read(cbOTP_OFFSET_MAC_WLAN, mac, cbOTP_SIZE_MAC);
    if (ret != cbOTP_SIZE_MAC) {
        memset(mac, 0, cbOTP_SIZE_MAC);
        ret = ESP_FAIL;
    } else {
        ret = is_valid_parameter(mac, cbOTP_SIZE_MAC);
    }
    return ret;
}

esp_err_t otp_read_mac_wifi_ap(uint8_t mac[cbOTP_SIZE_MAC])
{
    esp_err_t ret;

    if (mac == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ret = otp_read(cbOTP_OFFSET_MAC_WLAN_AP, mac, cbOTP_SIZE_MAC);
    if (ret != cbOTP_SIZE_MAC) {
        memset(mac, 0, cbOTP_SIZE_MAC);
        ret = ESP_FAIL;
    } else {
        ret = is_valid_parameter(mac, cbOTP_SIZE_MAC);
    }
    return ret;
}

esp_err_t otp_read_mac_eth(uint8_t mac[cbOTP_SIZE_MAC])
{
    esp_err_t ret;

    if (mac == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ret = otp_read(cbOTP_OFFSET_MAC_ETHERNET, mac, cbOTP_SIZE_MAC);
    if (ret != cbOTP_SIZE_MAC) {
        memset(mac, 0, cbOTP_SIZE_MAC);
        ret = ESP_FAIL;
    } else {
        ret = is_valid_parameter(mac, cbOTP_SIZE_MAC);
    }

    return ret;
}

esp_err_t otp_read_mac_bt(uint8_t mac[cbOTP_SIZE_MAC])
{
    esp_err_t ret;

    if (mac == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ret = otp_read(cbOTP_OFFSET_MAC_BLUETOOTH, mac, cbOTP_SIZE_MAC);
    if (ret != cbOTP_SIZE_MAC) {
        memset(mac, 0, cbOTP_SIZE_MAC);
        ret = ESP_FAIL;
    } else {
        ret = is_valid_parameter(mac, cbOTP_SIZE_MAC);
    }
    return ret;
}

esp_err_t otp_read_uuid(uint8_t uuid[cbOTP_SIZE_UUID])
{
    esp_err_t ret;

    if (uuid == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ret = otp_read(cbOTP_OFFSET_UUID, uuid, cbOTP_SIZE_UUID);
    if (ret != cbOTP_SIZE_UUID) {
        memset(uuid, 0, cbOTP_SIZE_UUID);
        ret = ESP_FAIL;
    } else {
        ret = is_valid_parameter(uuid, cbOTP_SIZE_UUID);
    }
    return ret;
}

esp_err_t otp_read_type_code(uint8_t type_code[cbOTP_SIZE_TYPE_CODE])
{
    esp_err_t ret;

    if (type_code == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    ret = otp_read(cbOTP_OFFSET_TYPE_CODE, type_code, cbOTP_SIZE_TYPE_CODE);
    if (ret != cbOTP_SIZE_TYPE_CODE) {
        memset(type_code, 0, cbOTP_SIZE_TYPE_CODE);
        ret = ESP_FAIL;
    } else {
        ret = is_valid_parameter(type_code, cbOTP_SIZE_TYPE_CODE);
    }
    return ret;
}

/**
* @brief Check if OTP parameter is programmed.
*
* @param buf pointer to parameter value buffer
* @param len length of parameter
*
* @return ESP_OK if parameter is valid , ESP_FAIL if not
*/
static esp_err_t is_valid_parameter(uint8_t buf[], uint32_t len)
{
    for (uint8_t i = 0; i < len; i++) {
        if (buf[i] != 0xFF)
            return ESP_OK;
    }
    /* Assume non programmed memory area if contains all 0xff */
    return ESP_FAIL;
}
