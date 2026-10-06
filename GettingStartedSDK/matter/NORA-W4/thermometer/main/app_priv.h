// SPDX-License-Identifier: Apache-2.0
//
// Shared types between app_main.cpp and ds18b20_task.cpp.

#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// ---- Direct 1-Wire GPIO (default, RMT bit-bang) ----------------------------
// EVK-NORA-W40 J15.4 = NORA H9 = ESP32-C6 GPIO15.
// Pure GPIO pad: not a strapping pin, not USB, not UART0, not behind a DIP switch.
// Doubles as LED_BLUE on the EVK — the LED is just an indicator, the bus
// still works. If you want the bus completely clean, move to GPIO4 (J16.29).
#define APP_DS18B20_GPIO        15

// ---- DS2482 I2C-to-1-Wire Click board (MikroBUS 1) -------------------------
// MikroE "i2C 1-WIRE click" with DS2482-800 bridge.
// SDA = GPIO6 (B4/I2C_SDA), SCL = GPIO7 (A3/I2C_SCL) — native I2C + LP_I2C.
// Default I2C address 0x18 (all ADR jumpers in position 1 = GND).
// DS18B20 connected to OW_IO0 on the click board header (HD1 pin 1/2).
#define APP_DS2482_SDA          6
#define APP_DS2482_SCL          7
#define APP_DS2482_ADDR         0x18
#define APP_DS2482_CHANNEL      0       // OW_IO0

// ---- Sampling parameters ---------------------------------------------------
// Adaptive sampling: fast when temperature is changing, slow when stable.
// - On significant change (> FAST_THRESHOLD_C): switch to FAST period
// - After FAST_COUNT consecutive stable reads: ramp back to SLOW period
// This gives instant response (hot coffee → cold water in ~3 s) while
// saving battery during idle periods (room temp drifts → 60 s samples).
#define APP_SAMPLE_PERIOD_FAST_MS   3000      // 3 s — rapid change tracking
#define APP_SAMPLE_PERIOD_SLOW_MS   60000     // 60 s — idle/stable (production)
#define APP_FAST_THRESHOLD_C        0.5f      // °C change to trigger fast mode
#define APP_FAST_COUNT              5         // stable reads before slowing down
#define APP_REPORT_THRESHOLD_C      0.1f      // °C — only push to Matter on real change

// Re-send the value at least this often even when it has not moved, otherwise
// controllers (Apple Home in particular) mark a steady sensor unresponsive.
#define APP_MATTER_KEEPALIVE_MS     (240 * 60 * 1000)   // 4 h, 0 = off

// Endpoint id of the Matter Temperature Sensor (assigned in app_main.cpp).
extern uint16_t g_temp_endpoint_id;

#ifdef __cplusplus
}
#endif
