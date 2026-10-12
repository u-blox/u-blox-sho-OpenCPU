# NORA-W30 (Realtek RTL8720DF)

| | |
|---|---|
| Radio | Dual-band Wi-Fi 4 (802.11a/b/g/n, 2.4 and 5 GHz), Bluetooth LE 5.3 |
| MCU | Dual core: Cortex-M33 compatible (KM4, application) and Cortex-M23 compatible (KM0, low power) |
| Memory | 512 kB RAM, 4 MB flash |
| Parts | NORA-W301 (antenna pin), NORA-W306 (internal PCB antenna) |
| SDK | Realtek Ameba-D (`ameba-rtos-d`), GNU Make, `arm-none-eabi-gcc` |
| Host | Linux only. On Windows the launcher hops into WSL2 by itself. |

## Quick start

```bash
./ubx-sdk.sh nora-w30 --doctor
./ubx-sdk.sh nora-w30 --clone
./ubx-sdk.sh nora-w30 --variant NORA-W301 --region ETSI --rf-config --build project_hp
```

Without `--rf-config` the firmware uses Realtek's reference-board TX power
tables and is not regulatory compliant on the module. `--variant` is
`NORA-W301` or `NORA-W306`; `--region` prints the channel plan the application
must select at runtime.

Inside WSL2 (or on Linux) the build needs:

```bash
sudo apt install build-essential gcc-arm-none-eabi git python3
```

## What gets built

Ameba-D builds a complete firmware image, not one example at a time:

| Project | Core | |
|---------|------|---|
| `project_hp` | KM4 | Your application (default) |
| `project_lp` | KM0 | Low-power core and boot |

`--list` shows the `example_sources/` folders. They are compiled into the
firmware through the SDK configuration, not built as separate targets.

Images land in
`sdks/ameba-rtos-d/main/project/realtek_amebaD_va0_example/GCC-RELEASE/<project>/asdk/image/`.

## Flash and log

```bash
./ubx-sdk.sh nora-w30 --build project_lp      # KM0 core, once
./ubx-sdk.sh nora-w30 --build project_hp --flash --log
```

`--flash` programs both cores over SWD through the EVK's on-board J-Link OB
(SEGGER J-Link software required): `km0_boot_all.bin` at 0x08000000,
`km4_boot_all.bin` at 0x08004000 and `km0_km4_image2.bin` at 0x08006000. Pass
the probe serial number (`--flash <SN>`) when several J-Links are connected.
`--log` opens the J-Link virtual COM port at 115200. On Windows the build runs
in WSL2 and `--flash` and `--log` run on Windows, where the probe is.

Realtek's ROM bootloader (hold BOOT while resetting) with the Windows Image
Tool in the SDK's `tools/` folder is the alternative without a debugger.

## MAC address

Set by u-blox in eFuse. Read it on the module: build `project_hp`, flash it and
type `ATW?` in the console. `--mac-set` shows how to use another address at
runtime.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| WSL2 does not start, hangs or shows a `Wsl/Service/...` error | Administrator prompt: `net stop vmcompute`, then `net start vmcompute` |
| `arm-none-eabi-gcc` or `make` not found | Install the packages above inside WSL2 |
| Serial port not visible in WSL2 | Flash and log from Windows, or attach the port with `usbipd` |
