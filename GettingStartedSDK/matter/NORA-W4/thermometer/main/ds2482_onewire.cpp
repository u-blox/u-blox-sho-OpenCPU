// SPDX-License-Identifier: Apache-2.0
//
// DS2482-800 I2C-to-1-Wire bridge + DS18B20 temperature reading.
//
// Uses the ESP-IDF v5.x i2c_master driver. The DS2482-800 translates I2C
// commands into 1-Wire bus operations, so we don't need GPIO bit-bang or RMT.
// This lets us use the MikroE "i2C 1-WIRE click" board on MikroBUS 1.
//
// DS18B20 protocol: Skip ROM → Convert T → wait 800 ms → Read Scratchpad.
// Only supports a single DS18B20 per channel (Skip ROM). For multi-drop,
// extend with ROM Search + Match ROM.

#include "ds2482_onewire.h"

#include <string.h>
#include "driver/i2c_master.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "ds2482";

// ---- DS2482 command bytes --------------------------------------------------
#define CMD_DRST  0xF0   // Device Reset
#define CMD_SRP   0xE1   // Set Read Pointer
#define CMD_WCFG  0xD2   // Write Configuration
#define CMD_CHSL  0xC3   // Channel Select (800 only)
#define CMD_1WRS  0xB4   // 1-Wire Reset
#define CMD_1WWB  0xA5   // 1-Wire Write Byte
#define CMD_1WRB  0x96   // 1-Wire Read Byte

// ---- DS2482 status register bits -------------------------------------------
#define ST_1WB    0x01   // 1-Wire Busy
#define ST_PPD    0x02   // Presence Pulse Detect
#define ST_SD     0x04   // Short Detected
#define ST_RST    0x10   // Device Reset

// ---- DS2482 read pointer codes ---------------------------------------------
#define PTR_STATUS  0xF0
#define PTR_DATA    0xE1

// ---- DS2482-800 channel select write/readback codes ------------------------
static const uint8_t kChWrite[8] = {
    0xF0, 0xE1, 0xD2, 0xC3, 0xB4, 0xA5, 0x96, 0x87
};
static const uint8_t kChRead[8] = {
    0xB8, 0xB1, 0xAA, 0xA3, 0x9C, 0x95, 0x8E, 0x87
};

// ---- DS18B20 ROM commands --------------------------------------------------
#define DS_READ_ROM      0x33
#define DS_SKIP_ROM      0xCC
#define DS_CONVERT_T     0x44
#define DS_WRITE_SCRATCH 0x4E
#define DS_READ_SCRATCH  0xBE
#define DS_READ_POWER    0xB4

// DS18B20 config register byte for 10-bit resolution (bits 5-6 = 01).
// 9-bit=0x1F  10-bit=0x3F  11-bit=0x5F  12-bit=0x7F (lower 5 bits = 1's).
#define DS_CFG_10BIT     0x3F

// ---- Module state ----------------------------------------------------------
static i2c_master_dev_handle_t s_dev = nullptr;
static uint8_t s_channel = 0;

// ---- Low-level helpers -----------------------------------------------------

static esp_err_t i2c_tx(const uint8_t *data, size_t len)
{
    return i2c_master_transmit(s_dev, data, len, 100);
}

static esp_err_t i2c_rx(uint8_t *data, size_t len)
{
    return i2c_master_receive(s_dev, data, len, 100);
}

/// Poll status register until 1-Wire Busy clears. Returns final status.
static esp_err_t wait_1wb(uint8_t *out)
{
    for (int i = 0; i < 200; i++) {
        uint8_t st = 0;
        ESP_RETURN_ON_ERROR(i2c_rx(&st, 1), TAG, "status read");
        if (!(st & ST_1WB)) {
            if (out) *out = st;
            return ESP_OK;
        }
        vTaskDelay(1);
    }
    ESP_LOGE(TAG, "1-Wire busy timeout");
    return ESP_ERR_TIMEOUT;
}

// ---- DS2482 operations -----------------------------------------------------

static esp_err_t ds2482_reset(void)
{
    uint8_t cmd = CMD_DRST;
    ESP_RETURN_ON_ERROR(i2c_tx(&cmd, 1), TAG, "DRST tx");
    uint8_t st = 0;
    ESP_RETURN_ON_ERROR(i2c_rx(&st, 1), TAG, "DRST rx");
    if (!(st & ST_RST)) {
        ESP_LOGE(TAG, "Device reset failed, status=0x%02X", st);
        return ESP_ERR_INVALID_RESPONSE;
    }
    return ESP_OK;
}

