/*
 * u-blox NORA-W30: print the Wi-Fi MAC address programmed by u-blox.
 *
 * Replaces project/realtek_amebaD_va0_example/src/src_hp/main.c in Ameba-D.
 * The address is read through the Wi-Fi driver, which loads it from eFuse.
 * Nothing is written.
 */

#include "ameba_soc.h"
#include "main.h"
#include "wifi_conf.h"

extern VOID wlan_network(VOID);

static void read_mac_task(void *param)
{
    char mac[32] = {0};

    (void)param;
    while (!wifi_is_up(RTW_STA_INTERFACE)) {
        vTaskDelay(100);
    }

    if (wifi_get_mac_address(mac) == RTW_SUCCESS) {
        printf("\r\n[OK] Wi-Fi MAC: %s\r\n", mac);
    } else {
        printf("\r\n[FAIL] wifi_get_mac_address\r\n");
    }

    vTaskDelete(NULL);
}

int main(void)
{
    wlan_network();

    if (xTaskCreate(read_mac_task, "read_mac", 1024, NULL, tskIDLE_PRIORITY + 1, NULL) != pdPASS) {
        printf("\r\n[FAIL] xTaskCreate read_mac\r\n");
    }

    vTaskStartScheduler();
    return 0;
}
