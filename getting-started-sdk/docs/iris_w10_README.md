# IRIS-W10 (NXP RW612/RW610)

| | |
|---|---|
| Radio | Dual-band Wi-Fi 6, Bluetooth LE 5.4, IEEE 802.15.4 / Thread (RW612 parts only) |
| MCU | Arm Cortex-M33 up to 260 MHz, 1.2 MB SRAM, 8 or 16 MB flash |
| Parts | IRIS-W101 (antenna pin), IRIS-W106 (internal PCB antenna); `-00B`/`-10B` RW612, `-30B`/`-40B` RW610 |
| SDK | NXP MCUXpresso SDK (west, CMake, Ninja), board target `rdrw612bga` |
| Host | Windows, WSL2, Linux |
| EVK | EVK-IRIS-W1 (on-board MCU-Link) |

## Quick start

```bash
./ubx-sdk.sh iris-w10 --doctor
./ubx-sdk.sh iris-w10 --clone --install
./ubx-sdk.sh iris-w10 --variant IRIS-W101-00B --rf-config --build demo_apps/hello_world --flash --log
```

Without `--rf-config` the firmware uses NXP's reference-board calibration and
is not regulatory compliant on the module. It also installs the flash driver
for the module's flash part.

- `--clone` fetches the release this SDK is tested with, only what `rdrw612bga`
  needs (about 2 GB); `--clone main` fetches the development branch next to it.
  `--clone --full` fetches the whole SDK (about 7 GB).
- Needs CMake 3.30+, Ninja 1.12+ and the Arm GNU Toolchain. `--install`
  installs `west` and the SDK's Python requirements and names whatever else is
  missing. The toolchain is found by itself (Arm installer, MCUXpresso
  Installer, or `PATH`); set `ARMGCC_DIR` to its root only to force one.
- `--list` shows the examples; a bare name such as `wifi_cli` is enough when it
  is unique.
- Release build: `--build <example> -- --config release`.

Output: `sdks/mcuxpresso-sdk/<version>/build/`, named after the example
(`.elf`, `.bin`, `.hex`); older SDK releases use `build/<debug|release>/`.

## Flash and log

`--flash` writes the `.bin` at 0x08000000 through J-Link Commander on the EVK's
MCU-Link (J-Link firmware) and verifies it. `--log` opens the MCU-Link VCOM at
115200 baud.

J-Link needs a valid flash config block (FCB) in flash. When it cannot program
or verify (blank or wrong FCB), recover once through the boot ROM with `blhost`
(installed by `--install`):

1. SW3 position 1 (EXT-REQ) to GND, power-cycle.
2. `./ubx-sdk.sh iris-w10 --flash COM<n>` (the MCU-Link VCOM).
3. SW3 position 1 back, power-cycle. J-Link `--flash` works again.

The flash part decides the FCB: Fidelix (modules from date code 2346) is the
default; for older Macronix modules add `--set flash_part=macronix-8mb` to
`--rf-config`.

## MCUXpresso for VS Code

After `--clone --install --rf-config`, import
`sdks/mcuxpresso-sdk/<version>` as a local repository, then import an example
for `rdrw612bga`. Build and debug from the extension (MCU-Link through
LinkServer, or J-Link). See [SETUP.md](SETUP.md#vendor-extensions).

## u-blox files

The u-blox files are in [mcuxpresso/iris-w10/sw-config](../../mcuxpresso/iris-w10/sw-config/README.md).
`--rf-config` applies the Wi-Fi, Bluetooth and 802.15.4 calibration, the TX
power limits and the flash driver. The board pin mux (`board-files/`) and
linker scripts (`linker-scripts/`) are copied by hand when your design needs
them.

## MAC address

Set by u-blox in the RW612 OTP. Read it on the module:
`--build wifi_examples/wifi_cli --flash --log`, then type `wlan-mac`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `No Arm GNU toolchain found` | Install it, or set `ARMGCC_DIR` to the toolchain root (not `bin/`) |
| `west not found` | `--install` |
| Example missing after `--clone` | It is outside the board-only fetch: `--clone --full` |
| Stale build | `--clean --build <example>` |
