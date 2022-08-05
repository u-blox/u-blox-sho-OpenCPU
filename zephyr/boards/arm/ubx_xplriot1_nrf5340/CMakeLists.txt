# u-blox XPLR-IOT-1 board configuration

# Copyright (c) 2022 u-blox AG
# SPDX-License-Identifier: Apache-2.0

if ((CONFIG_BOARD_UBX_XPLRIOT1_NRF5340_CPUAPP OR CONFIG_BOARD_UBX_XPLRIOT1_NRF5340_CPUAPP_NS)
    AND CONFIG_BOARD_ENABLE_CPUNET)
  zephyr_library()
  zephyr_library_sources(nrf5340_cpunet_reset.c)
  # Explicit definition of littlefs  external flash partition needed when multi image build
  set(PM_STATIC_YML_FILE ${CMAKE_CURRENT_LIST_DIR}/lfs_ext_flash.yml CACHE INTERNAL "")
endif()
