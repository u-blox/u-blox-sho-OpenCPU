/*
 * Copyright 2026 u-blox
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

/* Prints every MAC address the NORA-W40 firmware uses, as ESP-IDF derives them. */

#include <stdio.h>
#include <stdint.h>

#include "esp_err.h"
#include "esp_mac.h"

static void print_mac(const char *label, esp_mac_type_t type, size_t len)
{
    uint8_t mac[8] = {0};
    esp_err_t err = esp_read_mac(mac, type);

    printf("  %-20s", label);
    if (err != ESP_OK)
    {
        printf("%s\n", esp_err_to_name(err));
        return;
    }
    for (size_t i = 0; i < len; i++)
    {
        printf("%s%02X", i ? ":" : "", mac[i]);
    }
    printf("\n");
}

void app_main(void)
{
    printf("\nu-blox NORA-W40 MAC addresses\n");
    print_mac("Factory eFuse:", ESP_MAC_EFUSE_FACTORY, 6);
    print_mac("Base:", ESP_MAC_BASE, 6);
    print_mac("Wi-Fi station:", ESP_MAC_WIFI_STA, 6);
    print_mac("Wi-Fi SoftAP:", ESP_MAC_WIFI_SOFTAP, 6);
    print_mac("Bluetooth LE:", ESP_MAC_BT, 6);
    print_mac("IEEE 802.15.4:", ESP_MAC_IEEE802154, 8);

    printf("\nTo use another address, call esp_iface_mac_addr_set(mac, ESP_MAC_BASE)\n"
           "before esp_wifi_init() and esp_bt_controller_init().\n");
}
