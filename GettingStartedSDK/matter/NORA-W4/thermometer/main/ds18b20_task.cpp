// SPDX-License-Identifier: Apache-2.0
//
// 1-Wire DS18B20 sampling task.
//
// Wakes every APP_SAMPLE_PERIOD_MS, reads the sensor via the espressif/ds18b20
// managed component (RMT-based 1-Wire), and only pushes the value into
// Matter when it changed by more than APP_REPORT_THRESHOLD_C. This keeps
// Thread radio wakeups (and AP/router beacon receptions) to a minimum,
// which is the whole point of running as an SED.

#include "ds18b20_task.h"
#include "app_priv.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#ifdef APP_USE_DS2482
#include "ds2482_onewire.h"
#else
#include "onewire_bus.h"
#include "ds18b20.h"
#endif

#include <esp_matter.h>
#include <esp_matter_attribute_utils.h>

using namespace esp_matter;
using namespace chip::app::Clusters;

static const char * TAG = "ds18b20";

static float s_last_pushed_c = -1000.0f;
static int64_t s_last_push_us = 0;

// ============================================================================
// Sensor abstraction: two compile-time implementations
// ============================================================================

#ifdef APP_USE_DS2482
// ---- DS2482 Click board path (I2C → 1-Wire bridge) -------------------------

static esp_err_t sensor_init(void)
{
    ESP_LOGI(TAG, "🔌 Using DS2482 I2C-to-1-Wire Click board (MikroBUS 1)");
    return ds2482_init(APP_DS2482_SDA, APP_DS2482_SCL,
                       APP_DS2482_ADDR, APP_DS2482_CHANNEL);
}

static esp_err_t sensor_read(float *celsius)
{
    return ds2482_read_temperature(celsius);
}

#else
// ---- Direct GPIO path (RMT bit-bang, default) ------------------------------

static onewire_bus_handle_t    s_bus = nullptr;
static ds18b20_device_handle_t s_dev = nullptr;

static esp_err_t sensor_init(void)
{
    ESP_LOGI(TAG, "📡 Using direct 1-Wire GPIO%d (RMT bit-bang)", APP_DS18B20_GPIO);

    onewire_bus_config_t bus_config = {
        .bus_gpio_num = APP_DS18B20_GPIO,
        .flags = {},
    };
    onewire_bus_rmt_config_t rmt_config = {
        .max_rx_bytes = 10,
    };
    ESP_RETURN_ON_ERROR(onewire_new_bus_rmt(&bus_config, &rmt_config, &s_bus),
                        TAG, "onewire bus create failed");

    onewire_device_iter_handle_t iter = nullptr;
    ESP_RETURN_ON_ERROR(onewire_new_device_iter(s_bus, &iter), TAG, "iter alloc");

    onewire_device_t dev = {};
    int found = 0;
    while (onewire_device_iter_get_next(iter, &dev) == ESP_OK) {
        ds18b20_config_t ds_cfg = {};
        if (ds18b20_new_device(&dev, &ds_cfg, &s_dev) == ESP_OK) {
            ESP_LOGI(TAG, "Found DS18B20 ROM=0x%016llX", dev.address);
            found++;
            break;
        }
    }
    onewire_del_device_iter(iter);

    if (found == 0) {
        ESP_LOGE(TAG, "No DS18B20 found on GPIO%d — check wiring", APP_DS18B20_GPIO);
        return ESP_ERR_NOT_FOUND;
    }

    /* 10-bit = 187.5 ms conversion, 0.25 °C step. Plenty for room
     * temperature — the DS18B20 itself is only spec'd to ±0.5 °C — and
     * ~4× less mA·s per read than 12-bit (750 ms). Battery-friendly.
     * Kept in sync with NORA-B20 thermometer. */
    return ds18b20_set_resolution(s_dev, DS18B20_RESOLUTION_10B);
}

static esp_err_t sensor_read(float *celsius)
{
    esp_err_t err = ds18b20_trigger_temperature_conversion(s_dev);
    if (err != ESP_OK) return err;
    /* 10-bit max conversion time is 187.5 ms; 250 ms = comfortable margin. */
    vTaskDelay(pdMS_TO_TICKS(250));
    return ds18b20_get_temperature(s_dev, celsius);
}