static esp_err_t ds2482_write_config(uint8_t cfg)
{
    // Upper nibble must be bitwise complement of lower nibble.
    uint8_t buf[2] = {
        CMD_WCFG,
        static_cast<uint8_t>((cfg & 0x0F) | ((~cfg & 0x0F) << 4))
    };
    ESP_RETURN_ON_ERROR(i2c_tx(buf, 2), TAG, "WCFG tx");
    uint8_t rb = 0;
    ESP_RETURN_ON_ERROR(i2c_rx(&rb, 1), TAG, "WCFG rx");
    if (rb != (cfg & 0x0F)) {
        ESP_LOGE(TAG, "Config verify fail: wrote 0x%02X, read 0x%02X", cfg, rb);
        return ESP_ERR_INVALID_RESPONSE;
    }
    return ESP_OK;
}

static esp_err_t ds2482_select_channel(uint8_t ch)
{
    if (ch > 7) return ESP_ERR_INVALID_ARG;
    uint8_t buf[2] = { CMD_CHSL, kChWrite[ch] };
    ESP_RETURN_ON_ERROR(i2c_tx(buf, 2), TAG, "CHSL tx");
    uint8_t rb = 0;
    ESP_RETURN_ON_ERROR(i2c_rx(&rb, 1), TAG, "CHSL rx");
    if (rb != kChRead[ch]) {
        ESP_LOGE(TAG, "Channel %d select: expected 0x%02X, got 0x%02X",
                 ch, kChRead[ch], rb);
        return ESP_ERR_INVALID_RESPONSE;
    }
    return ESP_OK;
}

// ---- 1-Wire bus operations via DS2482 --------------------------------------

static esp_err_t ow_reset(bool *presence)
{
    uint8_t cmd = CMD_1WRS;
    ESP_RETURN_ON_ERROR(i2c_tx(&cmd, 1), TAG, "1WRS tx");
    uint8_t st = 0;
    ESP_RETURN_ON_ERROR(wait_1wb(&st), TAG, "1WRS wait");
    if (st & ST_SD) {
        ESP_LOGE(TAG, "1-Wire short detected!");
        return ESP_ERR_INVALID_STATE;
    }
    if (presence) *presence = (st & ST_PPD) != 0;
    return ESP_OK;
}

static esp_err_t ow_write_byte(uint8_t byte)
{
    uint8_t buf[2] = { CMD_1WWB, byte };
    ESP_RETURN_ON_ERROR(i2c_tx(buf, 2), TAG, "1WWB tx");
    return wait_1wb(nullptr);
}

static esp_err_t ow_read_byte(uint8_t *byte)
{
    uint8_t cmd = CMD_1WRB;
    ESP_RETURN_ON_ERROR(i2c_tx(&cmd, 1), TAG, "1WRB tx");
    ESP_RETURN_ON_ERROR(wait_1wb(nullptr), TAG, "1WRB wait");
    // Point the read pointer at the data register.
    uint8_t srp[2] = { CMD_SRP, PTR_DATA };
    ESP_RETURN_ON_ERROR(i2c_tx(srp, 2), TAG, "SRP tx");
    return i2c_rx(byte, 1);
}

// ---- Public API ------------------------------------------------------------

