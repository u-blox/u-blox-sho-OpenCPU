# IRIS-EVK-W1 Board GPIO Configuration Guide (LEDs and Switches)

This guide details the setup process for GPIO components (such as LEDs and switches) on the IRIS-EVK-W1 board. The configuration requires modifications to `pin_mux` files and utilizes the SDK API within the main application code.

## GPIO Configuration Steps

### 1. Add `pin_mux.c` and `pin_mux.h` to Your Project
   - Copy the `pin_mux.c` and `pin_mux.h` files into the `board` folder of your project directory. These files handle pin mappings and initialize functions for the board's LEDs and switches.

### 2. Enable or Disable GPIO Functionality
   - Locate the board GPIO initialization function (for example, `BOARD_InitPins()`) in the SDK. This function sets up board pins, including GPIO configuration for LEDs and switches:
      ```c
      IO_MUX_SetPinMux(IO_MUX_GPIOXX);
      ```
   - Confirm that `pin_mux.c` initializes the necessary GPIO pins in the `BOARD_InitPins` function.

### GPIO Pin Assignments

Here’s a table of GPIO pin assignments for LEDs and switches:

| **GPIO Number** | **Function**              |
|-----------------|---------------------------|
| GPIO42          | RGB-Blue                  |
| GPIO43          | RGB-Green                 |
| GPIO44          | RGB-Red                   |
| GPIO45          | SW1                       |
| GPIO46          | MikroBus-Analog 1         |
| GPIO47          | MikroBus-Analog 2         |
| GPIO48          | MikroBus-Analog 3         |
| GPIO49          | MikroBus-Analog 4         |
| GPIO51          | SW2                       |

### 3. Include `pin_mux.h` in Your Application Code
   - In the main application file (`main.c`), add `#include "pin_mux.h"` to import the GPIO configurations. This will allow the use of GPIO pins with predefined macros and functions in the `pin_mux.h` file.This macro defines specific board parameters, including peripheral name, signal, channel, pin number, port number, and other settings.

## Example Code Snippet for `main.c`

Here’s a sample code snippet for configuring and toggling an RGB LED:

```c
#include "pin_mux.h"
#include "fsl_gpio.h"

int main(void) {
    /* Initialize board pins */
    GPIO_PortInit(GPIO, 1);

    /* Configure RGB_BLUE pin (GPIO42) */
    gpio_pin_config_t gpio1_pinH12_config = {
        .pinDirection = kGPIO_DigitalOutput,
        .outputLogic = 0U
    };
    
    GPIO_PinInit(GPIO, 1U, 11U, &gpio1_pinH12_config);
    uint32_t coreClock = CLOCK_GetFreq(kCLOCK_CoreSysClk);
    PRINTF("Core Clock = %d\n", coreClock);

    /* Toggle RGB_BLUE LED */
    GPIO_PortToggle(GPIO, 1U, 1U << 11U);
    SDK_DelayAtLeastUs(3000000, coreClock);
}
```

## Using the MCUXpresso Config Tool to Generate `pin_mux` Files

The MCUXpresso Config Tool, integrated into the IDE, allows you to create and manage `pin_mux` files. For detailed instructions, refer to the [NXP documentation](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcuxpresso-config-tools-pins-clocks-and-peripherals:MCUXpresso-Config-Tools).
