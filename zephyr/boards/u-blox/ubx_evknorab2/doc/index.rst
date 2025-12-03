.. _ubx_evknorab2:

EVK NORA-B2
###########

Overview
********

.. note::

   All software for the NORA-B2 module is experimental and hardware availability
   is restricted to the participants in the limited sampling program.
   This board definition is preliminary. Tested using Zephyr samples blinky,
   blinky_pwm, button. Other interfaces are untested.

The NORA-B2 module is built on the nRF54L15 SoC from Nordic Semiconductor.

The Development Kit hardware provides support for the Nordic Semiconductor
nRF54L15 Arm Cortex-M33 CPU and the following devices:

* :abbr:`SAADC (Successive Approximation Analog to Digital Converter)`
* CLOCK
* RRAM
* :abbr:`GPIO (General Purpose Input Output)`
* :abbr:`TWIM (I2C-compatible two-wire interface master with EasyDMA)`
* MEMCONF
* :abbr:`MPU (Memory Protection Unit)`
* :abbr:`NVIC (Nested Vectored Interrupt Controller)`
* :abbr:`PWM (Pulse Width Modulation)`
* :abbr:`GRTC (Global real-time counter)`
* Segger RTT (RTT Console)
* :abbr:`SPI (Serial Peripheral Interface)`
* :abbr:`UARTE (Universal asynchronous receiver-transmitter)`
* :abbr:`WDT (Watchdog Timer)`

.. figure:: img/XXXXX.webp
     :align: center
     :alt: EVK NORA-B2

     EVK NORA-B2

Hardware
********

EVK NORA-B2 has two crystal oscillators:

* High-frequency 32 MHz crystal oscillator (HFXO, module internal). Please
  refer to NORA-B2 SIM for information about internal capacitor settings.
* Low-frequency 32.768 kHz crystal oscillator (LFXO)

The LFXO crystal oscillator can be configured to use either
internal or external capacitors. By default, the internal capacitors are used.
For more information about configuring the oscillators, refer to the
:nrf_clock_control: documentation.

Supported Features
==================

The ``ubx_evknorab2/nrf54l15/cpuapp`` board configuration supports the following
hardware features:

+-----------+------------+----------------------+
| Interface | Controller | Driver/Component     |
+===========+============+======================+
| CLOCK     | on-chip    | clock_control        |
+-----------+------------+----------------------+
| GPIO      | on-chip    | gpio                 |
+-----------+------------+----------------------+
| GRTC      | on-chip    | counter              |
+-----------+------------+----------------------+
| MEMCONF   | on-chip    | retained_mem         |
+-----------+------------+----------------------+
| MPU       | on-chip    | arch/arm             |
+-----------+------------+----------------------+
| NVIC      | on-chip    | arch/arm             |
+-----------+------------+----------------------+
| PWM       | on-chip    | pwm                  |
+-----------+------------+----------------------+
| RRAM      | on-chip    | flash                |
+-----------+------------+----------------------+
| RTT       | Segger     | console              |
+-----------+------------+----------------------+
| SPI(M/S)  | on-chip    | spi                  |
+-----------+------------+----------------------+
| SPU       | on-chip    | system protection    |
+-----------+------------+----------------------+
| TWIM      | on-chip    | i2c                  |
+-----------+------------+----------------------+
| UARTE     | on-chip    | serial               |
+-----------+------------+----------------------+
| WDT       | on-chip    | watchdog             |
+-----------+------------+----------------------+

Other hardware features have not been enabled yet for this board.

Programming and Debugging
*************************

Applications for the ``ubx_evknorab2/nrf54l15/cpuapp`` board can be
built, flashed, and debugged in the usual way. See
:ref:`build_an_application` and :ref:`application_run` for more details on
building and running.

Applications for the ``ubx_evknorab2/nrf54l15/cpuflpr`` board target need
to be built as multicore configuration with code snippet called ``vpr_launcher``
for the application core.

Enter the following command to compile ``hello_world`` for the FLPR core::
 west build -p -b ubx_evknorab2/nrf54l15/cpuflpr --sysbuild -- -DSB_VPR_LAUNCHER=y

Flashing
========

As an example, this section shows how to build and flash the :ref:`hello_world`
application.

.. warning::

   When programming the device, you might get an error similar to the following message::

    ERROR: The operation attempted is unavailable due to readback protection in
    ERROR: your device. Please use --recover to unlock the device.

   This error occurs when readback protection is enabled.
   To disable the readback protection, you must *recover* your device.

   Enter the following command to recover the core::

    west flash --recover

   The ``--recover`` command erases the flash memory and then writes a small binary into
   the recovered flash memory.
   This binary prevents the readback protection from enabling itself again after a pin
   reset or power cycle.

Follow the instructions in the :ref:`nordic_segger` page to install
and configure all the necessary software. Further information can be
found in :ref:`nordic_segger_flashing`.

To build and program the sample to the EVK NORA-B2, complete the following steps:

First, connect the EVK to you computer using the USB port on the EVK.
Next, build the sample by running the following command:

.. zephyr-app-commands::
   :zephyr-app: samples/hello_world
   :board: ubx_evknorab2/nrf54l15/cpuapp
   :goals: build flash

Testing the LEDs and buttons in the EVK-NORA-B2
***********************************************

Test the EVK NORA-B2 with a :zephyr:code-sample:`blinky` sample or a 
:zephyr:code-sample:`buttons` sample.

References
**********

.. target-notes::

.. _NORA-B20 product page: https://www.u-blox.com/en/product/nora-b2-series
