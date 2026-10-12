# Zephyr RTOS

Board support packages and DFU bootloaders for u-blox modules using
Zephyr RTOS or the Nordic Semiconductor [nRF Connect SDK](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/index.html) (NCS).

> **_NOTE:_** NCS is based on Zephyr RTOS. NCS lags mainline Zephyr by a few months.

## SDK resources

| SDK | Repository | Documentation |
|-----|------------|---------------|
| Zephyr RTOS | [zephyrproject-rtos/zephyr](https://github.com/zephyrproject-rtos/zephyr) | [Zephyr documentation](https://docs.zephyrproject.org), [Zephyr Project](https://www.zephyrproject.org/) |
| nRF Connect SDK | [nrfconnect/sdk-nrf](https://github.com/nrfconnect/sdk-nrf) | [nRF Connect SDK documentation](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/index.html), [nRF Connect SDK product page](https://www.nordicsemi.com/Products/Development-software/nRF-Connect-SDK) |

| Folder | Content |
|--------|---------|
| [boards](boards) | Board support packages |
| [dfu-bootloaders](dfu-bootloaders/README.md) | Factory DFU bootloaders for ANNA-B402 and NINA-B40x |

## Boards in mainline Zephyr
Board support packages for the following boards have been merged with the Zephyr
project mainline repository: https://github.com/zephyrproject-rtos/zephyr

| EVK board    | Folder (in Zephyr)     |
|--------------|------------------------|
| BMD-300-EVAL | u-blox/ubx_bmd300eval  |
| BMD-301-EVAL | u-blox/ubx_bmd300eval  |
| BMD-350-EVAL | u-blox/ubx_bmd300eval  |
| BMD-330-EVAL | u-blox/ubx_bmd330eval  |
| BMD-340-EVAL | u-blox/ubx_bmd340eval  |
| BMD-341-EVAL | u-blox/ubx_bmd340eval  |
| BMD-345-EVAL | u-blox/ubx_bmd345eval  |
| BMD-360-EVAL | u-blox/ubx_bmd360eval  |
| BMD-380-EVAL | u-blox/ubx_bmd380eval  |
| EVK-ANNA-B1  | u-blox/ubx_evkannab1   |
| EVK-IRIS-W1  | u-blox/ubx_evk_iris_w1 |
| EVK-NINA-B1  | u-blox/ubx_evkninab1   |
| EVK-NINA-B3  | u-blox/ubx_evkninab3   |
| EVK-NINA-B4  | u-blox/ubx_evkninab4   |
| EVK-NINA-B5  | u-blox/ubx_evkninab5   |
| EVK-NORA-B2  | u-blox/ubx_evknorab2   |

## Boards in this repository
Board support packages for the following boards are available in this repository.
Folders are relative to [boards](boards). HW model v1 boards are in `arm/`, HW model v2 boards are in `u-blox/`.

| EVK board                    | Folder                                                            | HW model | Remarks                | Mainline Zephyr |
|------------------------------|-------------------------------------------------------------------|----------|------------------------|-----------------|
| EVK-ANNA-B4                  | [u-blox/ubx_evkannab4](boards/u-blox/ubx_evkannab4)               | v2       | Tested with NCS v2.7.0 | Planned |
| EVK-ANNA-B5                  | [u-blox/ubx_evkannab5](boards/u-blox/ubx_evkannab5)               | v2       | Tested with NCS v3.4.1 | Planned, [PR #118332](https://github.com/zephyrproject-rtos/zephyr/pull/118332) |
| EVK-NORA-B10                 | [u-blox/ubx_evknorab10](boards/u-blox/ubx_evknorab10)             | v2       | Tested with NCS v3.2.1 | Planned |
| EVK-NORA-B12                 | [u-blox/ubx_evknorab12](boards/u-blox/ubx_evknorab12)             | v2       | Tested with NCS v3.2.1 | Planned |
| MINI-NORA-B10 Rev C or later | [arm/ubx_mininorab10_nrf5340](boards/arm/ubx_mininorab10_nrf5340) | v1       | Tested with NCS v2.6.0 | Not planned |
| MINI-NORA-B12 Rev C or later | [arm/ubx_mininorab12_nrf5340](boards/arm/ubx_mininorab12_nrf5340) | v1       | Tested with NCS v2.6.0 | Not planned |
| XPLR-IOT-1                   | [arm/ubx_xplriot1_nrf5340](boards/arm/ubx_xplriot1_nrf5340)       | v1       | Tested with NCS v1.9.1 | Not planned |
| R41Z-EVAL                    | [arm/ubx_r41zeval_kw41z](boards/arm/ubx_r41zeval_kw41z)           | v1       | Tested with Zephyr v2.6-rc1 | Not planned |

## Archived boards
These board support packages are retained in the repository for older NCS versions.

| EVK board                      | Folder                                                                                                  | Remarks                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------------|
| EVK-ANNA-B4                    | [arm/archive/ubx_evkannab4_nrf52833_ncs250](boards/arm/archive/ubx_evkannab4_nrf52833_ncs250)           | Tested with NCS v2.5.0                  |
| EVK-NORA-B10                   | [arm/archive/ubx_evknorab10_nrf5340_ncs250](boards/arm/archive/ubx_evknorab10_nrf5340_ncs250)           | Tested with NCS v2.5.0                  |
| EVK-NORA-B12                   | [arm/archive/ubx_evknorab12_nrf5340_ncs250](boards/arm/archive/ubx_evknorab12_nrf5340_ncs250)           | Tested with NCS v2.5.0                  |
| EVK-NORA-B10                   | [arm/archive/ubx_evknorab10_nrf5340_ncs220](boards/arm/archive/ubx_evknorab10_nrf5340_ncs220)           | Tested with NCS v2.2.x / Zephyr 3.2.99  |
| EVK-NORA-B12                   | [arm/archive/ubx_evknorab12_nrf5340_ncs220](boards/arm/archive/ubx_evknorab12_nrf5340_ncs220)           | Tested with NCS v2.2.x / Zephyr 3.2.99  |
| MINI-NORA-B10 Rev B or earlier | [arm/archive/ubx_mininorab10revb_nrf5340_ncs161](boards/arm/archive/ubx_mininorab10revb_nrf5340_ncs161) | Tested with NCS v1.6.1 / Zephyr 2.6-rc1 |

## Using the board support packages

### Option 1: Build with BOARD_ROOT
Build directly from this repository by pointing `BOARD_ROOT` to the folder that
contains the `boards` folder, i.e. the `zephyr` folder of this repository:

	west build -b <board name> -- -DBOARD_ROOT=<path to u-blox-sho-OpenCPU>/zephyr

Boards in the `arm/archive` folder are not found this way; copy them as described in option 2.

### Option 2: Copy into the Zephyr tree
Copy the board configuration directory to

	<install directory>/zephyr/boards/arm
	or
	<install directory>/zephyr/boards/u-blox (for HW model v2)

and then build your code for that board.

The board configuration directory also contains a documentation folder.
