// SPDX-License-Identifier: Apache-2.0
//
// DS2482-800 I2C-to-1-Wire bridge driver for MikroE "i2C 1-WIRE click" board.
// Provides DS18B20 temperature reading over I2C instead of direct GPIO bit-bang.
//
// Hardware: DS2482-800 on MikroBUS 1 of EVK-NORA-W40
//   SDA = GPIO6  (B4/I2C_SDA)
//   SCL = GPIO7  (A3/I2C_SCL)
//   Default I2C address: 0x18 (all ADR jumpers to GND)
//   DS18B20 on any OW_IOx channel (default: OW_IO0)

#pragma once

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/// Initialize DS2482-800 on I2C bus and verify DS18B20 presence.
/// @param sda       SDA GPIO number (6 for MikroBUS 1)
/// @param scl       SCL GPIO number (7 for MikroBUS 1)
/// @param i2c_addr  7-bit I2C address (0x18 default)
/// @param channel   1-Wire channel 0-7 (which OW_IOx the DS18B20 is on)
esp_err_t ds2482_init(int sda, int scl, uint8_t i2c_addr, uint8_t channel);

/// Read temperature from DS18B20 via DS2482.
/// Blocks ~250 ms for 10-bit conversion (was 800 ms @ 12-bit before
/// the battery-life-tuned default; resolution is 0.25 °C, well within
/// the DS18B20's own ±0.5 °C accuracy spec).
/// @param[out] celsius  temperature in degrees Celsius
esp_err_t ds2482_read_temperature(float *celsius);

#ifdef __cplusplus
}
#endif
