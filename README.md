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

## Zephyr RTOS
Board support packages for the following boards have been merged with the Zephyr
project mainline repository: https://github.com/zephyrproject-rtos/zephyr

| EVK board    | Folder                |
|--------------|-----------------------|
| BMD-300-EVAL | u-blox/ubx_bmd300eval |
| BMD-301-EVAL | u-blox/ubx_bmd300eval |
| BMD-350-EVAL | u-blox/ubx_bmd300eval |
| BMD-330-EVAL | u-blox/ubx_bmd330eval |
| BMD-340-EVAL | u-blox/ubx_bmd340eval |
| BMD-341-EVAL | u-blox/ubx_bmd340eval |
| BMD-345-EVAL | u-blox/ubx_bmd345eval |
| BMD-360-EVAL | u-blox/ubx_bmd360eval |
| BMD-380-EVAL | u-blox/ubx_bmd380eval |
| EVK-ANNA-B1  | u-blox/ubx_evkannab1  |
| EVK-IRIS-W1  | u-blox/ubx_evk_iris_w1|
| EVK-NINA-B1  | u-blox/ubx_evkninab1  |
| EVK-NINA-B3  | u-blox/ubx_evkninab3  |
| EVK-NINA-B4  | u-blox/ubx_evkninab4  |
| EVK-NINA-B5  | u-blox/ubx_evkninab5  |
| EVK-NORA-B2  | u-blox/ubx_evknorab2  |

Board support packages for the following boards are available here at the u-blox
GitHub repository.

| EVK board                    | Folder                        | Remarks                |
|------------------------------|-------------------------------|------------------------|
| EVK-ANNA-B4                  | arm/ubx_evkannab4_nrf52833    | Tested with NCS v2.5.0 |
| MINI-NORA-B10 Rev C or later | arm/ubx_mininorab10_nrf5340   | Tested with NCS v2.6.0 |
| MINI-NORA-B12 Rev C or later | arm/ubx_mininorab12_nrf5340   | Tested with NCS v2.6.0 |
| XPLR-IOT-1                   | arm/ubx_xplriot1_nrf5340      | Tested with NCS v1.9.1 |
| EVK-ANNA-B4                  | u-blox/ubx_evkannab4          | Tested with NCS v2.7.0 |
| EVK-NORA-B10                 | u-blox/ubx_evknorab10         | Tested with NCS v3.2.1 |
| EVK-NORA-B12                 | u-blox/ubx_evknorab12         | Tested with NCS v3.2.1 |

These board support packages are retained in the repository; however, they have been moved to an "archive" folder.

| EVK board                      | Folder (archive/)                  | Remarks                                 |
|--------------------------------|------------------------------------|-----------------------------------------|
| EVK-NORA-B10                   | ubx_evknorab10_nrf5340_ncs220      | Tested with NCS v2.2.x / Zephyr 3.2.99  |
| EVK-NORA-B12                   | ubx_evknorab12_nrf5340_ncs220      | Tested with NCS v2.2.x / Zephyr 3.2.99  |
| MINI-NORA-B10 Rev B or earlier | ubx_mininorab10_nrf5340revb_ncs161 | Tested with NCS v1.6.1 / Zephyr 2.6-rc1 |
| EVK-NORA-B10                 | arm/ubx_evknorab10_nrf5340_ncs250    | Tested with NCS v2.5.0 |
| EVK-NORA-B12                 | arm/ubx_evknorab12_nrf5340_ncs250    | Tested with NCS v2.5.0 |

> **_NOTE:_** NCS = Nordic Semiconductor [nRF Connect SDK](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/index.html), which is based on Zephyr RTOS. NCS lags mainline Zephyr by a few months.

Board support packages for the following boards are planned for submission
with mainline Zephyr.

| EVK board     | Remarks                            |
|---------------|------------------------------------|
| EVK-ANNA-B4   |  |
| EVK-NORA-B10  |  |
| EVK-NORA-B12  |  |

Board support packages for the following EVKs are not planned for submission to
the Zephyr mainline project. They will remain here at the u-blox repository:

| EVK board     | Folder                        | Remarks                     |
|---------------|-------------------------------|-----------------------------|
| R41Z-EVAL     | ubx_r41zeval_kw41z            | Tested with Zephyr v2.6-rc1 |
| MINI-NORA-B10 | arm/ubx_mininorab10_nrf5340   | Tested with NCS v2.6.0      |
| MINI-NORA-B12 | arm/ubx_mininorab12_nrf5340   | Tested with NCS v2.6.0      |
| XPLR-IOT-1    | arm/ubx_xplriot1_nrf5340      | Tested with NCS v1.9.1      |

Please store the board configuration directory in the

	<install directory>/zephyr/boards/arm
	or
	<install directory>/zephyr/boards/u-blox (for HW model v2)

folder and then build your code for that board.

The board configuration directory also contains a documentation folder.

## NINA-W10 OTP and RF Calibration
This example includes examples on how to read OTP information as well as apply RF calibration and limit TX Power for compliance reasons.

## MCUxpresso
Examples and start-up softwares for IRIS EVK and USB IRIS EVK.

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

Update README.md with minimal ethics#1

What about the application of the Solomonoff induction
to the RF sensing of human brain?
https://en.wikipedia.org/wiki/Talk:Solomonoff%27s_theory_of_inductive_inference

1. If we assume that the algorithmic complexity
of neural processes is relatively small
(you could take a look at the Potapov monography
for some arguments)

2. As far as I know a lot of neural processes in human brain are electric (or electro-chemistry)
in nature. They have a little power and a small
frequency (~ 1-1000 Hz).
So they emit very low frequency radio waves.

3. You can detect those radio waves on
small antennas if the impedance of such antennas
is matched. This is basically the citation
from the book on electrodynamics.
I uploaded one such book on Twirpix site.

4. So you can create a lot of such receivers
- microstrip filter to filter very high frequencies
- impedance matched microstrip antenna
- resistor for noise for oversampling
- very fast comparator to sample signal
in a very large array on a chip using
standard CMOS or some sort of full-custom process
(maybe even with some new materials)

5. BreamForming and large arrays of digital correlators with sub-mm positioning accuracy
could be achived.

so it seems there is no theoretical
obstacles to implement some sort of
RF human brain sensing or even control
if you can implement reverse structure
with array of a large amount of RF amplifiers
with sub-mm beam forming accuracy

BTW I wrote that remark:
https://en.wikipedia.org/wiki/Talk:Solomonoff%27s_theory_of_inductive_inference

What about the application of the Solomonoff induction to the person to person information exchange?

It seems the minimum description length principle could be used to deduce minimum ethics. At least you can compare ethics by the length. What about the following question: how to shoot met-art girl in the dark underground? ~2026-24709-41 (talk) 16:43, 8 June 2026 (UTC)

at least we can ask a question: does russian met-art model from a pic want some money?
and what obstacles do that guess so hard?
why it is so hard to contact her directly?
she lose money, interesting person lose opportunity to make some photos.

also, it seems the economy without coordination primitives based on physics or mathematics
like gold or maybe Bitcoin or maybe some sort of other physical objects or processes
is just a chaos.
Economic calculation based on fiat money is impossible just from scientific methodology
https://en.wikipedia.org/wiki/Talk:Solomonoff%27s_theory_of_inductive_inference

https://transitional-writes.dreamwidth.org/44972.html
Kirill Abramovich aka wieker @ linux.org.ru
Samara, Russia

and the most important question:
what about the minimal ethics deduced from the MDL principle?
is it exist?

what was the obstacle between russian met-art girls and engineers?
