// SPDX-License-Identifier: Apache-2.0
//
// NORA-W40 (ESP32-C6) Matter Thermometer — single-SoC, Matter-over-Thread SED.
//
// Boots Matter via esp-matter, registers a Temperature Sensor endpoint, then
// kicks off the DS18B20 sampling task. Sensor wiring + GPIO choice documented
// in app_priv.h and ../README.md.

#include "app_priv.h"
#include "ds18b20_task.h"

#ifdef APP_USE_HVAC
#include "scd41_task.h"
#endif

#include "esp_log.h"
#include "nvs_flash.h"

#include <esp_matter.h>
#include <esp_matter_console.h>
#include <esp_matter_ota.h>

#include <app/server/Server.h>
#include <esp_pm.h>

#if CHIP_DEVICE_CONFIG_ENABLE_THREAD
#include <openthread/instance.h>
#include <openthread/thread.h>
#include <esp_openthread.h>
#endif

#if CHIP_DEVICE_CONFIG_ENABLE_THREAD
#include <platform/ESP32/OpenthreadLauncher.h>

// OpenThread platform-config macros (per esp-matter example convention,
// each example defines its own — values cribbed from examples/light/app_priv.h).
#define ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG()       \
    { .radio_mode = RADIO_MODE_NATIVE, }

#define ESP_OPENTHREAD_DEFAULT_HOST_CONFIG()        \
    { .host_connection_mode = HOST_CONNECTION_MODE_NONE, }

#define ESP_OPENTHREAD_DEFAULT_PORT_CONFIG()        \
    { .storage_partition_name = "nvs", .netif_queue_size = 10, .task_queue_size = 10, }
#endif

using namespace esp_matter;
using namespace esp_matter::endpoint;
using namespace chip::app::Clusters;

static const char * TAG = "app_main";

uint16_t g_temp_endpoint_id = 0;

// ---------------------------------------------------------------------------
// Matter event callback. Mostly informational — we just log lifecycle events
// so the demo log tells a clear story (commissioning ✓, Thread up ✓, …).
// ---------------------------------------------------------------------------
static void on_matter_event(const ChipDeviceEvent * event, intptr_t)
{
    switch (event->Type) {
        case chip::DeviceLayer::DeviceEventType::kThreadConnectivityChange:
            ESP_LOGI(TAG, "🧵 Thread connectivity changed: %s",
                     event->ThreadConnectivityChange.Result ==
                         chip::DeviceLayer::kConnectivity_Established
                             ? "ESTABLISHED"
                             : "LOST");
            break;
        case chip::DeviceLayer::DeviceEventType::kCommissioningComplete:
            ESP_LOGI(TAG, "🎉 Commissioning complete!");
            break;
        case chip::DeviceLayer::DeviceEventType::kFabricRemoved:
            ESP_LOGW(TAG, "Fabric removed");
            break;
        default:
            break;
    }
}

// ---------------------------------------------------------------------------
// Per-cluster identify callback (spec-required). We have no LED to blink on
// the bare EVK in SED mode, so this is a no-op stub. Could toggle a GPIO if
// the demo unit grows an LED later.
// ---------------------------------------------------------------------------
static esp_err_t on_identification(identification::callback_type_t type,
                                   uint16_t endpoint_id,
                                   uint8_t /*effect_id*/,
                                   uint8_t /*effect_variant*/,
                                   void * /*priv*/)
{
    ESP_LOGI(TAG, "Identify on endpoint %u, type=%d", endpoint_id, (int)type);
    return ESP_OK;
}

// Attribute writes from the controller. We don't accept writes on
// MeasuredValue — controllers should only read/subscribe — but the callback
// must exist or the SDK rejects every write with INVALID_ACTION.
static esp_err_t on_attribute_update(attribute::callback_type_t /*type*/,
                                     uint16_t /*endpoint_id*/,
                                     uint32_t /*cluster_id*/,
                                     uint32_t /*attribute_id*/,
                                     esp_matter_attr_val_t * /*val*/,
                                     void * /*priv*/)
{
    return ESP_OK;
}

