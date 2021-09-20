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

#include "otp_mx25.h"

// undef to use actual OTP
//#define OTP_TEST

#define MAX_READ_SIZE                               (OTP_SPI_MAX_XFER_SIZE - 4)
#define MAX_WRITE_SIZE                              (OTP_SPI_MAX_XFER_SIZE - 4)

#define OTP_AREA_SIZE                               0x1000
#define PAGE_SIZE                                   0x100
#define REGISTER_VALUE_OFFSET                       0x01

#define SECURITY_REG_LOCK_DOWN_SEC_OTP_BIT          0x02

#define STATUS_REG_STATUS_SRWD_BIT                  0x80
#define STATUS_REG_STATUS_BP3_BIT                   0x20
#define STATUS_REG_STATUS_BP2_BIT                   0x10
#define STATUS_REG_STATUS_BP1_BIT                   0x08
#define STATUS_REG_STATUS_BP0_BIT                   0x04
#define STATUS_REG_WRITE_ENABLED_BIT                0x02
#define STATUS_REG_WRITE_IN_PROGRESS_BIT            0x01
#define STATUS_REG_CONFIG_1_TB_BIT                  0x08
#define STATUS_REG_CONFIG_2_POWER_MODE_BIT          0x04


#define MIN(a,b) ((a) < (b) ? (a) : (b))

#define CMD_WRSR        0x01 //write status register
#define CMD_RDSR        0x05 //Read status register
#define CMD_RDCR        0x15//read configuration register
#define CMD_WRSCUR      0x2F//write security register
#define CMD_RDSCUR      0x2B//read security register

#define CMD_READ        0x03//Read
#define CMD_ENSO        0xB1 //Enter OTP
#define CMD_EXSO        0xC1 //Exit OTP

#define CMD_PP          0x02 //page program
#define CMD_WREN        0x06 //write enable
#define CMD_WRDI        0x04 //write disable




/*===========================================================================
* DECLARATIONS
*=========================================================================*/
static esp_err_t IRAM_ATTR mx25_otp_read_chunk(uint32_t offset, uint8_t *data, uint32_t len);

static esp_err_t IRAM_ATTR cmd_enter_secured_otp(void);
static esp_err_t IRAM_ATTR cmd_exit_secured_otp(void);
static esp_err_t IRAM_ATTR cmd_read_data_bytes(uint32_t offset, uint8_t *buf, uint32_t size);


static otp_ops_t mx25_otp_ops = {
    .otp_chip_read = otp_mx25_read,
};

static otp_device_t mx25_otp_dev;
/*===========================================================================
* FUNCTIONS
*=========================================================================*/
static bool is_offset_in_dev_limit(uint32_t offset, uint32_t len)
{
    return ((offset + len) < mx25_otp_dev.otp_size);
}

static esp_err_t IRAM_ATTR mx25_otp_read_chunk(uint32_t offset, uint8_t *data, uint32_t len)
{
    esp_err_t ret;
    uint32_t prev[8];

    if (!is_offset_in_dev_limit(offset, len)) {
        return ESP_FAIL;
    }

    otp_save_spi_reg(prev);
    otp_spi_configure();
    cmd_enter_secured_otp();
    ret = cmd_read_data_bytes(offset, data, len);
    cmd_exit_secured_otp();
    otp_restore_spi_reg(prev);
    return ret;
}

static esp_err_t IRAM_ATTR cmd_enter_secured_otp(void)
{
    uint8_t cmd[] = { CMD_ENSO };
    return otp_spi_xfer(cmd, sizeof(cmd), NULL, 0, NULL, 0);
}

static esp_err_t IRAM_ATTR cmd_exit_secured_otp(void)
{
    uint8_t cmd[] = { CMD_EXSO };
    return otp_spi_xfer(cmd, sizeof(cmd), NULL, 0, NULL, 0);
}

static esp_err_t IRAM_ATTR cmd_read_data_bytes(uint32_t offset, uint8_t *buf, uint32_t size)
{
    uint8_t cmd[] = {
        CMD_READ,
        (uint8_t)(offset >> 16),
        (uint8_t)(offset >> 8),
        (uint8_t)(offset)
    };

    return otp_spi_xfer(cmd, sizeof(cmd), NULL, 0, buf, size);
}

/**
* @brief Read from otp memory.
*
*        Maximum data size for the underlying spi transfer is 64 bytes.
*        4 of these are used for the spi command and next 60 bytes data
*        This function splits the read into suitable chunks.
*
*/
esp_err_t IRAM_ATTR otp_mx25_read(uint32_t offset, uint8_t *data, uint32_t len)
{
    esp_err_t err = ESP_OK;
    uint32_t rd_offser = offset;

    while ((err == ESP_OK) &&
           (rd_offser < (offset + len))) {
        uint32_t rd_len = offset + len - rd_offser;

        // Handle spi max transfer size
        rd_len = MIN(rd_len, MAX_READ_SIZE);

        err = mx25_otp_read_chunk(rd_offser, data, rd_len);
        rd_offser += rd_len;
        data += rd_len;
    }

    return err;
}

esp_err_t otp_mx25_probe(otp_device_t *otp_dev)
{
    if (otp_dev == NULL) {
        return ESP_FAIL;
    }
    otp_dev->otp_ops = &mx25_otp_ops;
    mx25_otp_dev.otp_base_address = otp_dev->otp_base_address;
    mx25_otp_dev.otp_size = otp_dev->otp_size;
    mx25_otp_dev.otp_ops = otp_dev->otp_ops;

    return ESP_OK;
}
