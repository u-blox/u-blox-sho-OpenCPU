/**
 * Copyright (c) 2014 - 2020, Nordic Semiconductor ASA
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form, except as embedded into a Nordic
 *    Semiconductor ASA integrated circuit in a product or a software update for
 *    such product, must reproduce the above copyright notice, this list of
 *    conditions and the following disclaimer in the documentation and/or other
 *    materials provided with the distribution.
 *
 * 3. Neither the name of Nordic Semiconductor ASA nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 *
 * 4. This software, with or without modification, must only be used with a
 *    Nordic Semiconductor ASA integrated circuit.
 *
 * 5. Any software provided in binary form under this license must not be reverse
 *    engineered, decompiled, modified and/or disassembled.
 *
 * THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

/**

Modified by u-blox 2020

*/

#ifndef BOARD_CUSTOM_H
#define BOARD_CUSTOM_H

#ifdef __cplusplus
extern "C" {
#endif

#include "nrf_gpio.h"

// In this case PIN 16 is used as button SW1, if the green led
// should be used it is possible to defined that one instead.
#define LEDS_NUMBER    2

#define LED_1          8	// Red
#define LED_2          18	// Blue
#define LED_3          16	// Green/SW1 button


#define LEDS_ACTIVE_STATE 0

#define LEDS_LIST { LED_1, LED_2 }

#define BSP_LED_0      LED_1
#define BSP_LED_1      LED_2

#define LEDS_INV_MASK  LEDS_MASK

#define BUTTONS_NUMBER 2

#define BUTTON_1       16	// SW1
#define BUTTON_2       30	// SW2
#define BUTTON_PULL    NRF_GPIO_PIN_PULLUP

#define BUTTONS_ACTIVE_STATE 0

#define BUTTONS_LIST { BUTTON_1, BUTTON_2 }

#define BSP_BUTTON_0   BUTTON_1
#define BSP_BUTTON_1   BUTTON_2

#define RX_PIN_NUMBER  5
#define TX_PIN_NUMBER  6
#define CTS_PIN_NUMBER 7
#define RTS_PIN_NUMBER 31
#define HWFC           true

#define SPIS_MISO_PIN   12  // SPI MISO signal.
#define SPIS_CSN_PIN    11  // SPI CSN signal.
#define SPIS_MOSI_PIN   13  // SPI MOSI signal.
#define SPIS_SCK_PIN    14  // SPI SCK signal.

#define SPIM0_SCK_PIN   14  // SPI clock GPIO pin number.
#define SPIM0_MOSI_PIN  13  // SPI Master Out Slave In GPIO pin number.
#define SPIM0_MISO_PIN  12  // SPI Master In Slave Out GPIO pin number.
#define SPIM0_SS_PIN    11  // SPI Slave Select GPIO pin number.

// Arduino board mappings
#define ARDUINO_SCL_PIN              3  // SCL signal pin (IO_25)
#define ARDUINO_SDA_PIN              2  // SDA signal pin (IO_24)

// Connector J4
#define ARDUINO_13_PIN              NRF_GPIO_PIN_MAP(0, 14)  // IO_5
#define ARDUINO_12_PIN              NRF_GPIO_PIN_MAP(0, 12)  // IO_3
#define ARDUINO_11_PIN              NRF_GPIO_PIN_MAP(0, 13)  // IO_4
#define ARDUINO_10_PIN              NRF_GPIO_PIN_MAP(0, 11)  // IO_2
#define ARDUINO_9_PIN               NRF_GPIO_PIN_MAP(0, 8)   // IO_1
//#define ARDUINO_8_PIN                                      // IO_11, SWDCLK

// Connector J3
#define ARDUINO_7_PIN               NRF_GPIO_PIN_MAP(0, 10)  // IO_29
#define ARDUINO_6_PIN               NRF_GPIO_PIN_MAP(0, 9)   // IO_28
//#define ARDUINO_5_PIN                                      // IO_15, SWDIO
#define ARDUINO_4_PIN               NRF_GPIO_PIN_MAP(0, 18)  // IO_8, SWO
#define ARDUINO_3_PIN               NRF_GPIO_PIN_MAP(0, 31)  // UART_RTS
#define ARDUINO_2_PIN               NRF_GPIO_PIN_MAP(0, 7)   // UART_CTS
#define ARDUINO_1_PIN               NRF_GPIO_PIN_MAP(0, 6)   // UART_TXD
#define ARDUINO_0_PIN               NRF_GPIO_PIN_MAP(0, 5)   // UART_RXD

// Connector J2
#define ARDUINO_A0_PIN              NRF_GPIO_PIN_MAP(0, 3)   // IO_25
#define ARDUINO_A1_PIN              NRF_GPIO_PIN_MAP(0, 2)   // IO_24
#define ARDUINO_A2_PIN              NRF_GPIO_PIN_MAP(0, 4)   // IO_27
#define ARDUINO_A3_PIN              NRF_GPIO_PIN_MAP(0, 30)  // IO_18
#define ARDUINO_A4_PIN              NRF_GPIO_PIN_MAP(0, 29)  // IO_17, UART_DSR
#define ARDUINO_A5_PIN              NRF_GPIO_PIN_MAP(0, 28)  // IO_16, UART_DTR

// Low frequency clock source to be used by the SoftDevice
#define NRF_CLOCK_LFCLKSRC      {.source        = NRF_CLOCK_LF_SRC_XTAL,            \
                                 .rc_ctiv       = 0,                                \
                                 .rc_temp_ctiv  = 0,                                \
                                 .xtal_accuracy = NRF_CLOCK_LF_XTAL_ACCURACY_20_PPM}

#ifdef __cplusplus
}
#endif

#endif // BOARD_CUSTOM_H
