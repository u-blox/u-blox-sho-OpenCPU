/** @file main.c
 *
 *  @brief main file
 *
 *
 * @@ The example code to read the written Type Number (16 bytes) and Serial Number (8 bytes) of u-blox IRIS:
 *
 */

#include "fsl_device_registers.h"
#include "fsl_debug_console.h"
#include "pin_mux.h"
#include "clock_config.h"
#include "board.h"
#include "fsl_romapi_otp.h"

#include <string.h>

#include "fsl_power.h"
/*******************************************************************************
 * Definitions
 ******************************************************************************/

#define DEFAULT_SYSTEM_CLOCK                     (260000000u) /* Default System clock value */

#define TYPE_NUMBER_SIZE                         (16U)
#define SERIAL_NUMBER_SIZE                       (8U)

#define TYPE_NUMBER_START_EFUSE_ID               (305U)
#define SERIAL_NUMBER_START_EFUSE_ID             (313U)

#define TYPE_NUMBER_EFUSE_ID_COUNT               (8U)
#define SERIAL_NUMBER_EFUSE_ID_COUNT             (4U)

/*******************************************************************************
 * Prototypes
 ******************************************************************************/

/*******************************************************************************
 * Variables
 ******************************************************************************/


/*******************************************************************************
 * Code
 ******************************************************************************/
int32_t uPortReadTypeNumber(uint8_t *pTypeNumber)
{
    status_t status = kStatus_Fail;

    status = otp_init(DEFAULT_SYSTEM_CLOCK);

    if (status == kStatus_Success) {
        for (uint32_t id = TYPE_NUMBER_START_EFUSE_ID;
             id < TYPE_NUMBER_START_EFUSE_ID + TYPE_NUMBER_EFUSE_ID_COUNT; ++id) {

            // Read only 2 bytes from OTP memory due to the controller restriction
            status = otp_fuse_read(id, (uint32_t *)pTypeNumber);

            if (status != kStatus_Success) {
                break;  // Break loop on error
            }

            pTypeNumber += sizeof(uint16_t);
        }

        if (status == kStatus_Success) {
            status = otp_deinit();
            if (status != kStatus_Success) {
                status = kStatus_Fail;
            }
        }
    } else {
        status = kStatus_Fail;
    }

    return status;
}


int32_t uPortReadSerialNumber(uint8_t *pSerialNumber)
{
    status_t status = kStatus_Fail;

    status = otp_init(DEFAULT_SYSTEM_CLOCK);

    if (status == kStatus_Success) {
        for (uint32_t id = SERIAL_NUMBER_START_EFUSE_ID;
             id < SERIAL_NUMBER_START_EFUSE_ID + SERIAL_NUMBER_EFUSE_ID_COUNT; ++id) {

            // Read only 2 bytes from OTP memory due to the controller restriction
            status = otp_fuse_read(id, (uint32_t *)pSerialNumber);

            if (status != kStatus_Success) {
                break;  // Break loop on error
            }

            pSerialNumber += sizeof(uint16_t);
        }

        if (status == kStatus_Success) {
            status = otp_deinit();
            if (status != kStatus_Success) {
                status = kStatus_Fail;
            }
        }
    } else {
        status = kStatus_Fail;
    }

    return status;
}



int main()
{
    /* Init hardware */
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
        CLOCK_EnableClock(kCLOCK_Flexspi);
        RESET_ClearPeripheralReset(kFLEXSPI_RST_SHIFT_RSTn);
        /* Use aux0_pll_clk / 2 */
        BOARD_SetFlexspiClock(FLEXSPI, 2U, 2U);
    }
    BOARD_InitDebugConsole();

    status_t status;
    uint8_t typeNumber[TYPE_NUMBER_SIZE];
    status = uPortReadTypeNumber(typeNumber);
    assert(kStatus_Success == status);
    PRINTF("Type Number: 0x%X%X%X%X%X%X%X%X%X%X%X%X%X%X%X%X\r\n", typeNumber[0], typeNumber[1], typeNumber[2], typeNumber[3], typeNumber[4], typeNumber[5], typeNumber[6], typeNumber[7], typeNumber[8], typeNumber[9], typeNumber[10] ,typeNumber[11], typeNumber[12], typeNumber[13], typeNumber[14], typeNumber[15]); 
    
    uint8_t serialNumber[SERIAL_NUMBER_SIZE];
    status = uPortReadSerialNumber(serialNumber);
    assert(kStatus_Success == status);
    PRINTF("Serial Number: 0x%X%X%X%X%X%X%X%X\r\n", serialNumber[0], serialNumber[1], serialNumber[2], serialNumber[3], serialNumber[4], serialNumber[5], serialNumber[6], serialNumber[7]); 

    PRINTF("Read Type Number and Serial Number successfully!\r\n");

}
