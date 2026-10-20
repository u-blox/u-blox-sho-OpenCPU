# u-blox-sho-OpenCPU
Repository with reference code for u-blox Open CPU modules.

## Introduction
The reference code in this repository is intended to run on the Evaluation Kits
that can be purchased from u-blox. It is also intended as a reference for how to
configure the modules when they are integrated on a customer's own board.

Data sheets and other information related to the modules and EVKs can be found
at the u-blox website, https://www.u-blox.com/.

## Contents

| Folder | SDK / environment | Content |
|--------|-------------------|---------|
| [zephyr](zephyr/README.md) | Zephyr RTOS / nRF Connect SDK | Board support packages and DFU bootloaders |
| [nrf5-sdk](nrf5-sdk/README.md) | Nordic nRF5 SDK | Board files for EVK-ANNA-B1, EVK-ANNA-B4, EVK-NINA-B1, EVK-NINA-B3 and EVK-NINA-B4 |
| [mcuxpresso](mcuxpresso/README.md) | NXP MCUXpresso SDK | IRIS-W1 (EVK-IRIS-W1, USB-IRIS-W1) and EVK-NINA-B50x |
| [esp-idf](esp-idf/README.md) | Espressif ESP-IDF | RF calibration and output power for NINA-W1, NORA-W1 and NORA-W40 |
| [ameba-rtos-d](ameba-rtos-d/README.md) | Realtek Ameba-D SDK | RF parameters and adaptivity for NORA-W30 |

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

