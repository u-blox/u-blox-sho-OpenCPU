/*
 * Copyright 2021 NXP
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
/*
 * Modified by u-blox 2023
*/
#ifndef _PIN_MUX_H_
#define _PIN_MUX_H_

/*!
 * @addtogroup pin_mux
 * @{
 */

/***********************************************************************************************************************
 * API
 **********************************************************************************************************************/

#if defined(__cplusplus)
extern "C" {
#endif

/*!
 * @brief Calls initialization functions.
 *
 */
void BOARD_InitBootPins(void);

/* Symbols to be used with GPIO driver. Red GPIO_1 */
#define BOARD_INITPINS_LED_RED_GPIO GPIOA                /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_LED_RED_PORT PORTA                /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_LED_RED_PIN 16U                /*!<@brief GPIO peripheral base pointer */
#define BOARD_INITPINS_LED_RED_PIN_MASK (1U << BOARD_INITPINS_LED_RED_PIN) /*!<@brief GPIO pin mask */

/* Symbols to be used with PORT driver Green GPIO_7  */
#define BOARD_INITPINS_LED_GREEN_GPIO GPIOA                /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_LED_GREEN_PORT PORTA                /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_LED_GREEN_PIN 4U                   /*!<@brief PORT pin number */
#define BOARD_INITPINS_LED_GREEN_PIN_MASK (1U << BOARD_INITPINS_LED_GREEN_PIN)      /*!<@brief PORT pin mask */

/* Symbols to be used with PORT driver. BLUE GPIO_8 */
#define BOARD_INITPINS_LED_BLUE_GPIO GPIOC                /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_LED_BLUE_PORT PORTC                /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_LED_BLUE_PIN 5U                   /*!<@brief PORT pin number */
#define BOARD_INITPINS_LED_BLUE_PIN_MASK (1U << BOARD_INITPINS_LED_BLUE_PIN)      /*!<@brief PORT pin mask */

/* Symbols to be used with PORT driver. SW2 GPIO_18 PTD3 */
#define BOARD_INITPINS_SW2_GPIO GPIOD               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_SW2_PORT PORTD               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_SW2_PIN 3U                   /*!<@brief PORT pin number */
#define BOARD_INITPINS_SW2_PIN_MASK (1U << BOARD_INITPINS_SW2_PIN)      /*!<@brief PORT pin mask */

/* Symbols to be used with PORT driver. SW1 GPIO_7 shared with Green LED */
#define BOARD_INITPINS_SW1_GPIO GPIOA               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_SW1_PORT PORTA               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_SW1_PIN 4U                   /*!<@brief PORT pin number */
#define BOARD_INITPINS_SW1_PIN_MASK (1U << BOARD_INITPINS_SW1_PIN)      /*!<@brief PORT pin mask */

/* Symbols to be used with PORT driver. UART RX GPIO_23 */
#define BOARD_INITPINS_UART_RX_GPIO GPIOC               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_UART_RX_PORT PORTC               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_UART_RX_PIN 2U                   /*!<@brief PORT pin number */
#define BOARD_INITPINS_UART_RX_PIN_MASK (1U << BOARD_INITPINS_UART_RX_PIN)      /*!<@brief PORT pin mask */

/* Symbols to be used with PORT driver. UART TX GPIO_22 */
#define BOARD_INITPINS_UART_TX_GPIO GPIOC               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_UART_TX_PORT PORTC               /*!<@brief PORT peripheral base pointer */
#define BOARD_INITPINS_UART_TX_PIN 3U                   /*!<@brief PORT pin number */
#define BOARD_INITPINS_UART_TX_PIN_MASK (1U << BOARD_INITPINS_UART_TX_PIN)      /*!<@brief PORT pin mask */

/*!
 * @brief Configures pin routing and optionally pin electrical features.
 *
 */
void BOARD_InitPins(void);

/* Setting GPIO_7  as input instead of using as LED control signal */
void BOARD_RedefineSW1();

#if defined(__cplusplus)
}
#endif

/*!
 * @}
 */
#endif /* _PIN_MUX_H_ */

/***********************************************************************************************************************
 * EOF
 **********************************************************************************************************************/