esp_err_t ds2482_init(int sda, int scl, uint8_t i2c_addr, uint8_t channel)
{
    // Create I2C master bus (400 kHz, internal pull-ups as backup).
    i2c_master_bus_config_t bus_cfg = {};
    bus_cfg.i2c_port = I2C_NUM_0;
    bus_cfg.sda_io_num = static_cast<gpio_num_t>(sda);
    bus_cfg.scl_io_num = static_cast<gpio_num_t>(scl);
    bus_cfg.clk_source = I2C_CLK_SRC_DEFAULT;
    bus_cfg.glitch_ignore_cnt = 7;
    bus_cfg.flags.enable_internal_pullup = true;

    i2c_master_bus_handle_t bus = nullptr;
    ESP_RETURN_ON_ERROR(i2c_new_master_bus(&bus_cfg, &bus), TAG,
                        "I2C bus init failed (SDA=%d SCL=%d)", sda, scl);

    // Add DS2482 device at the given address.
    i2c_device_config_t dev_cfg = {};
    dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_7;
    dev_cfg.device_address = i2c_addr;
    dev_cfg.scl_speed_hz = 400000;

    ESP_RETURN_ON_ERROR(i2c_master_bus_add_device(bus, &dev_cfg, &s_dev), TAG,
                        "I2C add device 0x%02X failed", i2c_addr);

    s_channel = channel;

    // Reset the DS2482.
    ESP_RETURN_ON_ERROR(ds2482_reset(), TAG, "DS2482 reset");

    // Enable Active Pullup (APU) — provides strong drive for parasitic power.
    ESP_RETURN_ON_ERROR(ds2482_write_config(0x01), TAG, "DS2482 config APU");

    // Select 1-Wire channel.
    ESP_RETURN_ON_ERROR(ds2482_select_channel(channel), TAG, "Channel select");

    // Verify a 1-Wire device is present.
    bool presence = false;
    ESP_RETURN_ON_ERROR(ow_reset(&presence), TAG, "1-Wire reset");
    if (!presence) {
        ESP_LOGE(TAG, "No 1-Wire device on DS2482 channel %d (OW_IO%d) — "
                 "check wiring on the click board header", channel, channel);
        return ESP_ERR_NOT_FOUND;
    }

    // --- Read ROM (64-bit unique ID) — only works with single device on bus ---
    ESP_RETURN_ON_ERROR(ow_reset(&presence), TAG, "ROM reset");
    ESP_RETURN_ON_ERROR(ow_write_byte(DS_READ_ROM), TAG, "Read ROM cmd");
    uint8_t rom[8] = {};
    for (int i = 0; i < 8; i++) {
        ESP_RETURN_ON_ERROR(ow_read_byte(&rom[i]), TAG, "ROM byte %d", i);
    }

    // CRC8 check (Dallas/Maxim CRC, polynomial x^8+x^5+x^4+1)
    uint8_t crc = 0;
    for (int i = 0; i < 7; i++) {
        uint8_t byte = rom[i];
        for (int b = 0; b < 8; b++) {
            uint8_t mix = (crc ^ byte) & 0x01;
            crc >>= 1;
            if (mix) crc ^= 0x8C;
            byte >>= 1;
        }
    }
    if (crc != rom[7]) {
        ESP_LOGW(TAG, "ROM CRC mismatch: computed 0x%02X, got 0x%02X", crc, rom[7]);
    }

    // Identify family
    const char *sensor_name = "Unknown";
    switch (rom[0]) {
        case 0x28: sensor_name = "DS18B20";  break;
        case 0x22: sensor_name = "DS1822";   break;
        case 0x3B: sensor_name = "MAX31820"; break;
        case 0x10: sensor_name = "DS18S20 (unsupported scratchpad)"; break;
    }

    ESP_LOGI(TAG, "1-Wire ROM: %02X-%02X%02X%02X%02X%02X%02X-%02X (%s)",
             rom[0], rom[6], rom[5], rom[4], rom[3], rom[2], rom[1], rom[7],
             sensor_name);

    // --- Check power supply mode ---
    ESP_RETURN_ON_ERROR(ow_reset(&presence), TAG, "power reset");
    ESP_RETURN_ON_ERROR(ow_write_byte(DS_SKIP_ROM), TAG, "skip rom pwr");
    ESP_RETURN_ON_ERROR(ow_write_byte(DS_READ_POWER), TAG, "Read Power Supply");
    uint8_t pwr_bit = 0;
    ESP_RETURN_ON_ERROR(ow_read_byte(&pwr_bit), TAG, "power bit");
    const char *pwr_mode = (pwr_bit & 0x01) ? "external VDD" : "parasitic";
    ESP_LOGI(TAG, "Power supply: %s", pwr_mode);

    // --- Read resolution from scratchpad config register ---
    if (rom[0] == 0x28 || rom[0] == 0x22 || rom[0] == 0x3B) {
        ESP_RETURN_ON_ERROR(ow_reset(&presence), TAG, "res reset");
        ESP_RETURN_ON_ERROR(ow_write_byte(DS_SKIP_ROM), TAG, "skip rom res");
        ESP_RETURN_ON_ERROR(ow_write_byte(DS_READ_SCRATCH), TAG, "read scratch res");
        uint8_t sp[5];  // bytes 0-4: TL, TH, TH_alarm, TL_alarm, Config
        for (int i = 0; i < 5; i++) {
            ESP_RETURN_ON_ERROR(ow_read_byte(&sp[i]), TAG, "sp byte %d", i);
        }
        uint8_t cfg = (sp[4] >> 5) & 0x03;
        static const int res_bits[] = {9, 10, 11, 12};
        static const int conv_ms[]  = {94, 188, 375, 750};
        ESP_LOGI(TAG, "Resolution at boot: %d-bit (%.4f °C/LSB, %d ms conversion)",
                 res_bits[cfg], 0.5f / (1 << cfg), conv_ms[cfg]);

        /* --- Write scratchpad to force 10-bit resolution ---
         * 0.25 °C step is plenty for room temperature and the conversion
         * shrinks 750 · ms → 187.5 ms (~4× less mA·s per read). Kept in
         * sync with NORA-B20 thermometer. The DS18B20 itself is only
         * spec'd to ±0.5 °C, so 12-bit precision is mostly noise anyway. */
        if (cfg != 0x01) {  // 0x01 == 10-bit
            ESP_RETURN_ON_ERROR(ow_reset(&presence), TAG, "cfg reset");
            ESP_RETURN_ON_ERROR(ow_write_byte(DS_SKIP_ROM), TAG, "skip rom cfg");
            ESP_RETURN_ON_ERROR(ow_write_byte(DS_WRITE_SCRATCH), TAG, "write scratch");
            ESP_RETURN_ON_ERROR(ow_write_byte(0x00), TAG, "TH");          // alarm high
            ESP_RETURN_ON_ERROR(ow_write_byte(0x00), TAG, "TL");          // alarm low
            ESP_RETURN_ON_ERROR(ow_write_byte(DS_CFG_10BIT), TAG, "cfg"); // 10-bit
            ESP_LOGI(TAG, "Set DS18B20 to 10-bit (0.25 °C, ~188 ms conversion)");
        }
    }

    ESP_LOGI(TAG, "DS2482-800 OK on I2C 0x%02X, %s on OW_IO%d "
             "(MikroBUS 1: SDA=GPIO%d SCL=GPIO%d)",
             i2c_addr, sensor_name, channel, sda, scl);
    return ESP_OK;
}