extern "C" void app_main()
{
    // --- NVS (Matter fabric storage) ----------------------------------------
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGW(TAG, "Erasing NVS (incompatible / full)");
        ESP_ERROR_CHECK(nvs_flash_erase());
        ESP_ERROR_CHECK(nvs_flash_init());
    }
    ESP_ERROR_CHECK(err);

    // --- Matter node --------------------------------------------------------
    node::config_t node_cfg;
    node_t * node = node::create(&node_cfg, on_attribute_update, on_identification);
    if (!node) {
        ESP_LOGE(TAG, "Failed to create Matter node");
        return;
    }

#ifdef APP_USE_HVAC
    // --- Air Quality Sensor endpoint (device type 0x002C) -------------------
    // The esp-matter factory creates Identify + AirQuality clusters; we attach
    // Temp, Humidity, and CO₂ concentration clusters on the same endpoint so
    // Apple Home / Google Home show the full tile (Air Quality + 3 numeric
    // sub-readings).
    air_quality_sensor::config_t aq_cfg;
    endpoint_t * ep = air_quality_sensor::create(node, &aq_cfg, ENDPOINT_FLAG_NONE, nullptr);
    if (!ep) {
        ESP_LOGE(TAG, "Failed to create Air Quality Sensor endpoint");
        return;
    }
    g_temp_endpoint_id = endpoint::get_id(ep);

    // TemperatureMeasurement cluster (int16, 0.01 °C) — SCD41 spec range.
    {
        cluster::temperature_measurement::config_t tm_cfg;
        tm_cfg.measured_value     = nullable<int16_t>();          // unknown until first sample
        tm_cfg.min_measured_value = nullable<int16_t>(-1000);     // -10.00 °C
        tm_cfg.max_measured_value = nullable<int16_t>( 6000);     //  60.00 °C
        if (!cluster::temperature_measurement::create(ep, &tm_cfg, CLUSTER_FLAG_SERVER)) {
            ESP_LOGE(TAG, "Failed to add TemperatureMeasurement cluster");
        }
    }

    // RelativeHumidityMeasurement cluster (uint16, 0.01 %).
    {
        cluster::relative_humidity_measurement::config_t rh_cfg;
        rh_cfg.measured_value     = nullable<uint16_t>();
        rh_cfg.min_measured_value = nullable<uint16_t>(0);        //   0.00 %
        rh_cfg.max_measured_value = nullable<uint16_t>(10000);    // 100.00 %
        if (!cluster::relative_humidity_measurement::create(ep, &rh_cfg, CLUSTER_FLAG_SERVER)) {
            ESP_LOGE(TAG, "Failed to add RelativeHumidityMeasurement cluster");
        }
    }

    // CarbonDioxideConcentrationMeasurement cluster (float, ppm).
    // Medium = Air (0). Feature: NumericMeasurement (bit 0). Unit = PPM (0).
    {
        cluster::concentration_measurement::config_t co2_cfg;
        co2_cfg.measurement_medium = 0;   // Air
        co2_cfg.feature_flags      = 0x01;                                       // NumericMeasurement
        co2_cfg.features.numeric_measurement.measurement_unit  = 0;              // PPM
        co2_cfg.features.numeric_measurement.min_measured_value = nullable<float>(0.0f);
        co2_cfg.features.numeric_measurement.max_measured_value = nullable<float>(40000.0f);
        if (!cluster::carbon_dioxide_concentration_measurement::create(ep, &co2_cfg, CLUSTER_FLAG_SERVER)) {
            ESP_LOGE(TAG, "Failed to add CarbonDioxideConcentrationMeasurement cluster");
        }
    }

    ESP_LOGI(TAG, "Air Quality Sensor endpoint id = %u (HVAC Click / SCD41)", g_temp_endpoint_id);
