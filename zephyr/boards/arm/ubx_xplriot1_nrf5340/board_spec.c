/*
 * u-blox XPLR-IOT-1 ubxlib board specific setup
 * Copyright (c) 2022 u-blox AG
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <string.h>
#include <drivers/uart.h>
#include <hal/nrf_gpio.h>
#include <hal/nrf_uarte.h>
#include <device.h>

#include "ubxlib.h"

#define NORA_EN_SARA_PIN     10  // Applies voltage rail to the Sara module
#define SARA_PWR_ON_PIN       9  // Applies POWER_ON Signal

#define NORA_EN_NINA_PIN      8  // Applies voltage rail to the Nina module
#define NORA_NINA_COM_EN_PIN 42  // Controls whether Uart Routes to NORA or USB UART bridge

#define NORA_EN_MAX_PIN       4  // Applies voltage rail to the Max10 module
#define NORA_MAX_COM_EN_PIN  47  // Controls whether Uart Routes to NORA or USB UART bridge

#define ALT_INT_PIN          32  // ALT_INT input(int) pin
#define SARA_INT_PIN         33  // SARA_INT/NINA_SW1 pin

/* Uart pins
* The limitations of the nrf53 makes it impossible to use
  all the needed 4 uarts when also using I2c. Therefore the
  Nina and and Sara modules can not be connected to the Nora at
  the same time if i2c is enabled. The workaround implemented
  here is to change the pins on uart #2 in order to connect
  it to either the Sara or the Nina.

*/
#define SARA_SEC_UART_RX     40
#define SARA_SEC_UART_TX     36
#define SARA_SEC_UART_CTS    38
#define SARA_SEC_UART_RTS    19

#define NINA_UART_RX         43
#define NINA_UART_TX         31
#define NINA_UART_CTS        30
#define NINA_UART_RTS        20


static bool gI2cEnabled = false;
static bool gUart2Used = false;

static bool setupSharedUart(bool sara) {
  // Setup uart #2 to the specified module unless it is already in use
  bool ok = false;
  if (!gI2cEnabled) {
    // Not needed
    ok = true;
  } else if (!gUart2Used) {
    int txPin = sara ? SARA_SEC_UART_TX : NINA_UART_TX;
    int rxPin = sara ? SARA_SEC_UART_RX : NINA_UART_RX;
    int ctsPin = sara ? SARA_SEC_UART_CTS : NINA_UART_CTS;
    int rtsPin = sara ? SARA_SEC_UART_RTS : NINA_UART_RTS;
    nrf_uarte_disable(NRF_UARTE2_S);
    nrf_gpio_pin_set(txPin);
    nrf_gpio_cfg_output(txPin);
    nrf_gpio_cfg_input(rxPin, NRF_GPIO_PIN_NOPULL);
    nrf_uarte_txrx_pins_set(NRF_UARTE2_S, txPin, rxPin);
    nrf_gpio_cfg_input(ctsPin, NRF_GPIO_PIN_NOPULL);
    nrf_gpio_pin_set(rtsPin);
    nrf_gpio_cfg_output(rtsPin);
    nrf_uarte_hwfc_pins_set(NRF_UARTE2_S, rtsPin, ctsPin);
    nrf_uarte_enable(NRF_UARTE2_S);
    nrf_uarte_task_trigger(NRF_UARTE2_S, NRF_UARTE_TASK_STARTRX);
    gUart2Used = true;
    ok = true;
  }
  return ok;
}

