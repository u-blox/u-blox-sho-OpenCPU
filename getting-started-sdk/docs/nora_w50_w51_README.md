# NORA-W50-W51 (TI CC3501E/CC3551E)

| | |
|---|---|
| Radio | Wi-Fi 6 (802.11b/g/n/ax), Bluetooth LE 5.4. NORA-W50x 2.4 GHz; NORA-W51x 2.4 and 5 GHz |
| MCU | Arm Cortex-M33 at 160 MHz, 1.1 MB SRAM, 4 or 8 MB flash |
| Parts | NORA-W501/W511 (antenna pin), NORA-W506/W516 (internal PCB antenna) |
| SDK | TI SimpleLink Wi-Fi SDK, FreeRTOS, board `LP_EM_CC35X1` |
| Host | Windows, WSL2, Linux |

The SDK ships board files for TI's LaunchPad. For a u-blox EVK keep the device
and re-run SysConfig (`.syscfg` in each example) for the module's pinout and
flash size.

## Tools

Install these yourself (TI and Arm installers); `--doctor` finds them and says
what is missing:

| Tool | |
|------|---|
| SysConfig | <https://www.ti.com/tool/SYSCONFIG> (also in Code Composer Studio) |
| TI Arm Clang or Arm GNU Toolchain | One is enough; examples ship `ticlang/` and `gcc/` builds |
| CMake, GNU make | On Windows `gmake` from CCS, or `winget install ezwinports.make` |
| SimpleLink Wi-Fi Toolbox | Flashing |

An SDK installed with TI's installer (`C:\ti\simplelink_wifi_sdk_*`, `~/ti/...`)
is used as is. Without one, `--clone` fetches TI's example repos with the SDK
as a submodule.

## Quick start

```bash
./ubx-sdk.sh nora-w50-w51 --doctor
./ubx-sdk.sh nora-w50-w51 --clone
python scripts/nora_w50_w51_build.py configure       # tool paths into imports.mak, once
./ubx-sdk.sh nora-w50-w51 --build-sdk                # once per SDK, slow
./ubx-sdk.sh nora-w50-w51 --list
./ubx-sdk.sh nora-w50-w51 --build network_terminal --flash --log
```

The u-blox RF configuration for this module is pending, so `--rf-config` has
nothing to apply yet.

`configure` has no launcher flag yet. It writes the detected tool paths into
the SDK's `imports.mak` (backup `imports.mak.orig`); TI's makefiles do not
accept spaces, so Windows paths are converted to their 8.3 form. Override a
path it cannot find with, e.g.,
`python scripts/nora_w50_w51_build.py --gcc_armcompiler <dir> configure`.
Pass build options after `--`, e.g. `--build network_terminal -- --toolchain gcc`.

## Examples

Under `examples/rtos/LP_EM_CC35X1/`; each has a `README.html`.

| Example | |
|---------|---|
| `drivers/uart2echo` | Proves toolchain, flashing and console |
| `drivers/empty` | Skeleton for your own application |
| `demos/network_terminal` | Wi-Fi CLI: `scan`, `wlanconnect`, sockets, ping |
| `demos/ble_wifi_provisioning` | Wi-Fi credentials from a phone over Bluetooth LE |
| `demos/mqtt_client`, `demos/ota_example` | MQTT, firmware update |

## Flash and log

The EVK's on-board XDS110 gives debug and a UART. `--flash` runs the Wi-Fi
Toolbox programmer with the `tool_settings.json` the build writes (set
`TI_TOOLBOX` if the toolbox is not on PATH); it fails when the build wrote
none. Not yet verified on an EVK. CCS and UniFlash also work. `--log` opens the
XDS110 *Application/User UART* at 115200.

## WSL2

Keep the workspace in the Linux file system (the default is `~/nora-w50-w51`);
`/mnt/c` builds are very slow. USB is not visible in WSL2 by default: attach it
with `usbipd attach --wsl --busid <BUSID>` from an admin PowerShell, or flash
from Windows.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Linker errors about missing SDK libraries | `--build-sdk` was skipped |
| A tool not found | `--doctor` names it; install it, or pass its path to `configure` as above |
| No serial output | Use the *Application* UART, not *Auxiliary*, at 115200 |
| Wi-Fi does not see a 5 GHz network | NORA-W50x is 2.4 GHz only |

Zephyr support for the CC35xx comes from TI's downstream
[simplelink-zephyr](https://github.com/TexasInstruments/simplelink-zephyr) and
is not driven by this SDK.
