// SPDX-License-Identifier: Apache-2.0
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

// Initialises the 1-Wire bus + DS18B20 driver, then spawns a FreeRTOS task
// that samples the sensor periodically and pushes filtered values into the
// Matter TemperatureMeasurement cluster.
//
// Safe to call once Matter is up (g_temp_endpoint_id != 0); the task will
// also tolerate being started early — it just won't push until the endpoint
// is registered.
void ds18b20_task_start(void);

#ifdef __cplusplus
}
#endif
