# u-blox Generic Aoa Tag App
This repository contains a basic aoa Tag example that is compatible with u-blox direction finding solution. It is based on the [directionless_tx example](https://github.com/zephyrproject-rtos/zephyr/tree/main/samples/bluetooth/direction_finding_connectionless_tx) from the Zephyr SDK with added Eddystone advertising as described in the [ANT-B10 SIM](https://content.u-blox.com/sites/default/files/documents/ANT-B10_SIM_UBX-22025788.pdf) and ANT-B11 SIM. The example application is built and tested against [u-blox EVK-BMD-360](https://www.u-blox.com/en/product/evk-bmd-360) that features nRF52811 SoC .


# Setup
Below is a short summary of the required steps to compile the application.
For more detailed instructions go to the offical [nRF Connect Getting Started Guide](https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/getting_started.html)

## Download nRF Connect and Toolchain
- Open nRF Connect for Desktop and open the Toolchain Manager.
- Download nRF Connect SDK v2.7.0.

### Building with nRF Connect VSCode plugin
- In Visual Studio Code go to marketplace and search for "nrf connect".
- Install the nRF Connect Extension Pack (this will install all required extensions at once).
- Click on the nRF Connect extension and select "Add an existing application"
- Choose the folder BMD-360_AOATAG (or the folder name you choose when cloning this repository).
- Press CTRL+SHIFT+P and search/select "nRF Connect: Select nRF Connect SDK"
- Press "Yes" in the popup asking if you want to change it.
- In the dropdown you should see the path where nRF Connect was installed before. Choose it.
- Under "applications" press "No build configurations Click to create one".
- Choose all boards and select ubx_bmd360eval_nrf52811 in the drowdown.
- Click "Add argument" button to add Extra CMake arguments "-DEXTRA_CONF_FILE=overlay-aoa.conf"
- Press "Build Configuration" button.
- Now project should build successfully.

### Building with command line
- Open nRF Connect for Desktops Toolchain Manager.
- Right next to the "nRF Connect SDK v2.7.0" you have a dropdown, click "Open bash". This step is not required, but it will set up the necessary environment variables for you.
- `cd` to project folder
- `west build -b ubx_bmd360eval_nrf52811 . -- -DEXTRA_CONF_FILE=overlay-aoa.conf`
- `west flash`
- `west flash` only will be enough for building + flashing after that, specifying the board is only needed on the first build.


## Running on other boards
This sample application primarily supports the u-blox BMD-360 EVK.

However getting it up and running on other boards which either use NINA-B4 module (like **NINA-B4-EVK**) or a NRF52833 DK is only a matter of selecting the appropriate board file.

# Using the application
u-blox anchors should automatically detect the aoa tags implemented based on this example.

# More information about the hardware kits
Please find the user manual of u-blox anchors on how to setup direction finding solution.

# Note
Please be aware BMD-360 is memory constrained, for any functionality outside this example, such as accessing sensors or implementing a SW update functionality on the tag, a module with more memory is recommended.

# Disclaimer
Copyright (C) u-blox

u-blox reserves all rights in this deliverable (documentation, software, etc., hereafter “Deliverable”).

u-blox grants you the right to use, copy, modify and distribute the Deliverable provided hereunder for any purpose without fee.

THIS DELIVERABLE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED WARRANTY. IN PARTICULAR, NEITHER THE AUTHOR NOR U-BLOX MAKES ANY REPRESENTATION OR WARRANTY OF ANY KIND CONCERNING THE MERCHANTABILITY OF THIS DELIVERABLE OR ITS FITNESS FOR ANY PARTICULAR PURPOSE.

In case you provide us a feedback or make a contribution in the form of a further development of the Deliverable (“Contribution”), u-blox will have the same rights as granted to you, namely to use, copy, modify and distribute the Contribution provided to us for any purpose without fee.