int32_t uDeviceCallback(const char *pOperationType,
                        void *pOperationParam1,
                        void *pOperationParam2) {
  int32_t errorCode = U_ERROR_COMMON_INVALID_PARAMETER;

  if (strstr(pOperationType, "init")) {
    const struct device *i2cDev = device_get_binding("I2C_1");
    gI2cEnabled = i2cDev != NULL && i2cDev->state->initialized;
    errorCode = U_ERROR_COMMON_SUCCESS;
    // Reclaim net core uart0 pins, for use by the app core.
    nrf_gpio_pin_mcu_select(NORA_EN_SARA_PIN, NRF_GPIO_PIN_MCUSEL_APP);
    nrf_gpio_pin_mcu_select(ALT_INT_PIN, NRF_GPIO_PIN_MCUSEL_APP);
    nrf_gpio_pin_mcu_select(SARA_INT_PIN, NRF_GPIO_PIN_MCUSEL_APP);

  } else if (strstr(pOperationType, "deinit")) {
    errorCode = U_ERROR_COMMON_SUCCESS;
  } else if (strstr(pOperationType, "def")) {
    // Set defaults
    uDeviceCfg_t *pDeviceCfg = (uDeviceCfg_t *)pOperationParam1;
    switch (pDeviceCfg->deviceType) {
      case U_DEVICE_TYPE_CELL:
        pDeviceCfg->deviceCfg.cfgCell.moduleType = U_CELL_MODULE_TYPE_SARA_R5;
        pDeviceCfg->deviceCfg.cfgCell.pinEnablePower = NORA_EN_SARA_PIN;
        pDeviceCfg->deviceCfg.cfgCell.pinPwrOn = SARA_PWR_ON_PIN | U_CELL_PIN_INVERTED;
        pDeviceCfg->transportCfg.cfgUart.uart = gI2cEnabled ? 2 : 1;
        errorCode = U_ERROR_COMMON_SUCCESS;
        break;

      case U_DEVICE_TYPE_SHORT_RANGE:
        pDeviceCfg->deviceCfg.cfgSho.moduleType = U_SHORT_RANGE_MODULE_TYPE_NINA_W15;
        pDeviceCfg->transportCfg.cfgUart.uart = 2;
        errorCode = U_ERROR_COMMON_SUCCESS;
        break;

      case U_DEVICE_TYPE_GNSS:
        pDeviceCfg->deviceCfg.cfgGnss.moduleType = U_GNSS_MODULE_TYPE_M9;
        pDeviceCfg->deviceCfg.cfgGnss.pinEnablePower = NORA_EN_MAX_PIN;
        pDeviceCfg->transportCfg.cfgUart.uart = 3;
        errorCode = U_ERROR_COMMON_SUCCESS;
        break;

      default:
        break;
    }
  } else if (strstr(pOperationType, "open")) {
    // Do necessary enabling of the device
    switch ((uDeviceType_t)pOperationParam1) {
      case U_DEVICE_TYPE_CELL:
        // All enabling is handled in ubxlib
        // but do possible uart redefinition
        if (setupSharedUart(true)) {
          errorCode = U_ERROR_COMMON_SUCCESS;
        }
        break;

      case U_DEVICE_TYPE_SHORT_RANGE:
        if (setupSharedUart(false)) {
          // Enable power and connection to the uart
          nrf_gpio_cfg_output(NORA_EN_NINA_PIN);
          nrf_gpio_cfg_output(NORA_NINA_COM_EN_PIN);
          nrf_gpio_pin_set(NORA_EN_NINA_PIN);
          nrf_gpio_pin_set(NORA_NINA_COM_EN_PIN);
          errorCode = U_ERROR_COMMON_SUCCESS;
        }
        break;

      case U_DEVICE_TYPE_GNSS:
        // Enable connection to the uart
        nrf_gpio_cfg_output(NORA_MAX_COM_EN_PIN);
        nrf_gpio_pin_set(NORA_MAX_COM_EN_PIN);
        errorCode = U_ERROR_COMMON_SUCCESS;
        break;

      default:
        break;
    }
  } else if (strstr(pOperationType, "close")) {
    // Close down the device with possible power off
    switch ((uDeviceType_t)pOperationParam1) {
      case U_DEVICE_TYPE_CELL:
        gUart2Used = false;
        errorCode = U_ERROR_COMMON_SUCCESS;
        break;

      case U_DEVICE_TYPE_SHORT_RANGE:
        if (pOperationParam2 != NULL) {
          nrf_gpio_pin_clear(NORA_EN_NINA_PIN);
        }
        gUart2Used = false;
        errorCode = U_ERROR_COMMON_SUCCESS;
        break;

      case U_DEVICE_TYPE_GNSS:
        errorCode = U_ERROR_COMMON_SUCCESS;
        break;

      default:
        break;
    }
  }
  return errorCode;
}
