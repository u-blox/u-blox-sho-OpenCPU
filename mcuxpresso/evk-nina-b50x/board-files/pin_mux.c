/*
 * Copyright 2021-2023 NXP
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
/*
 * Modified by u-blox for NINA-B50 EVK 2023
*/

#include "fsl_common.h"
#include "fsl_port.h"
#include "fsl_gpio.h"
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
 * Description   : Configures pin routing and optionally pin electrical features.
 *
 * END ****************************************************************************************************************/
void BOARD_InitPins(void)
{
    /* Clock Configuration */
    CLOCK_EnableClock(kCLOCK_GpioA);
    /* Clock Configuration */
    CLOCK_EnableClock(kCLOCK_GpioC);
    /* Clock Configuration */
    CLOCK_EnableClock(kCLOCK_PortA);
    /* Clock Configuration */
    CLOCK_EnableClock(kCLOCK_PortC);

    gpio_pin_config_t LED_GREEN_config = {
        .pinDirection = kGPIO_DigitalOutput,
        .outputLogic = 0U
    };

    /* Initialize GPIO functionality on pin PTA19 (pin 14)  GREEN LED*/
    GPIO_PinInit(BOARD_INITPINS_LED_GREEN_GPIO, BOARD_INITPINS_LED_GREEN_PIN, &LED_GREEN_config);

    const port_pin_config_t LED_GREEN = {/* Internal pull-up/down resistor is disabled */
                                         (uint16_t)kPORT_PullDisable,
                                         /* Low internal pull resistor value is selected. */
                                         (uint16_t)kPORT_LowPullResistor,
                                         /* Fast slew rate is configured */
                                         (uint16_t)kPORT_FastSlewRate,
                                         /* Passive input filter is disabled */
                                         (uint16_t)kPORT_PassiveFilterDisable,
                                         /* Open drain output is disabled */
                                         (uint16_t)kPORT_OpenDrainDisable,
                                         /* Low drive strength is configured */
                                         (uint16_t)kPORT_LowDriveStrength,
                                         /* Normal drive strength is configured */
                                         (uint16_t)kPORT_NormalDriveStrength,
                                         /* Pin is configured as PTA19 */
                                         (uint16_t)kPORT_MuxAsGpio,
                                         /* Pin Control Register fields [15:0] are not locked */
                                         (uint16_t)kPORT_UnlockRegister};

    /* PORTA19 (pin 14) is configured as PTA19 */
    PORT_SetPinConfig(BOARD_INITPINS_LED_GREEN_PORT, BOARD_INITPINS_LED_GREEN_PIN, &LED_GREEN);


    gpio_pin_config_t LED_BLUE_config = {
        .pinDirection = kGPIO_DigitalOutput,
        .outputLogic = 0U
    };

    /* Initialize GPIO functionality on pin PTC5 (pin 43)  BLUE LED */
    GPIO_PinInit(BOARD_INITPINS_LED_BLUE_GPIO, BOARD_INITPINS_LED_BLUE_PIN, &LED_BLUE_config);

    const port_pin_config_t LED_BLUE = {/* Internal pull-up/down resistor is disabled */
                                         (uint16_t)kPORT_PullDisable,
                                         /* Low internal pull resistor value is selected. */
                                         (uint16_t)kPORT_LowPullResistor,
                                         /* Fast slew rate is configured */
                                         (uint16_t)kPORT_FastSlewRate,
                                         /* Passive input filter is disabled */
                                         (uint16_t)kPORT_PassiveFilterDisable,
                                         /* Open drain output is disabled */
                                         (uint16_t)kPORT_OpenDrainDisable,
                                         /* Low drive strength is configured */
                                         (uint16_t)kPORT_LowDriveStrength,
                                         /* Normal drive strength is configured */
                                         (uint16_t)kPORT_NormalDriveStrength,
                                         /* Pin is configured as PTC5 */
                                         (uint16_t)kPORT_MuxAsGpio,
                                         /* Pin Control Register fields [15:0] are not locked */
                                         (uint16_t)kPORT_UnlockRegister};
    /* PORTC15 (pin 43) is configured as PTC5 */
    PORT_SetPinConfig(BOARD_INITPINS_LED_BLUE_PORT, BOARD_INITPINS_LED_BLUE_PIN, &LED_BLUE);


    gpio_pin_config_t LED_RED_config = {
        .pinDirection = kGPIO_DigitalOutput,
        .outputLogic = 0U
    };

    /* Initialize GPIO functionality on pin PTA16 (pin 11)  */
    GPIO_PinInit(BOARD_INITPINS_LED_RED_GPIO, BOARD_INITPINS_LED_RED_PIN, &LED_RED_config);

    const port_pin_config_t LED_RED = {/* Internal pull-up/down resistor is disabled */
                                         (uint16_t)kPORT_PullDisable,
                                         /* Low internal pull resistor value is selected. */
                                         (uint16_t)kPORT_LowPullResistor,
                                         /* Fast slew rate is configured */
                                         (uint16_t)kPORT_FastSlewRate,
                                         /* Passive input filter is disabled */
                                         (uint16_t)kPORT_PassiveFilterDisable,
                                         /* Open drain output is disabled */
                                         (uint16_t)kPORT_OpenDrainDisable,
                                         /* Low drive strength is configured */
                                         (uint16_t)kPORT_LowDriveStrength,
                                         /* Normal drive strength is configured */
                                         (uint16_t)kPORT_NormalDriveStrength,
                                         /* Pin is configured as PTA19 */
                                         (uint16_t)kPORT_MuxAsGpio,
                                         /* Pin Control Register fields [15:0] are not locked */
                                         (uint16_t)kPORT_UnlockRegister};
    /* PORTA16 (pin 11) is configured as PTA16 */
    PORT_SetPinConfig(BOARD_INITPINS_LED_RED_PORT, BOARD_INITPINS_LED_RED_PIN, &LED_RED);



    const port_pin_config_t UART_RX = {/* Internal pull-up/down resistor is disabled */
                                                   (uint16_t)kPORT_PullDisable,
                                                   /* Low internal pull resistor value is selected. */
                                                   (uint16_t)kPORT_LowPullResistor,
                                                   /* Fast slew rate is configured */
                                                   (uint16_t)kPORT_FastSlewRate,
                                                   /* Passive input filter is disabled */
                                                   (uint16_t)kPORT_PassiveFilterDisable,
                                                   /* Open drain output is disabled */
                                                   (uint16_t)kPORT_OpenDrainDisable,
                                                   /* Low drive strength is configured */
                                                   (uint16_t)kPORT_LowDriveStrength,
                                                   /* Normal drive strength is configured */
                                                   (uint16_t)kPORT_NormalDriveStrength,
                                                   /* Pin is configured as LPUART1_RX */
                                                   (uint16_t)kPORT_MuxAlt3,
                                                   /* Pin Control Register fields [15:0] are not locked */
                                                   (uint16_t)kPORT_UnlockRegister};
    /* PORTC2 (pin 39) is configured as LPUART1_RX */
    PORT_SetPinConfig(BOARD_INITPINS_UART_RX_PORT, BOARD_INITPINS_UART_RX_PIN, &UART_RX);



    const port_pin_config_t UART_TX = {/* Internal pull-up/down resistor is disabled */
                                                   (uint16_t)kPORT_PullDisable,
                                                   /* Low internal pull resistor value is selected. */
                                                   (uint16_t)kPORT_LowPullResistor,
                                                   /* Fast slew rate is configured */
                                                   (uint16_t)kPORT_FastSlewRate,
                                                   /* Passive input filter is disabled */
                                                   (uint16_t)kPORT_PassiveFilterDisable,
                                                   /* Open drain output is disabled */
                                                   (uint16_t)kPORT_OpenDrainDisable,
                                                   /* Low drive strength is configured */
                                                   (uint16_t)kPORT_LowDriveStrength,
                                                   /* Normal drive strength is configured */
                                                   (uint16_t)kPORT_NormalDriveStrength,
                                                   /* Pin is configured as LPUART1_TX */
                                                   (uint16_t)kPORT_MuxAlt3,
                                                   /* Pin Control Register fields [15:0] are not locked */
                                                   (uint16_t)kPORT_UnlockRegister};
    /* PORTC3 (pin 40) is configured as LPUART1_TX */
    PORT_SetPinConfig(BOARD_INITPINS_UART_TX_PORT, BOARD_INITPINS_UART_TX_PIN, &UART_TX);

    /* SW2 is input */
    gpio_pin_config_t SW2_config = {
        .pinDirection = kGPIO_DigitalInput,
        .outputLogic = 0U
    };

    GPIO_PinInit(BOARD_INITPINS_SW2_GPIO, BOARD_INITPINS_SW2_PIN, &SW2_config);

    const port_pin_config_t SW2 = {/* Internal pull-up resistor is enabled */
                                   (uint16_t)kPORT_PullUp,
                                   /* Low internal pull resistor value is selected. */
                                   (uint16_t)kPORT_LowPullResistor,
                                   /* Fast slew rate is configured */
                                   (uint16_t)kPORT_FastSlewRate,
                                   /* Passive input filter is disabled */
                                   (uint16_t)kPORT_PassiveFilterDisable,
                                   /* Open drain output is disabled */
                                   (uint16_t)kPORT_OpenDrainDisable,
                                   /* Low drive strength is configured */
                                   (uint16_t)kPORT_LowDriveStrength,
                                   /* Normal drive strength is configured */
                                   (uint16_t)kPORT_NormalDriveStrength,
                                   /* Pin is configured as PTD3 */
                                   (uint16_t)kPORT_MuxAsGpio,
                                   /* Pin Control Register fields [15:0] are not locked */
                                   (uint16_t)kPORT_UnlockRegister};

    /* Initialize GPIO functionality on pin PTC6 (pin 44)  */
    PORT_SetPinConfig(BOARD_INITPINS_SW2_PORT, BOARD_INITPINS_SW2_PIN, &SW2);

}