esp_err_t ds2482_read_temperature(float *celsius)
{
    if (!s_dev || !celsius) return ESP_ERR_INVALID_ARG;

    // Re-select channel (safe even if already selected).
    ESP_RETURN_ON_ERROR(ds2482_select_channel(s_channel), TAG, "ch sel");

    // --- Start conversion ---
    bool pres = false;
    ESP_RETURN_ON_ERROR(ow_reset(&pres), TAG, "rst1");
    if (!pres) return ESP_ERR_NOT_FOUND;

    ESP_RETURN_ON_ERROR(ow_write_byte(DS_SKIP_ROM), TAG, "skip rom");
    ESP_RETURN_ON_ERROR(ow_write_byte(DS_CONVERT_T), TAG, "convert T");

    // 10-bit conversion takes max 187.5 ms; 250 ms is a safe margin.
    vTaskDelay(pdMS_TO_TICKS(250));

    // --- Read scratchpad ---
    ESP_RETURN_ON_ERROR(ow_reset(&pres), TAG, "rst2");
    if (!pres) return ESP_ERR_NOT_FOUND;

    ESP_RETURN_ON_ERROR(ow_write_byte(DS_SKIP_ROM), TAG, "skip rom2");
    ESP_RETURN_ON_ERROR(ow_write_byte(DS_READ_SCRATCH), TAG, "read scratch");

    uint8_t lsb = 0, msb = 0;
    ESP_RETURN_ON_ERROR(ow_read_byte(&lsb), TAG, "lsb");
    ESP_RETURN_ON_ERROR(ow_read_byte(&msb), TAG, "msb");

    // 12-bit signed register, 0.0625 °C per LSB (low 4 bits are the sub-degree
    // fraction). At 10-bit resolution the lowest 2 bits are always 0, but the
    // raw register format is unchanged — only the step size differs. Same
    // raw-÷16 conversion still gives correct °C, just in 0.25 °C steps.
    int16_t raw = static_cast<int16_t>((msb << 8) | lsb);
    *celsius = raw / 16.0f;

    if (*celsius < -55.0f || *celsius > 125.0f) {
        ESP_LOGW(TAG, "DS18B20 out of range: %.2f °C (raw=0x%04X)",
                 *celsius, static_cast<uint16_t>(raw));
        return ESP_ERR_INVALID_RESPONSE;
    }
    return ESP_OK;
}
