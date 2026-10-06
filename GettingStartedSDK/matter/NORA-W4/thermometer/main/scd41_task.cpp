// SPDX-License-Identifier: Apache-2.0
//
// SCD41 sampling task — publishes CO₂ / temperature / humidity readings into
// the Matter Air Quality Sensor endpoint on the NORA-W40.
//
// Boots the sensor (wake → stop_periodic → self-test → start_periodic), then
// loops forever reading the SCD41 every 5 s and pushing values into 4 Matter
// attributes via esp_matter::attribute::update(). CO₂ also drives a 3-level
// AirQuality enum (Good / Fair / Poor) for the Apple Home / Google Home tile.
//
// I²C wiring + CRC / command details: see comments in this file's lower half
// (kept identical to the stage-1 probe — only the surrounding plumbing
// changed). Hardware: MikroE HVAC Click in EVK-NORA-W40 MikroBUS 1.

#include "scd41_task.h"
#include "app_priv.h"

#include <string.h>

#include "driver/i2c_master.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <esp_matter.h>
#include <esp_matter_attribute.h>

#include <app-common/zap-generated/cluster-objects.h>

using chip::app::DataModel::Nullable;
namespace AirQualityNs = chip::app::Clusters::AirQuality;
namespace TempMeasNs   = chip::app::Clusters::TemperatureMeasurement;
namespace RhMeasNs     = chip::app::Clusters::RelativeHumidityMeasurement;
namespace Co2MeasNs    = chip::app::Clusters::CarbonDioxideConcentrationMeasurement;

static const char *TAG = "scd41";

// ---- SCD41 fixed I²C address ------------------------------------------------
#define SCD41_ADDR  0x62

// ---- SCD41 command words (16-bit, big-endian on the wire) ------------------
// Source: Sensirion SCD4x Datasheet rev. 1.4 — command set table.
#define CMD_WAKE_UP            0x36F6   // ~20 ms, first wake may NACK
#define CMD_STOP_PERIODIC      0x3F86   // ~500 ms
#define CMD_GET_SERIAL         0x3682   // read 3 words (6 data + 3 CRC bytes)
#define CMD_PERFORM_SELF_TEST  0x3639   // 10 s, read 1 word (0 = pass)
#define CMD_START_PERIODIC     0x21B1   // 5 s cadence, no response
#define CMD_GET_DATA_READY     0xE4B8   // read 1 word
#define CMD_READ_MEASUREMENT   0xEC05   // read 3 words

// ---- Task config ------------------------------------------------------------
#define SCD41_TASK_STACK_WORDS   4096
#define SCD41_TASK_PRIO          5

static uint16_t s_endpoint_id = 0;

// ---- Sensirion CRC8 (polynomial 0x31, init 0xFF, no final XOR) -------------
static uint8_t sensirion_crc8(const uint8_t *data, size_t len)
{
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int b = 0; b < 8; b++) {
            crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x31)
                               : static_cast<uint8_t>(crc << 1);
        }
    }
    return crc;
}

// ---- I²C helpers ------------------------------------------------------------

static esp_err_t send_cmd(i2c_master_dev_handle_t dev, uint16_t cmd)
{
    uint8_t b[2] = { static_cast<uint8_t>(cmd >> 8), static_cast<uint8_t>(cmd & 0xFF) };
    return i2c_master_transmit(dev, b, 2, 200);
}

/// Read N words from the SCD41 (each word = 2 data bytes + 1 CRC byte).
/// Validates Sensirion CRC on every word. N must be <= 6.
static esp_err_t read_words(i2c_master_dev_handle_t dev, uint16_t *out, size_t n)
{
    if (n == 0 || n > 6) return ESP_ERR_INVALID_ARG;
    uint8_t buf[18];
    const size_t n_bytes = n * 3;
    esp_err_t err = i2c_master_receive(dev, buf, n_bytes, 200);
    if (err != ESP_OK) return err;
    for (size_t i = 0; i < n; i++) {
        const uint8_t want = sensirion_crc8(&buf[i * 3], 2);
        const uint8_t got  = buf[i * 3 + 2];
        if (got != want) {
            ESP_LOGE(TAG, "CRC fail word %u: data=%02X %02X CRC=%02X (expected %02X)",
                     static_cast<unsigned>(i), buf[i * 3], buf[i * 3 + 1], got, want);
            return ESP_ERR_INVALID_CRC;
        }
        out[i] = static_cast<uint16_t>((buf[i * 3] << 8) | buf[i * 3 + 1]);
    }
    return ESP_OK;
}

static esp_err_t cmd_then_read(i2c_master_dev_handle_t dev, uint16_t cmd,
                               uint32_t wait_ms, uint16_t *out, size_t n)
{
    esp_err_t err = send_cmd(dev, cmd);
    if (err != ESP_OK) return err;
    vTaskDelay(pdMS_TO_TICKS(wait_ms));
    return read_words(dev, out, n);
}

