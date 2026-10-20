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

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_err.h"
#include "esp_log.h"
#include "assert.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "nvs_flash.h"
#include "esp_event.h"  // esp-idf < v5.1 change to #include "esp_event_loop.h"

#include "lwip/err.h"
#include "lwip/sys.h"

#include "otp_defs.h"
#include "otp_reader.h"
#include "ubx_phy_cal.h"

static const char *TAG = "u-blox OTP, phy cal";

static void wifi_init_sta(void);
static void event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data);

void app_main(void)
{
    int8_t freq_cal = 0;
    uint8_t mac_wifi_sta[cbOTP_SIZE_MAC];
    uint8_t mac_wifi_eth[cbOTP_SIZE_MAC];
    uint8_t mac_wifi_bt[cbOTP_SIZE_MAC];
    uint8_t mac_wifi_ap[cbOTP_SIZE_MAC];
    uint8_t uuid[cbOTP_SIZE_UUID];
    uint8_t type_code[cbOTP_SIZE_TYPE_CODE + 1];
    memset(type_code, 0, sizeof(type_code));

    // Initialize NVS, needed for wifi phy cal
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // Try to detect the flash chip used
    // Must be done before reading using the OTP.
    if (otp_probe() == ESP_OK) {
        ESP_LOGI(TAG, "Sucessfully detected flash chip\n");
    } else {
        ESP_LOGE(TAG, "otp_probe failed, could not detected flash chip. OTP functionality not available.");
        assert(false);
    }

    ESP_ERROR_CHECK(otp_read_rf_freq_calibration(&freq_cal));
    ESP_LOGI(TAG, "freq_cal_val: %d\n", freq_cal);

    ESP_ERROR_CHECK(otp_read_mac_wifi_sta(mac_wifi_sta));
    ESP_ERROR_CHECK(otp_read_mac_eth(mac_wifi_eth));
    ESP_ERROR_CHECK(otp_read_mac_bt(mac_wifi_bt));
    ESP_ERROR_CHECK(otp_read_mac_wifi_ap(mac_wifi_ap));

    ESP_LOG_BUFFER_HEX("mac_wifi_sta", mac_wifi_sta, cbOTP_SIZE_MAC);
    ESP_LOG_BUFFER_HEX("mac_wifi_eth", mac_wifi_eth, cbOTP_SIZE_MAC);
    ESP_LOG_BUFFER_HEX("mac_wifi_bt", mac_wifi_bt, cbOTP_SIZE_MAC);
    ESP_LOG_BUFFER_HEX("mac_wifi_ap", mac_wifi_ap, cbOTP_SIZE_MAC);

    ESP_ERROR_CHECK(otp_read_uuid(uuid));
    ESP_LOG_BUFFER_HEX("UUID", uuid, cbOTP_SIZE_UUID);

    ESP_ERROR_CHECK(otp_read_type_code(type_code));
    ESP_LOGI(TAG, "Type code: %s", (char*)type_code);

    ESP_LOGI(TAG, "Starting WiFi. This will trigger a call to esp_phy_get_init_data from esp-idf code.");
    wifi_init_sta();
}

static void wifi_init_sta(void)
{
    printf("%s\n", IDF_VER);
    
    ESP_ERROR_CHECK(esp_netif_init());  // esp-idf < v4.3 change to tcpip_adapter_init();

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta(); // Necessary for version v5.1 or up

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = CONFIG_EXAMPLE_WIFI_SSID,
            .password = CONFIG_EXAMPLE_WIFI_PASSWORD,
        },
    };
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA) );
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config) );
    ESP_ERROR_CHECK(esp_wifi_start() );

    ESP_LOGI(TAG, "wifi_init_sta finished.");
}

static void event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        esp_wifi_connect();
        ESP_LOGI(TAG,"connect to the AP fail, retrying...");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {

        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI(TAG, "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
    }
}
