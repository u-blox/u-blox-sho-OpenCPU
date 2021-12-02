/**
 * Copyright (c) 2019 - 2020, Nordic Semiconductor ASA
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

 Modified by u-blox 2021

*/

#ifndef EVK_ANNA_B4_H
#define EVK_ANNA_B4_H

#ifdef __cplusplus
extern "C" {
#endif

#include "nrf_gpio.h"

// LEDs definitions for EVK ANNA-B4
#define LEDS_NUMBER    2

// In this case PIN 6 is used as button SW1, if the green led
// should be used it is possible to define that one instead.
#define LED_1          NRF_GPIO_PIN_MAP(0,27) /* Red */
#define LED_2          NRF_GPIO_PIN_MAP(0,26) /* Blue */
#define LED_3          NRF_GPIO_PIN_MAP(0,6)  /* Green/SW1 */

#define LED_START      LED_1
#define LED_STOP       LED_2

#define LEDS_ACTIVE_STATE 0

#define LEDS_LIST { LED_1, LED_2 }

#define LEDS_INV_MASK  LEDS_MASK

#define BSP_LED_0      LED_1
#define BSP_LED_1      LED_2
//#define BSP_LED_2      LED_3

#define BUTTONS_NUMBER 2

#define BUTTON_1       6 /* SW1/Green LED */
#define BUTTON_2       15 /* SW2 */

#define BUTTON_PULL    NRF_GPIO_PIN_PULLUP

#define BUTTONS_ACTIVE_STATE 0

#define BUTTONS_LIST { BUTTON_1, BUTTON_2 }

#define BSP_BUTTON_0   BUTTON_1
#define BSP_BUTTON_1   BUTTON_2

#define RX_PIN_NUMBER  2
#define TX_PIN_NUMBER  3
#define CTS_PIN_NUMBER 22
#define RTS_PIN_NUMBER 16
#define HWFC           true


// Arduino board mappings
#define ARDUINO_SCL_PIN             NRF_GPIO_PIN_MAP(0, 12)  // SCL signal pin
#define ARDUINO_SDA_PIN             NRF_GPIO_PIN_MAP(0, 11)  // SDA signal pin
#define ARDUINO_AREF_PIN            NRF_GPIO_PIN_MAP(0, 8)   // AREF pin

#define ARDUINO_13_PIN              NRF_GPIO_PIN_MAP(0, 7)   // Digital pin 13
#define ARDUINO_12_PIN              NRF_GPIO_PIN_MAP(1, 0)   // Digital pin 12
#define ARDUINO_11_PIN              NRF_GPIO_PIN_MAP(0, 23)  // Digital pin 11
#define ARDUINO_10_PIN              NRF_GPIO_PIN_MAP(0, 19)  // Digital pin 10
#define ARDUINO_9_PIN               NRF_GPIO_PIN_MAP(0, 15)  // Digital pin 9
#define ARDUINO_8_PIN               NRF_GPIO_PIN_MAP(1, 9)   // Digital pin 8

#define ARDUINO_7_PIN               NRF_GPIO_PIN_MAP(0, 9)   // Digital pin 7
#define ARDUINO_6_PIN               NRF_GPIO_PIN_MAP(0, 10)  // Digital pin 6
#define ARDUINO_5_PIN               NRF_GPIO_PIN_MAP(0, 26)  // Digital pin 5
#define ARDUINO_4_PIN               NRF_GPIO_PIN_MAP(0, 27)  // Digital pin 4
#define ARDUINO_3_PIN               NRF_GPIO_PIN_MAP(0, 16)  // Digital pin 3
#define ARDUINO_2_PIN               NRF_GPIO_PIN_MAP(0, 22)  // Digital pin 2
#define ARDUINO_1_PIN               NRF_GPIO_PIN_MAP(0, 3)   // Digital pin 1
#define ARDUINO_0_PIN               NRF_GPIO_PIN_MAP(0, 2)   // Digital pin 0

#define ARDUINO_A0_PIN              5     // Analog channel 0
#define ARDUINO_A1_PIN              4     // Analog channel 1
#define ARDUINO_A2_PIN              28    // Analog channel 2
#define ARDUINO_A3_PIN              29    // Analog channel 3
#define ARDUINO_A4_PIN              30    // Analog channel 4
#define ARDUINO_A5_PIN              31    // Analog channel 5


#ifdef __cplusplus
}
#endif

#endif // EVK_ANNA_B4_H
