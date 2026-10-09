/** @file main.c
 *
 *  @brief main file
 *
 *
 *
 *  @ The example code to read the written Wi-Fi STA Address (8 bytes) for u-blox IRIS:
 *
 */

///////////////////////////////////////////////////////////////////////////////
//  Includes
///////////////////////////////////////////////////////////////////////////////

// SDK Included Files
#include "pin_mux.h"
#include "clock_config.h"
#include "board.h"
#include "fsl_debug_console.h"
#include "wlan_bt_fw.h"
#include "wlan.h"
#include "wifi.h"
#include "wm_net.h"
#include <osa.h>
#include "dhcp-server.h"
#include "cli.h"
#include "iperf.h"
#include "fsl_power.h"
/*******************************************************************************
 * Definitions
 ******************************************************************************/


/*******************************************************************************
 * Prototypes
 ******************************************************************************/

/*******************************************************************************
 * Code
 ******************************************************************************/
#define MAIN_TASK_STACK_SIZE 4096

static void main_task(osa_task_param_t arg);

static OSA_TASK_DEFINE(main_task, OSA_PRIORITY_BELOW_NORMAL, 1, MAIN_TASK_STACK_SIZE, 0);

OSA_TASK_HANDLE_DEFINE(main_task_Handle);

#define WIFI_STA_ADDRESS_SIZE          (6U)

static void printSeparator(void)
{
    PRINTF("========================================\r\n");
}


/* Callback Function passed to WLAN Connection Manager. The callback function
 * gets called when there are WLAN Events that need to be handled by the
 * application.
 */
int wlan_event_callback(enum wlan_event_reason reason, void *data)
{
    switch (reason) {
        case WLAN_REASON_INITIALIZED:
            PRINTF("WLAN initialized\r\n");
            break;
        case WLAN_REASON_INITIALIZATION_FAILED:
            PRINTF("WLAN initialization failed\r\n");
            break;
        default:
            PRINTF("app_cb: WLAN: Unknown Event: %d\r\n", reason);
            break;
    }

    return 0;
}

int32_t uPortReadWifiStaMacAddress(uint8_t *pWifiStaMacAddress)
{
    uint32_t status = -WM_FAIL;

    // Before accessing the Wi-Fi CPU's OTP memory, initialization of the WIFI Driver and wlan_set_rf_test_mode() APIs is required
   
    status = wlan_set_rf_test_mode();

    if (status != WM_SUCCESS) {
        status = -WM_FAIL;
    } else {
        status = wlan_get_rf_otp_mac_addr(pWifiStaMacAddress);
    }

    if (status != WM_SUCCESS) {
        status = -WM_FAIL;
    }

    return status;
}


static void main_task(osa_task_param_t arg)
{
    int32_t result = 0;
    (void)result;

    result = cli_init();

    assert(WM_SUCCESS == result);

    PRINTF("Initialize WLAN Driver\r\n");
    printSeparator();

    /* Initialize WIFI Driver */
    result = wlan_init(wlan_fw_bin, wlan_fw_bin_len);

    assert(WM_SUCCESS == result);

    result = wlan_start(wlan_event_callback);

    assert(WM_SUCCESS == result);

    uint8_t wifiMacAddress[WIFI_STA_ADDRESS_SIZE];
    uint32_t status;
    status = uPortReadWifiStaMacAddress(wifiMacAddress);

    assert(WM_SUCCESS == status);
    PRINTF("Wifi Station Mac Address: 0x%X%X%X%X%X%X\r\n", wifiMacAddress[0], wifiMacAddress[1], wifiMacAddress[2], wifiMacAddress[3], wifiMacAddress[4], wifiMacAddress[5]); 

}


/*******************************************************************************
 * Prototypes
 ******************************************************************************/

int main(void)
{
    OSA_Init();

    BOARD_InitBootPins();
    if (BOARD_IS_XIP())
    {
        BOARD_BootClockLPR();
        CLOCK_EnableClock(kCLOCK_Otp);
        CLOCK_EnableClock(kCLOCK_Els);
        CLOCK_EnableClock(kCLOCK_ElsApb);
        RESET_PeripheralReset(kOTP_RST_SHIFT_RSTn);
        RESET_PeripheralReset(kELS_APB_RST_SHIFT_RSTn);
    }
    else
    {
        BOARD_InitBootClocks();
    }
    BOARD_InitDebugConsole();
    /* Reset GMDA */
    RESET_PeripheralReset(kGDMA_RST_SHIFT_RSTn);
    /* Keep CAU sleep clock here. */
    /* CPU1 uses Internal clock when in low power mode. */
    POWER_ConfigCauInSleep(false);
    BOARD_InitSleepPinConfig();

    printSeparator();
    PRINTF("Example code to read out the wi-Fi STA Address\r\n");
    printSeparator();

    //uPortWifiTestModeInit();
     (void)OSA_TaskCreate((osa_task_handle_t)main_task_Handle, OSA_TASK(main_task), NULL);

    OSA_Start();

    return 0;
}
