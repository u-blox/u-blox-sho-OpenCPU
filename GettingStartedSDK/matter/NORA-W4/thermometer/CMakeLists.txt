# SPDX-License-Identifier: Apache-2.0
# NORA-W4 (ESP32-C6) single-SoC Matter Thermometer.
#
# Ported from u-connectMatter companion/endnode/nora-w40-thermometer.
# Modelled on esp-matter/examples/light/CMakeLists.txt. Built by build.sh,
# which sources export.sh from ESP-IDF v5.5.5 and esp-matter release/v1.5.

cmake_minimum_required(VERSION 3.16)

# --- esp-matter prerequisites -------------------------------------------------

if(NOT DEFINED ENV{ESP_MATTER_PATH})
    message(FATAL_ERROR
        "ESP_MATTER_PATH is not set. Build with: ubx-matter nora-w4 --build thermometer")
endif()

# Per-chip device HAL path (drives BSP, default pins, etc).
if(NOT DEFINED ENV{ESP_MATTER_DEVICE_PATH})
    if("${IDF_TARGET}" STREQUAL "esp32c6" OR "${IDF_TARGET}" STREQUAL "")
        set(ENV{ESP_MATTER_DEVICE_PATH} $ENV{ESP_MATTER_PATH}/device_hal/device/esp32c6_devkit_c)
    elseif("${IDF_TARGET}" STREQUAL "esp32h2")
        set(ENV{ESP_MATTER_DEVICE_PATH} $ENV{ESP_MATTER_PATH}/device_hal/device/esp32h2_devkit_c)
    else()
        message(FATAL_ERROR "Unsupported IDF_TARGET '${IDF_TARGET}' for NORA-W40 thermometer.")
    endif()
endif()

set(PROJECT_VER "3.4.0")
set(PROJECT_VER_NUMBER 3)

set(ESP_MATTER_PATH $ENV{ESP_MATTER_PATH})
set(MATTER_SDK_PATH ${ESP_MATTER_PATH}/connectedhomeip/connectedhomeip)

# --- IDF + esp-matter project glue --------------------------------------------

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
include(${ESP_MATTER_PATH}/examples/common/cmake_common/components_include.cmake)
include($ENV{ESP_MATTER_DEVICE_PATH}/esp_matter_device.cmake)

set(EXTRA_COMPONENT_DIRS
    "${ESP_MATTER_PATH}/examples/common"
    "${MATTER_SDK_PATH}/config/esp32/components"
    "${ESP_MATTER_PATH}/components"
    "${ESP_MATTER_PATH}/device_hal/device"
    ${extra_components_dirs_append})

project(u-connect-matter-thermometer)

# Match esp-matter example compile flags (C++17, size-optimised, suppress
# noisy upstream warnings on RISC-V).
idf_build_set_property(CXX_COMPILE_OPTIONS "-std=gnu++17;-Os;-DCHIP_HAVE_CONFIG_H;-Wno-overloaded-virtual" APPEND)
idf_build_set_property(C_COMPILE_OPTIONS "-Os" APPEND)
idf_build_set_property(COMPILE_OPTIONS "-Wno-format-nonliteral;-Wno-format-security" APPEND)