// ---- Matter attribute publishing -------------------------------------------

// CO₂ → AirQuality enum. 3-level mapping (Good / Fair / Poor) — these three
// enum values are always available from the cluster's mandatory FAIR feature,
// so we don't depend on optional MOD / VPO / EXP feature bits.
//   <  800 ppm → Good   (1)
//   < 1500 ppm → Fair   (2)
//   ≥ 1500 ppm → Poor   (4)
static uint8_t co2_to_air_quality(uint16_t co2_ppm)
{
    if (co2_ppm < 800)  return static_cast<uint8_t>(AirQualityNs::AirQualityEnum::kGood);
    if (co2_ppm < 1500) return static_cast<uint8_t>(AirQualityNs::AirQualityEnum::kFair);
    return                       static_cast<uint8_t>(AirQualityNs::AirQualityEnum::kPoor);
}

static void publish_to_matter(uint16_t co2_ppm, float temp_c, float rh_pct)
{
    using namespace esp_matter;

    // --- AirQuality (enum8) --------------------------------------------------
    {
        esp_matter_attr_val_t v = esp_matter_enum8(co2_to_air_quality(co2_ppm));
        attribute::update(s_endpoint_id, AirQualityNs::Id, AirQualityNs::Attributes::AirQuality::Id, &v);
    }

    // --- TemperatureMeasurement.MeasuredValue (int16, 0.01 °C) --------------
    {
        const int32_t scaled = static_cast<int32_t>(temp_c * 100.0f);
        const int16_t v_i16  = static_cast<int16_t>(
            scaled < INT16_MIN ? INT16_MIN : (scaled > INT16_MAX ? INT16_MAX : scaled));
        esp_matter_attr_val_t v = esp_matter_nullable_int16(v_i16);
        attribute::update(s_endpoint_id, TempMeasNs::Id, TempMeasNs::Attributes::MeasuredValue::Id, &v);
    }

    // --- RelativeHumidityMeasurement.MeasuredValue (uint16, 0.01 %) ---------
    {
        float    clamped = rh_pct < 0.0f ? 0.0f : (rh_pct > 100.0f ? 100.0f : rh_pct);
        uint16_t v_u16   = static_cast<uint16_t>(clamped * 100.0f);
        esp_matter_attr_val_t v = esp_matter_nullable_uint16(v_u16);
        attribute::update(s_endpoint_id, RhMeasNs::Id, RhMeasNs::Attributes::MeasuredValue::Id, &v);
    }

    // --- CarbonDioxideConcentrationMeasurement.MeasuredValue (float, ppm) ---
    // The concentration_measurement base cluster uses a single-precision float
    // for MeasuredValue regardless of medium (Air) and unit (PPM).
    {
        esp_matter_attr_val_t v = esp_matter_nullable_float(static_cast<float>(co2_ppm));
        attribute::update(s_endpoint_id, Co2MeasNs::Id, Co2MeasNs::Attributes::MeasuredValue::Id, &v);
    }
}

// ---- Sensor bring-up + sampling loop ---------------------------------------

