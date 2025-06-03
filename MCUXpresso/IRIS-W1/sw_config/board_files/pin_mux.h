/*
 * Copyright 2024 NXP
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 *
 * Modified by u-blox for IRIS-W1 2024
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

/*! @name GPIO_42 (coord G13), RGB_BLUE
  @{ */
/* Routed pin properties */
#define BOARD_INITPINS_RGB_BLUE_PERIPHERAL GPIO                    /*!<@brief Peripheral name */
#define BOARD_INITPINS_RGB_BLUE_SIGNAL PIO1                        /*!<@brief Signal name */
#define BOARD_INITPINS_RGB_BLUE_CHANNEL 10                         /*!<@brief Signal channel */
#define BOARD_INITPINS_RGB_BLUE_GPIO GPIO                          /*!<@brief GPIO peripheral base pointer */
#define BOARD_INITPINS_RGB_BLUE_GPIO_PIN 42U                       /*!<@brief GPIO pin number */
#define BOARD_INITPINS_RGB_BLUE_PORT 1U                            /*!<@brief PORT number */
#define BOARD_INITPINS_RGB_BLUE_PIN 10U                            /*!<@brief PORT pin number */
#define BOARD_INITPINS_RGB_BLUE_PIN_MASK (1U << 10U)               /*!<@brief PORT pin mask */
                                                                   /* @} */

/*! @name GPIO_43 (coord H12), RGB_GREEN
  @{ */
/* Routed pin properties */
#define BOARD_INITPINS_RGB_GREEN_PERIPHERAL GPIO                    /*!<@brief Peripheral name */
#define BOARD_INITPINS_RGB_GREEN_SIGNAL PIO1                        /*!<@brief Signal name */
#define BOARD_INITPINS_RGB_GREEN_CHANNEL 11                         /*!<@brief Signal channel */
#define BOARD_INITPINS_RGB_GREEN_GPIO GPIO                          /*!<@brief GPIO peripheral base pointer */
#define BOARD_INITPINS_RGB_GREEN_GPIO_PIN 43U                       /*!<@brief GPIO pin number */
#define BOARD_INITPINS_RGB_GREEN_PORT 1U                            /*!<@brief PORT number */
#define BOARD_INITPINS_RGB_GREEN_PIN 11U                            /*!<@brief PORT pin number */
#define BOARD_INITPINS_RGB_GREEN_PIN_MASK (1U << 11U)               /*!<@brief PORT pin mask */
                                                                    /* @} */

/*! @name GPIO_44 (coord J11), RGB_RED
  @{ */
/* Routed pin properties */
#define BOARD_INITPINS_RGB_RED_PERIPHERAL GPIO                    /*!<@brief Peripheral name */
#define BOARD_INITPINS_RGB_RED_SIGNAL PIO1                        /*!<@brief Signal name */
#define BOARD_INITPINS_RGB_RED_CHANNEL 12                         /*!<@brief Signal channel */
#define BOARD_INITPINS_RGB_RED_GPIO GPIO                          /*!<@brief GPIO peripheral base pointer */
#define BOARD_INITPINS_RGB_RED_GPIO_PIN 44U                       /*!<@brief GPIO pin number */
#define BOARD_INITPINS_RGB_RED_PORT 1U                            /*!<@brief PORT number */
#define BOARD_INITPINS_RGB_RED_PIN 12U                            /*!<@brief PORT pin number */
#define BOARD_INITPINS_RGB_RED_PIN_MASK (1U << 12U)               /*!<@brief PORT pin mask */
                                                                  /* @} */

/*! @name GPIO_45 (coord H10), SWITCH_1
  @{ */
/* Routed pin properties */
#define BOARD_INITPINS_SWITCH_1_PERIPHERAL GPIO                   /*!<@brief Peripheral name */
#define BOARD_INITPINS_SWITCH_1_SIGNAL PIO1                       /*!<@brief Signal name */
#define BOARD_INITPINS_SWITCH_1_CHANNEL 13                        /*!<@brief Signal channel */
#define BOARD_INITPINS_SWITCH_1_GPIO GPIO                         /*!<@brief GPIO peripheral base pointer */
#define BOARD_INITPINS_SWITCH_1_GPIO_PIN 45U                      /*!<@brief GPIO pin number */
#define BOARD_INITPINS_SWITCH_1_PORT 1U                           /*!<@brief PORT number */
#define BOARD_INITPINS_SWITCH_1_PIN 13U                           /*!<@brief PORT pin number */
#define BOARD_INITPINS_SWITCH_1_PIN_MASK (1U << 13U)              /*!<@brief PORT pin mask */
                                                                  /* @} */

/*! @name GPIO_51 (coord M8), SWITCH_2
  @{ */
/* Routed pin properties */
#define BOARD_INITPINS_SWITCH_2_PERIPHERAL GPIO                   /*!<@brief Peripheral name */
#define BOARD_INITPINS_SWITCH_2_SIGNAL PIO1                       /*!<@brief Signal name */
#define BOARD_INITPINS_SWITCH_2_CHANNEL 19                        /*!<@brief Signal channel */
#define BOARD_INITPINS_SWITCH_2_GPIO GPIO                         /*!<@brief GPIO peripheral base pointer */
#define BOARD_INITPINS_SWITCH_2_GPIO_PIN 51U                      /*!<@brief GPIO pin number */
#define BOARD_INITPINS_SWITCH_2_PORT 1U                           /*!<@brief PORT number */
#define BOARD_INITPINS_SWITCH_2_PIN 19U                           /*!<@brief PORT pin number */
#define BOARD_INITPINS_SWITCH_2_PIN_MASK (1U << 19U)              /*!<@brief PORT pin mask */
                                                                  /* @} */

/*!
 * @brief 
 *
 */
void BOARD_InitPins(void); /* Function assigned for the Cortex-M33 */

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
