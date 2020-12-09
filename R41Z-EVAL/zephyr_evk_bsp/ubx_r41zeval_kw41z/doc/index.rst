.. _ubx_r41zeval_kw41z:

u-blox EVK-R41Z: R41Z-EVAL
##########################

Overview
********

The u-blox R41Z evaluation kit provides a great starting point for almost any 
Bluetooth low energy, Thread, or Zigbee project. All the features of 
the R41Z module are easily accessed from the evaluation board.   

A simple USB connection provides power and OpenSDA v2.1 based debugging. 
Four user buttons (two conventional and two capacitive) are available,
as well as an RGB LED, reset button, combination acceleration/magnetometer 
sensor, and an external 4 Mbit flash module. Arduino form factor headers 
provide access to 16 GPIO and 6 analog inputs. This allows for easy use 
of the many existing Arduino shields. Current sense resistors allow for 
measuring current into the R41Z module and into the shield.

.. image:: ./img/R41Z-EVAL_rendering_90.png
   :width: 400px
   :align: center
   :alt: R41Z-EVAL

Hardware
********

- Supports all DC-DC configurations (Buck, Boost, Bypass)
- Inverted F-type antenna on R41Z module
- RF regulatory certified
- Serial Flash for OTA firmware upgrades
- On board NXP FXOS8700CQ digital sensor, 3D Accelerometer ( |plusminus| 2g/
  |plusminus| 4g/ |plusminus| 8g) + 3D
  Magnetometer
- OpenSDA and JTAG debug

The R41Z-EVAL is functionally equivalent to the FRDM-KW41Z EVK from NXP. All 
of the examples for the FRDM-KW41Z may be used on the R41Z-EVAL without 
modification.

See the `u-blox website`_ more information about the R41Z and R41Z-EVAL board.


Supported Features
==================

The R41Z-EVAL board configuration supports the following hardware features:

+-----------+------------+-------------------------------------+
| Interface | Controller | Driver/Component                    |
+===========+============+=====================================+
| NVIC      | on-chip    | nested vector interrupt controller  |
+-----------+------------+-------------------------------------+
| SYSTICK   | on-chip    | systick                             |
+-----------+------------+-------------------------------------+
| PINMUX    | on-chip    | pinmux                              |
+-----------+------------+-------------------------------------+
| COUNTER   | on-chip    | rtc                                 |
+-----------+------------+-------------------------------------+
| GPIO      | on-chip    | gpio                                |
+-----------+------------+-------------------------------------+
| I2C       | on-chip    | i2c                                 |
+-----------+------------+-------------------------------------+
| SPI       | on-chip    | spi                                 |
+-----------+------------+-------------------------------------+
| ADC       | on-chip    | adc                                 |
+-----------+------------+-------------------------------------+
| UART      | on-chip    | serial port-polling;                |
|           |            | serial port-interrupt               |
+-----------+------------+-------------------------------------+
| FLASH     | on-chip    | soc flash                           |
+-----------+------------+-------------------------------------+
| SENSOR    | off-chip   | fxos8700 polling:                   |
|           |            | fxos8700 trigger                    |
+-----------+------------+-------------------------------------+
| PWM       | on-chip    | tpm                                 |
+-----------+------------+-------------------------------------+

The default configuration can be found in the defconfig file:

	``boards/arm/ubx_r41zeval_kw41z/ubx_r41zeval_kw41z_defconfig``

Other hardware features are not currently supported by the port.

Connections and IOs
===================

The KW41Z SoC within the R41Z module has three pairs of pinmux/gpio 
controllers, but only two are currently enabled (PORTA/GPIOA and 
PORTC/GPIOC) for the R41Z-EVAL board.

+-------+-------------+---------------------------+
| Name  | Function    | Usage                     |
+=======+=============+===========================+
| PTC1  | GPIO        | Red LED / FXOS8700 INT1   |
+-------+-------------+---------------------------+
| PTA19 | GPIO        | Green LED                 |
+-------+-------------+---------------------------+
| PTA18 | GPIO        | Blue LED                  |
+-------+-------------+---------------------------+
| PTB2  | ADC         | ADC0 channel 3            |
+-------+-------------+---------------------------+
| PTC2  | I2C1_SCL    | I2C / FXOS8700            |
+-------+-------------+---------------------------+
| PTC3  | I2C1_SDA    | I2C / FXOS8700            |
+-------+-------------+---------------------------+
| PTC4  | GPIO        | SW3                       |
+-------+-------------+---------------------------+
| PTC5  | GPIO        | SW4                       |
+-------+-------------+---------------------------+
| PTC6  | LPUART0_RX  | UART Console              |
+-------+-------------+---------------------------+
| PTC7  | LPUART0_TX  | UART Console              |
+-------+-------------+---------------------------+
| PTC16 | SPI0_SCK    | SPI                       |
+-------+-------------+---------------------------+
| PTC17 | SPI0_SOUT   | SPI                       |
+-------+-------------+---------------------------+
| PTC18 | SPI0_SIN    | SPI                       |
+-------+-------------+---------------------------+
| PTC19 | SPI0_PCS0   | SPI                       |
+-------+-------------+---------------------------+