#else
    // --- Temperature Sensor endpoint (default / --clickboard builds) --------
    temperature_sensor::config_t ts_cfg;
    // MeasuredValue 0.01 °C units, int16. Start at "unknown" (NULL); first
    // real DS18B20 sample will overwrite it.
    ts_cfg.temperature_measurement.measured_value      = nullable<int16_t>(0);
    ts_cfg.temperature_measurement.min_measured_value  = nullable<int16_t>(-5500);   // -55.00 °C
    ts_cfg.temperature_measurement.max_measured_value  = nullable<int16_t>(12500);   // 125.00 °C

    endpoint_t * ep = temperature_sensor::create(node, &ts_cfg, ENDPOINT_FLAG_NONE, nullptr);
    if (!ep) {
        ESP_LOGE(TAG, "Failed to create Temperature Sensor endpoint");
        return;
    }
    g_temp_endpoint_id = endpoint::get_id(ep);
    ESP_LOGI(TAG, "Temperature Sensor endpoint id = %u", g_temp_endpoint_id);
#endif

#if CHIP_DEVICE_CONFIG_ENABLE_THREAD
    // --- OpenThread platform config (REQUIRED before esp_matter::start) ---
    esp_openthread_platform_config_t ot_config = {
        .radio_config = ESP_OPENTHREAD_DEFAULT_RADIO_CONFIG(),
        .host_config  = ESP_OPENTHREAD_DEFAULT_HOST_CONFIG(),
        .port_config  = ESP_OPENTHREAD_DEFAULT_PORT_CONFIG(),
    };
    set_openthread_platform_config(&ot_config);
#endif

    // --- Power management (explicit light sleep + DFS) -----------------------
#if CONFIG_PM_ENABLE
    esp_pm_config_t pm_config = {
        .max_freq_mhz = CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ,
        .min_freq_mhz = 10,
        .light_sleep_enable = true,
    };
    err = esp_pm_configure(&pm_config);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "\xE2\x9A\xA1 PM: light sleep enabled, DFS %d↔%d MHz",
                 10, CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ);
    } else {
        ESP_LOGW(TAG, "esp_pm_configure failed: %s (continuing without light sleep)",
                 esp_err_to_name(err));
    }
#endif

    // --- Start Matter (BLE commissioning + Thread join) ---------------------
    err = esp_matter::start(on_matter_event);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "esp_matter::start failed: %d", err);
        return;
    }

    // --- Thread SED poll period (Kconfig symbols not honored by esp-matter) --
#if CHIP_DEVICE_CONFIG_ENABLE_THREAD
    {
        otInstance *ot = esp_openthread_get_instance();
        if (ot) {
            otLinkSetPollPeriod(ot, 120000);  // 120 s — ~0.5 wakeups/min
            ESP_LOGI(TAG, "\xF0\x9F\x94\x8B Thread SED poll period set to %lu ms",
                     otLinkGetPollPeriod(ot));
        }
    }
#endif

    // --- Sensor task --------------------------------------------------------
#ifdef APP_USE_HVAC
    scd41_task_start(g_temp_endpoint_id);
#else
    ds18b20_task_start();
#endif

#ifdef APP_USE_HVAC
    ESP_LOGI(TAG, "✨ NORA-W40 Matter Air Quality Sensor up — HVAC Click (SCD41), Thread SED");
#elif defined(APP_USE_DS2482)
    ESP_LOGI(TAG, "✨ NORA-W40 Matter Thermometer up — DS2482 Click (I2C 0x%02X, OW_IO%d), Thread SED",
             APP_DS2482_ADDR, APP_DS2482_CHANNEL);
#else
    ESP_LOGI(TAG, "✨ NORA-W40 Matter Thermometer up — DS18B20 on GPIO%d, Thread SED",
             APP_DS18B20_GPIO);
#endif
}
