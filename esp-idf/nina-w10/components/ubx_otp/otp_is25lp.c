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

#include "otp_is25lp.h"

#define MAX_READ_SIZE                               (OTP_SPI_MAX_XFER_SIZE - 4  - 1) // 4 -> CMD length; 1 byte -> for dummy clock cycle
#define MAX_WRITE_SIZE                              (OTP_SPI_MAX_XFER_SIZE - 4)
#define CMD_BLK_ERASE                               (0x64)
#define CMD_RDFR                                    (0x48)
#define CMD_WRFR                                    (0x42)
#define CMD_RDSR                                    (0x05)
#define CMD_PP                                      (0x62) // security block program
#define CMD_READ                                    (0x68) // security block read
#define CMD_WREN                                    (0x06) //write enable
#define PAGE_SIZE                                   (0x100)
#define STATUS_REG_WRITE_ENABLED_BIT                (0x02)
#define STATUS_REG_WRITE_IN_PROGRESS_BIT            (0x01)
#define SECURITY_BLOCK_LOCK_ALL                     (0xF0)
#define SECURITY_BLOCK0_START_OFFSET                (0x00000000)
#define SECURITY_BLOCK1_START_OFFSET                (0x00001000)
#define SECURITY_BLOCK2_START_OFFSET                (0x00002000)
#define SECURITY_BLOCK3_START_OFFSET                (0x00003000)
#define SECURITY_BLOCK_OFFSET_UNDEFINED             (0xFFFFFFFF)
#define MIN(a,b)                                    ((a) < (b) ? (a) : (b))


static otp_ops_t otp_is2lp_ops = {
    .otp_chip_read = otp_is25lp_read,
};

static otp_device_t is25lp_otp_dev;

/**
 * SPI command for reading a page
 */
static esp_err_t IRAM_ATTR cmd_is25lp_page_read(uint32_t offset, uint8_t *buf, uint32_t size)
{
    uint8_t cmd[] = {
        CMD_READ,
        (uint8_t)(offset >> 16),
        (uint8_t)(offset >> 8),
        (uint8_t)(offset),
        (uint8_t)(0xFF) // Added 0xff for generating 8 dummy clock cycles
    };

    return otp_spi_xfer(cmd, sizeof(cmd), NULL, 0, buf, size);
}

/**
* @brief Transform the given offset to corresponding device offset
*
* @param offset otp memory flash write start offset
* @param out device offset
* @param out available length in that block
*
* @return ESP_OK if write is successful, ESP_FAIL if not
*/

static void otp_get_dev_offset(uint32_t offset, uint32_t *dev_offset, uint32_t *avail_wr_len)
{
    if ((dev_offset == NULL) || (avail_wr_len == NULL)) {
        return;
    }

    if (offset < PAGE_SIZE) {
        *dev_offset = offset;
        *avail_wr_len = PAGE_SIZE - *dev_offset;
    } else if ((offset > (PAGE_SIZE  - 1)) && (offset < (PAGE_SIZE * 2))) {
        *dev_offset = SECURITY_BLOCK1_START_OFFSET + offset - PAGE_SIZE;
        *avail_wr_len = (SECURITY_BLOCK1_START_OFFSET + PAGE_SIZE) - *dev_offset;
    } else if ((offset > ((PAGE_SIZE * 2) - 1)) && (offset < (PAGE_SIZE * 3))) {
        *dev_offset = SECURITY_BLOCK2_START_OFFSET + offset - (PAGE_SIZE << 1);
        *avail_wr_len = (SECURITY_BLOCK2_START_OFFSET + PAGE_SIZE) - *dev_offset;
    } else if ((offset > ((PAGE_SIZE * 3) - 1)) && (offset < (PAGE_SIZE * 4))) {
        *dev_offset = SECURITY_BLOCK3_START_OFFSET + offset - (PAGE_SIZE << 2);
        *avail_wr_len = (SECURITY_BLOCK3_START_OFFSET + PAGE_SIZE) - *dev_offset;
    } else {
        *dev_offset = SECURITY_BLOCK_OFFSET_UNDEFINED;
        *avail_wr_len = 0;
    }
}


static IRAM_ATTR uint32_t is25lp_otp_read_chunk(uint32_t offset, uint8_t *data, uint32_t len)
{
    esp_err_t ret;
    uint32_t prev[8];

    otp_save_spi_reg(prev);
    otp_spi_configure();
    ret = cmd_is25lp_page_read(offset, data, len);
    otp_restore_spi_reg(prev);

    return ret;
}

/**
* @brief Read from otp memory.
*
* @param offset otp memory flash read start offset
* @param data read buffer
* @param len length of read buffer
*
* @return ESP_OK if read is successful, ESP_FAIL if not
*/
esp_err_t IRAM_ATTR otp_is25lp_read(uint32_t offset, uint8_t *data, uint32_t len)
{
    esp_err_t err = ESP_OK;
    uint32_t dev_offs;
    uint32_t max_rd_len;
    uint32_t rd_offset = offset;

    while ((err == ESP_OK) && (rd_offset < (offset + len))) {

        uint32_t rd_len = offset + len - rd_offset;
        otp_get_dev_offset(rd_offset, &dev_offs, &max_rd_len);


        if (dev_offs == SECURITY_BLOCK_OFFSET_UNDEFINED) {
            err = ESP_FAIL;
            break;
        }

        // Handle security block boundaries
        rd_len = MIN(rd_len, max_rd_len);
        // Handle spi max transfer size
        rd_len = MIN(rd_len, MAX_READ_SIZE);
        err = is25lp_otp_read_chunk(dev_offs, data, rd_len);

        rd_offset += rd_len;
        data += rd_len;
    }

    return err;
}

esp_err_t otp_is25lp_probe(otp_device_t *otp_dev)
{
    if (otp_dev == NULL) {
        return ESP_FAIL;
    }

    otp_dev->otp_ops = &otp_is2lp_ops;
    is25lp_otp_dev.otp_base_address = otp_dev->otp_base_address;
    is25lp_otp_dev.otp_size = otp_dev->otp_size;
    is25lp_otp_dev.otp_ops = otp_dev->otp_ops;
    return ESP_OK;
}