.. image:: ./img/R41Z_EVAL_PinOut_vA.png
   :width: 800px
   :align: center
   :alt: R41Z-EVAL pin out

System Clock
============

The KW41Z SoC within the R41Z module is configured to use the 32 MHz external 
oscillator on the board with the on-chip FLL to generate a 40 MHz system clock.

Serial Port
===========

The KW41Z SoC within the R41Z module has one UART, which is used for the console.

Programming and Debugging
*************************

Build and flash applications as usual (see :ref:`build_an_application` and
:ref:`application_run` for more details).

Configuring a Debug Probe
=========================

The R41Z-EVAL utilizes the same OpenSDA debug interface as the FRDM-KW41Z board.

A debug probe is used for both flashing and debugging the board. This board is
configured by default to use the :ref:`opensda-daplink-onboard-debug-probe`.

Option 1: :ref:`opensda-daplink-onboard-debug-probe` (Recommended)
------------------------------------------------------------------

Install the :ref:`pyocd-debug-host-tools` and make sure they are in your search
path.

Follow the instructions in :ref:`opensda-daplink-onboard-debug-probe` to program
the `OpenSDA DAPLink FRDM-KW41Z Firmware`_.

Option 2: :ref:`opensda-jlink-onboard-debug-probe`
--------------------------------------------------

Install the :ref:`jlink-debug-host-tools` and make sure they are in your search
path.

Follow the instructions in :ref:`opensda-jlink-onboard-debug-probe` to program
the `OpenSDA J-Link FRDM-KW41Z Firmware`_.

Add the arguments ``-DBOARD_FLASH_RUNNER=jlink`` and
``-DBOARD_DEBUG_RUNNER=jlink`` when you invoke ``west build`` to override the
default runner from pyOCD to J-Link:

.. zephyr-app-commands::
   :zephyr-app: samples/hello_world
   :board: ubx_r41zeval_kw41z
   :gen-args: -DBOARD_FLASH_RUNNER=jlink -DBOARD_DEBUG_RUNNER=jlink
   :goals: build

Configuring a Console
=====================

Regardless of your choice in debug probe, we will use the OpenSDA
microcontroller as a usb-to-serial adapter for the serial console.

Connect a USB cable from your PC to J1.

Use the following settings with your serial terminal of choice (minicom, putty,
etc.):

- Speed: 115200
- Data: 8 bits
- Parity: None
- Stop bits: 1

Flashing
========

Here is an example for the :ref:`hello_world` application.

.. zephyr-app-commands::
   :zephyr-app: samples/hello_world
   :board: ubx_r41zeval_kw41z
   :goals: flash

Open a serial terminal, reset the board (press the SW1 button), and you should
see the following message in the terminal:

.. code-block:: console

   ***** Booting Zephyr OS v1.14.0-rc1 *****
   Hello World! ubx_r41zeval_kw41z

Debugging
=========

Here is an example for the :ref:`hello_world` application.

.. zephyr-app-commands::
   :zephyr-app: samples/hello_world
   :board: ubx_r41zeval_kw41z
   :goals: debug

Open a serial terminal, step through the application in your debugger, and you
should see the following message in the terminal:

.. code-block:: console

   ***** Booting Zephyr OS v1.14.0-rc1 *****
   Hello World! ubx_r41zeval_kw41z

.. _OpenSDA DAPLink FRDM-KW41Z Firmware:
   https://www.nxp.com/assets/downloads/data/en/reference-applications/OpenSDAv2.2_DAPLink_frdmkw41z_rev0241.zip

.. _OpenSDA J-Link FRDM-KW41Z Firmware:
   https://www.segger.com/downloads/jlink/OpenSDA_FRDM-KW41Z

.. _u-blox website:
   https://www.u-blox.com/en/product/r41z-open-cpu
