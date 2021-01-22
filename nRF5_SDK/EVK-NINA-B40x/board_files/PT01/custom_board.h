/**
 * Copyright (c) 2019, Nordic Semiconductor ASA
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

Modified by u-blox 2019

*/

#ifndef CUSTOM_BOARD_H
#define CUSTOM_BOARD_H

#ifdef __cplusplus
extern "C" {
#endif

#include "nrf_gpio.h"

// In this file PIN 20 is used as button SWITCH_1, if the GREEN led
// should be used it is possible to define that one instead.
#define LEDS_NUMBER    2

#define LED_1          NRF_GPIO_PIN_MAP(0, 13)	// RED
#define LED_2          NRF_GPIO_PIN_MAP(1, 0)	// BLUE

#define LEDS_ACTIVE_STATE 0

#define LEDS_LIST { LED_1, LED_2 }

#define LEDS_INV_MASK  LEDS_MASK

#define BSP_LED_0      LED_1
#define BSP_LED_1      LED_2

#define BUTTONS_NUMBER 2

#define BUTTON_1       NRF_GPIO_PIN_MAP(0, 20)  // SWITCH_1	
#define BUTTON_2       NRF_GPIO_PIN_MAP(0, 2)  // SWITCH_2
#define BUTTON_PULL    NRF_GPIO_PIN_PULLUP

#define BUTTONS_ACTIVE_STATE 0

#define BUTTONS_LIST { BUTTON_1, BUTTON_2 }

#define BSP_BUTTON_0   BUTTON_1
#define BSP_BUTTON_1   BUTTON_2

#define RX_PIN_NUMBER NRF_GPIO_PIN_MAP(0, 29)
#define TX_PIN_NUMBER NRF_GPIO_PIN_MAP(1, 5)
#define CTS_PIN_NUMBER NRF_GPIO_PIN_MAP(1, 12)
#define RTS_PIN_NUMBER NRF_GPIO_PIN_MAP(0, 31)
#define HWFC           true


// Arduino board mappings
#define ARDUINO_SCL_PIN             24  // SCL signal pin
#define ARDUINO_SDA_PIN             16  // SDA signal pin

#define ARDUINO_13_PIN              NRF_GPIO_PIN_MAP(0, 7)
#define ARDUINO_12_PIN              NRF_GPIO_PIN_MAP(0, 2)
#define ARDUINO_11_PIN              NRF_GPIO_PIN_MAP(0, 15)
#define ARDUINO_10_PIN              NRF_GPIO_PIN_MAP(0, 14)
#define ARDUINO_9_PIN               NRF_GPIO_PIN_MAP(0, 12)
#define ARDUINO_8_PIN               NRF_GPIO_PIN_MAP(1, 9)

#define ARDUINO_7_PIN               NRF_GPIO_PIN_MAP(0, 10)
#define ARDUINO_6_PIN               NRF_GPIO_PIN_MAP(0, 9)
#define ARDUINO_5_PIN               NRF_GPIO_PIN_MAP(0, 11)
#define ARDUINO_4_PIN               NRF_GPIO_PIN_MAP(0, 13)
#define ARDUINO_3_PIN               NRF_GPIO_PIN_MAP(0, 31)
#define ARDUINO_2_PIN               NRF_GPIO_PIN_MAP(0, 23)
#define ARDUINO_1_PIN               NRF_GPIO_PIN_MAP(1, 5)
#define ARDUINO_0_PIN               NRF_GPIO_PIN_MAP(0, 29)

#define ARDUINO_A0_PIN              NRF_GPIO_PIN_MAP(0, 4)
#define ARDUINO_A1_PIN              NRF_GPIO_PIN_MAP(0, 30)
#define ARDUINO_A2_PIN              NRF_GPIO_PIN_MAP(0, 5)
#define ARDUINO_A3_PIN              NRF_GPIO_PIN_MAP(0, 2)
#define ARDUINO_A4_PIN              NRF_GPIO_PIN_MAP(0, 28)
#define ARDUINO_A5_PIN              NRF_GPIO_PIN_MAP(0, 3)

#define RASPBERRY_PI_3_PIN          NRF_GPIO_PIN_MAP(0, 24)
#define RASPBERRY_PI_5_PIN          NRF_GPIO_PIN_MAP(0, 16)
#define RASPBERRY_PI_7_PIN          NRF_GPIO_PIN_MAP(0, 15)
#define RASPBERRY_PI_11_PIN         NRF_GPIO_PIN_MAP(0, 14)
//#define RASPBERRY_PI_13_PIN         NRF_GPIO_PIN_MAP(0, 20)
#define RASPBERRY_PI_15_PIN         NRF_GPIO_PIN_MAP(0, 17)
#define RASPBERRY_PI_19_PIN         NRF_GPIO_PIN_MAP(0, 21)
#define RASPBERRY_PI_21_PIN         NRF_GPIO_PIN_MAP(0, 23)
#define RASPBERRY_PI_23_PIN         NRF_GPIO_PIN_MAP(0, 7)
#define RASPBERRY_PI_27_PIN         NRF_GPIO_PIN_MAP(0, 26)
#define RASPBERRY_PI_29_PIN         NRF_GPIO_PIN_MAP(0, 19)
//#define RASPBERRY_PI_31_PIN         NRF_GPIO_PIN_MAP(1, 11)
//#define RASPBERRY_PI_33_PIN         NRF_GPIO_PIN_MAP(1, 3)
#define RASPBERRY_PI_35_PIN         NRF_GPIO_PIN_MAP(1, 2)
#define RASPBERRY_PI_37_PIN         NRF_GPIO_PIN_MAP(1, 8)

#define RASPBERRY_PI_8_PIN          RX_PIN_NUMBER
#define RASPBERRY_PI_10_PIN         TX_PIN_NUMBER
#define RASPBERRY_PI_12_PIN         NRF_GPIO_PIN_MAP(0, 13)
#define RASPBERRY_PI_16_PIN         NRF_GPIO_PIN_MAP(0, 20)
#define RASPBERRY_PI_18_PIN         NRF_GPIO_PIN_MAP(0, 22)
#define RASPBERRY_PI_22_PIN         NRF_GPIO_PIN_MAP(0, 12)
#define RASPBERRY_PI_24_PIN         NRF_GPIO_PIN_MAP(0, 27)
#define RASPBERRY_PI_26_PIN         NRF_GPIO_PIN_MAP(0, 6)
#define RASPBERRY_PI_28_PIN         NRF_GPIO_PIN_MAP(1, 3)
#define RASPBERRY_PI_32_PIN         NRF_GPIO_PIN_MAP(0, 25)
#define RASPBERRY_PI_36_PIN         NRF_GPIO_PIN_MAP(1, 1)
#define RASPBERRY_PI_38_PIN         NRF_GPIO_PIN_MAP(1, 9)
#define RASPBERRY_PI_40_PIN         NRF_GPIO_PIN_MAP(0, 11)


#ifdef __cplusplus
}
#endif

#endif // CUSTOM_BOARD_H
