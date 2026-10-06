// SPDX-License-Identifier: Apache-2.0
//
// SCD41 (CO₂ / temperature / humidity) FreeRTOS task — feeds Matter clusters.
//
// Hardware: MikroE HVAC Click in EVK-NORA-W40 MikroBUS 1 socket.
//   SDA=GPIO6  SCL=GPIO7  I²C addr=0x62  VCC SEL jumper = 3V3.
//
// On start: opens I²C, wakes the SCD41, runs the 10 s on-chip self-test,
// then enters periodic measurement at 5 s cadence. Every successful sample
// is pushed into 4 Matter attributes on the air-quality endpoint via
// esp_matter::attribute::update():
//
//   AirQuality.AirQuality                         (cluster 0x005B)
//   TemperatureMeasurement.MeasuredValue          (cluster 0x0402)
//   RelativeHumidityMeasurement.MeasuredValue     (cluster 0x0405)
//   CarbonDioxideConcentrationMeasurement.        (cluster 0x040D)
//       MeasuredValue
//
// Stage 1 of the HVAC variant was probe-only (no Matter); this is stage 2.

#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/// Start the SCD41 sampling task. Call AFTER esp_matter::start() and AFTER
/// the air-quality endpoint has been created (so endpoint_id is valid).
/// @param endpoint_id  the Matter endpoint that hosts the SCD41 clusters.
/// @return 0 on success, negative on failure.
int scd41_task_start(uint16_t endpoint_id);

#ifdef __cplusplus
}
#endif