static void scd41_task(void * /*arg*/)
{
    ESP_LOGI(TAG, "============================================================");
    ESP_LOGI(TAG, "  SCD41 task — endpoint %u (Air Quality Sensor)", s_endpoint_id);
    ESP_LOGI(TAG, "============================================================");
    ESP_LOGI(TAG, "MikroBUS 1: SDA=GPIO%d  SCL=GPIO%d  SCD41 addr=0x%02X",
             APP_DS2482_SDA, APP_DS2482_SCL, SCD41_ADDR);

    // --- Open I²C master bus (100 kHz; SCD41 spec max) ----------------------
    i2c_master_bus_config_t bus_cfg = {};
    bus_cfg.i2c_port               = I2C_NUM_0;
    bus_cfg.sda_io_num             = static_cast<gpio_num_t>(APP_DS2482_SDA);
    bus_cfg.scl_io_num             = static_cast<gpio_num_t>(APP_DS2482_SCL);
    bus_cfg.clk_source             = I2C_CLK_SRC_DEFAULT;
    bus_cfg.glitch_ignore_cnt      = 7;
    bus_cfg.flags.enable_internal_pullup = true;

    i2c_master_bus_handle_t bus = nullptr;
    esp_err_t err = i2c_new_master_bus(&bus_cfg, &bus);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "i2c_new_master_bus failed: %s — task exiting", esp_err_to_name(err));
        vTaskDelete(nullptr);
    }

    // --- Attach SCD41 device handle -----------------------------------------
    i2c_device_config_t dev_cfg = {};
    dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_7;
    dev_cfg.device_address  = SCD41_ADDR;
    dev_cfg.scl_speed_hz    = 100000;

    i2c_master_dev_handle_t dev = nullptr;
    if (i2c_master_bus_add_device(bus, &dev_cfg, &dev) != ESP_OK) {
        ESP_LOGE(TAG, "i2c_master_bus_add_device(0x%02X) failed — task exiting", SCD41_ADDR);
        vTaskDelete(nullptr);
    }

    // --- Wake-up (first wake_up NACKs by design — ignore) -------------------
    // Per Sensirion SCD4x datasheet §3.9.5, the sensor does NOT acknowledge
    // the wake_up command. The ESP-IDF `i2c.master` driver logs the NACK as
    // ESP_LOGE which looks alarming — silence it just for this one call so
    // the boot log stays clean. Wait the documented 20 ms (we give 30 ms).
    ESP_LOGI(TAG, "Wake up...");
    esp_log_level_t prev_i2c_lvl = esp_log_level_get("i2c.master");
    esp_log_level_set("i2c.master", ESP_LOG_NONE);
    (void)send_cmd(dev, CMD_WAKE_UP);
    vTaskDelay(pdMS_TO_TICKS(30));
    esp_log_level_set("i2c.master", prev_i2c_lvl);

    // --- Stop any leftover periodic measurement -----------------------------
    ESP_LOGI(TAG, "Stop periodic measurement (clean state)...");
    if (send_cmd(dev, CMD_STOP_PERIODIC) != ESP_OK) {
        ESP_LOGE(TAG, "  NACK — SCD41 not responding (check HVAC Click seat + VCC SEL=3V3)");
        vTaskDelete(nullptr);
    }
    vTaskDelay(pdMS_TO_TICKS(500));

    // --- Serial number (proves bidirectional comm + CRC) --------------------
    uint16_t serial[3] = {};
    if (cmd_then_read(dev, CMD_GET_SERIAL, 2, serial, 3) == ESP_OK) {
        ESP_LOGI(TAG, "Serial number: %04X:%04X:%04X", serial[0], serial[1], serial[2]);
    }

    // --- Self-test (10 s on-chip diagnostic) --------------------------------
    ESP_LOGI(TAG, "Self-test (10 s, please wait)...");
    uint16_t selftest = 0xFFFF;
    err = cmd_then_read(dev, CMD_PERFORM_SELF_TEST, 10000, &selftest, 1);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "  self-test command failed: %s", esp_err_to_name(err));
    } else if (selftest != 0) {
        ESP_LOGE(TAG, "  self-test FAILED — error code 0x%04X", selftest);
    } else {
        ESP_LOGI(TAG, "  Self-test PASSED \xE2\x9C\x93");
    }

    // --- Start periodic measurement (5 s cadence) ---------------------------
    ESP_LOGI(TAG, "Start periodic measurement (5 s cadence)");
    if (send_cmd(dev, CMD_START_PERIODIC) != ESP_OK) {
        ESP_LOGE(TAG, "  start_periodic_measurement NACK — task exiting");
        vTaskDelete(nullptr);
    }

    // --- Sampling loop ------------------------------------------------------
    // The SCD41 latches a new sample every ~5 s. We poll data-ready first
    // (handles the first-cycle warm-up), then read the 3-word measurement.
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(5000));

        uint16_t ready = 0;
        if (cmd_then_read(dev, CMD_GET_DATA_READY, 1, &ready, 1) != ESP_OK) continue;
        if ((ready & 0x07FF) == 0) {
            ESP_LOGD(TAG, "  data not ready (status=0x%04X), retrying", ready);
            continue;
        }

        uint16_t w[3] = {};
        if (cmd_then_read(dev, CMD_READ_MEASUREMENT, 1, w, 3) != ESP_OK) continue;

        const uint16_t co2_ppm = w[0];
        const float    temp_c  = -45.0f + 175.0f * static_cast<float>(w[1]) / 65535.0f;
        const float    rh_pct  =          100.0f * static_cast<float>(w[2]) / 65535.0f;

        ESP_LOGI(TAG, "CO\xE2\x82\x82 = %4u ppm   T = %5.2f \xC2\xB0""C   RH = %4.1f %%",
                 static_cast<unsigned>(co2_ppm), temp_c, rh_pct);

        publish_to_matter(co2_ppm, temp_c, rh_pct);
    }
}

// ---- Public entry point -----------------------------------------------------

extern "C" int scd41_task_start(uint16_t endpoint_id)
{
    s_endpoint_id = endpoint_id;
    BaseType_t ok = xTaskCreate(scd41_task, "scd41", SCD41_TASK_STACK_WORDS,
                                nullptr, SCD41_TASK_PRIO, nullptr);
    if (ok != pdPASS) {
        ESP_LOGE(TAG, "xTaskCreate(scd41) failed");
        return -1;
    }
    ESP_LOGI(TAG, "SCD41 task started (endpoint %u)", endpoint_id);
    return 0;
}
