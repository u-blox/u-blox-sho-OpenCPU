/***********************************************************************************************************************
 *
 * Copyright 2024 NXP
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 *
 * Modified by u-blox for IRIS-W1 2024
*/



#include "fsl_common.h"
#include "fsl_gpio.h"
#include "fsl_io_mux.h"
#include "pin_mux.h"

/* FUNCTION ************************************************************************************************************
 *
 * Function Name : BOARD_InitBootPins
 * Description   : Calls initialization functions.
 *
 * END ****************************************************************************************************************/

void BOARD_InitBootPins(void)
{
    BOARD_InitPins();
}

/* FUNCTION ************************************************************************************************************
 *
 * Function Name : BOARD_InitPins
 * Description   : 
 *
 * END ****************************************************************************************************************/
/* Function assigned for the Cortex-M33 */

void BOARD_InitPins(void)
{

    /* Initialize FC3_USART_DATA functionality on pin GPIO_24 (pin E5) */
    IO_MUX_SetPinMux(IO_MUX_FC3_USART_DATA);
    /* Initialize GPIO42 functionality on pin GPIO_42 (BLUE)(pin G13) */
    IO_MUX_SetPinMux(IO_MUX_GPIO42);
   //  Initialize GPIO43 functionality on pin GPIO_43 (GREEN) (pin H12)
    IO_MUX_SetPinMux(IO_MUX_GPIO43);
   //   Initialize GPIO44 functionality on pin GPIO_44 (RED) (pin J11)
    IO_MUX_SetPinMux(IO_MUX_GPIO44);
   //   Initialize GPIO45 functionality on pin GPIO_45 (SW1) (pin H10)
    IO_MUX_SetPinMux(IO_MUX_GPIO45);
   //  Initialize GPIO51 functionality on pin GPIO_51 (SW2) (pin M8)
    IO_MUX_SetPinMux(IO_MUX_GPIO51);
}
/***********************************************************************************************************************
 * EOF
 **********************************************************************************************************************/