void BOARD_RedefineSW1() {
    /* SW1 is input */
    gpio_pin_config_t SW1_config = {
        .pinDirection = kGPIO_DigitalInput,
        .outputLogic = 0U
    };
    GPIO_PinInit(BOARD_INITPINS_SW1_GPIO, BOARD_INITPINS_SW1_PIN, &SW1_config);

    const port_pin_config_t SW1 = {/* Internal pull-up resistor is enabled */
                                   (uint16_t)kPORT_PullUp,
                                   /* Low internal pull resistor value is selected. */
                                   (uint16_t)kPORT_LowPullResistor,
                                   /* Fast slew rate is configured */
                                   (uint16_t)kPORT_FastSlewRate,
                                   /* Passive input filter is disabled */
                                   (uint16_t)kPORT_PassiveFilterDisable,
                                   /* Open drain output is disabled */
                                   (uint16_t)kPORT_OpenDrainDisable,
                                   /* Low drive strength is configured */
                                   (uint16_t)kPORT_LowDriveStrength,
                                   /* Normal drive strength is configured */
                                   (uint16_t)kPORT_NormalDriveStrength,
                                   /* Pin is configured as PTD4 */
                                   (uint16_t)kPORT_MuxAsGpio,
                                   /* Pin Control Register fields [15:0] are not locked */
                                   (uint16_t)kPORT_UnlockRegister};

    /* Initialize GPIO functionality on pin PTA4 */
    PORT_SetPinConfig(BOARD_INITPINS_SW1_PORT, BOARD_INITPINS_SW1_PIN, &SW1);

}
/***********************************************************************************************************************
 * EOF
 **********************************************************************************************************************/
