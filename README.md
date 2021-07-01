# u-blox-sho-OpenCPU
Repository with reference code for u-blox Open CPU modules.

## Introduction
The reference code in this repository is intended to run on the Evaluation Kits
that can be purchased from u-blox.

Data sheets and other information related to the modules and EVKs can be found
at the u-blox website, https://www.u-blox.com/.

## nRF5 SDK
Please refer to the System Integration Manual for each product for help on how
to integrate the reference code in your build environment.

Refer to the EVK User Guide for each board for more information on the specific
board.

## Zephyr
Board support packages for the following EVKs have been merged with the Zephyr
project mainline repository: https://github.com/zephyrproject-rtos/zephyr

| EVK board    | Folder                  |
|--------------|-------------------------|
| BMD-300-EVAL | ubx_bmd300eval_nrf52832 |
| BMD-301-EVAL | ubx_bmd300eval_nrf52832 |
| BMD-350-EVAL | ubx_bmd300eval_nrf52832 |
| BMD-330-EVAL | ubx_bmd330eval_nrf52810 |
| BMD-340-EVAL | ubx_bmd340eval_nrf52840 |
| BMD-341-EVAL | ubx_bmd340eval_nrf52840 |
| BMD-345-EVAL | ubx_bmd345eval_nrf52840 |
| BMD-360-EVAL | ubx_bmd350eval_nrf52811 |
| BMD-380-EVAL | ubx_bmd380eval_nrf52840 |
| EVK-ANNA-B1  | ubx_evkannab1_nrf52832  |
| EVK-NINA-B1  | ubx_evkninab1_nrf52832  |
| EVK-NINA-B3  | ubx_evkninab3_nrf52832  |
| EVK-NINA-B4  | ubx_evkninab4_nrf52832  |

Board support packages for the followng EVKs are not planned for submission to
the Zephyr mainline project:

| EVK board | Folder             |
|-----------|--------------------|
| R41Z-EVAL | ubx_r41zeval_kw41z |

Please store the board configuration directory in the

	<install directory>/zephyr/boards/arm

folder and then build your code for that board.

The board configuration directory also contains a documentation folder.

# Disclaimer
Copyright &#x00a9; u-blox

u-blox reserves all rights in this deliverable (documentation, software, etc.,
hereafter “Deliverable”).

u-blox grants you the right to use, copy, modify and distribute the
Deliverable provided hereunder for any purpose without fee.

THIS DELIVERABLE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
WARRANTY. IN PARTICULAR, NEITHER THE AUTHOR NOR U-BLOX MAKES ANY
REPRESENTATION OR WARRANTY OF ANY KIND CONCERNING THE MERCHANTABILITY OF THIS
DELIVERABLE OR ITS FITNESS FOR ANY PARTICULAR PURPOSE.

In case you provide us a feedback or make a contribution in the form of a
further development of the Deliverable (“Contribution”), u-blox will have the
same rights as granted to you, namely to use, copy, modify and distribute the
Contribution provided to us for any purpose without fee.

