# u-blox MINI-NORA-B10 board configuration

# Copyright (c) 2021 u-blox AG
# SPDX-License-Identifier: Apache-2.0

if ((CONFIG_BOARD_UBX_MININORAB10_NRF5340_CPUAPP OR CONFIG_BOARD_UBX_MININORAB10_NRF5340_CPUAPPNS)
    AND CONFIG_BOARD_ENABLE_CPUNET)
zephyr_library()
zephyr_library_sources(nrf5340_cpunet_reset.c)
endif()