#endif // APP_USE_DS2482

static void push_to_matter(float celsius)
{
    if (g_temp_endpoint_id == 0) {
        return;                                 // Matter not yet up
    }
    const int64_t now_us = esp_timer_get_time();
    const bool keepalive_due = APP_MATTER_KEEPALIVE_MS > 0 && s_last_push_us != 0 &&
        now_us - s_last_push_us >= (int64_t)APP_MATTER_KEEPALIVE_MS * 1000;
    if (!keepalive_due && fabsf(celsius - s_last_pushed_c) < APP_REPORT_THRESHOLD_C) {
        return;                                 // suppress noise → save radio
    }

    // MeasuredValue is a nullable int16 in 0.01 °C; a non-nullable value is
    // rejected by attribute::update with INVALID_ARG.
    int16_t measured = (int16_t)lroundf(celsius * 100.0f);

    esp_matter_attr_val_t val = esp_matter_nullable_int16(nullable<int16_t>(measured));
    attribute::update(g_temp_endpoint_id,
                      TemperatureMeasurement::Id,
                      TemperatureMeasurement::Attributes::MeasuredValue::Id,
                      &val);

    ESP_LOGI(TAG, "📈 Pushed MeasuredValue: %.2f °C (raw %d)%s",
             celsius, measured, keepalive_due ? " [keepalive]" : "");
    s_last_pushed_c = celsius;
    s_last_push_us  = now_us;
}

static void sample_task(void *)
{
    if (sensor_init() != ESP_OK) {
        ESP_LOGE(TAG, "Sensor init failed — task exiting, no temperature reports");
        vTaskDelete(nullptr);
        return;
    }

    float prev_celsius = NAN;
    int stable_count = APP_FAST_COUNT;  // start in slow mode
    uint32_t sample_ms = APP_SAMPLE_PERIOD_SLOW_MS;

    ESP_LOGI(TAG, "Adaptive sampling: fast=%dms slow=%dms threshold=%.1f°C",
             APP_SAMPLE_PERIOD_FAST_MS, APP_SAMPLE_PERIOD_SLOW_MS, APP_FAST_THRESHOLD_C);

    while (true) {
        float celsius = NAN;
        if (sensor_read(&celsius) == ESP_OK &&
            celsius > -55.0f && celsius < 125.0f) {
            ESP_LOGD(TAG, "raw read: %.4f °C", celsius);
            push_to_matter(celsius);

            // Adaptive rate: fast on significant change, slow when stable
            if (!isnanf(prev_celsius) &&
                fabsf(celsius - prev_celsius) >= APP_FAST_THRESHOLD_C) {
                // Temperature is changing — switch to fast sampling
                stable_count = 0;
                if (sample_ms != APP_SAMPLE_PERIOD_FAST_MS) {
                    sample_ms = APP_SAMPLE_PERIOD_FAST_MS;
                    ESP_LOGI(TAG, "⚡ Fast sampling (%d ms) — temp changing rapidly", APP_SAMPLE_PERIOD_FAST_MS);
                }
            } else {
                // Stable reading
                if (stable_count < APP_FAST_COUNT) {
                    stable_count++;
                    if (stable_count >= APP_FAST_COUNT && sample_ms != APP_SAMPLE_PERIOD_SLOW_MS) {
                        sample_ms = APP_SAMPLE_PERIOD_SLOW_MS;
                        ESP_LOGI(TAG, "😴 Slow sampling (%d ms) — temp stable", APP_SAMPLE_PERIOD_SLOW_MS);
                    }
                }
            }
            prev_celsius = celsius;
        } else {
            ESP_LOGW(TAG, "Sensor read failed or out of range — skipping");
        }

        vTaskDelay(pdMS_TO_TICKS(sample_ms));
    }
}

void ds18b20_task_start(void)
{
    BaseType_t r = xTaskCreate(sample_task, "ds18b20",
                               4096, nullptr, tskIDLE_PRIORITY + 2, nullptr);
    if (r != pdPASS) {
        ESP_LOGE(TAG, "Failed to create DS18B20 sampling task");
    }
}
