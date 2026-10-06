# SPDX-License-Identifier: Apache-2.0

set(SRCS
    "app_main.cpp"
    "ds18b20_task.cpp"
)

# DS2482 Click board support (I2C-to-1-Wire bridge on MikroBUS 1).
# Activated by: idf.py -DAPP_USE_DS2482=1 build
# or from launcher: --clickboard
if(APP_USE_DS2482)
    list(APPEND SRCS "ds2482_onewire.cpp")
endif()

# HVAC Click board support — Sensirion SCD41 CO₂/T/RH on MikroBUS 1.
# Stage 2: full Matter Air Quality Sensor (device type 0x002C) with
# AirQuality, TemperatureMeasurement, RelativeHumidityMeasurement, and
# CarbonDioxideConcentrationMeasurement clusters.
# Activated by: idf.py -DAPP_USE_HVAC=1 build  (or launcher: --hvac)
# Mutually exclusive with --clickboard.
if(APP_USE_HVAC)
    list(APPEND SRCS "scd41_task.cpp")
endif()

idf_component_register(
    SRCS ${SRCS}
    INCLUDE_DIRS
        "."
    PRIV_REQUIRES
        nvs_flash
        driver
        esp_timer
        esp_matter
        esp_matter_console
        chip
        bt
        openthread
        mbedtls
        espressif__ds18b20
        espressif__onewire_bus
)

if(APP_USE_DS2482)
    target_compile_definitions(${COMPONENT_LIB} PUBLIC APP_USE_DS2482=1)
    message(STATUS "🔌 DS2482 I2C-to-1-Wire Click board mode (MikroBUS 1, OW_IO0)")
endif()

if(APP_USE_HVAC)
    target_compile_definitions(${COMPONENT_LIB} PUBLIC APP_USE_HVAC=1)
    message(STATUS "🌬️  HVAC Click — Matter Air Quality Sensor (SCD41 CO₂/T/RH on MikroBUS 1)")
endif()

if(APP_USE_HVAC AND APP_USE_DS2482)
    message(FATAL_ERROR "--hvac and --clickboard are mutually exclusive (one MikroBUS 1 socket)")
endif()
