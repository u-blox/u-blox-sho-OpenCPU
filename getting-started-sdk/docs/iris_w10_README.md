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

- `--clone` fetches only what `rdrw612bga` needs (about 2 GB); `--clone v25.09.00`
  picks a release. For the whole SDK (about 7 GB) run
  `python scripts/iris_w10_build.py clone --full`.
- Needs CMake 3.30+, Ninja 1.12+ and the Arm GNU Toolchain. `--install`
  installs `west` and the SDK's Python requirements and names whatever else is
  missing. The toolchain is found by itself (Arm installer, MCUXpresso
  Installer, or `PATH`); set `ARMGCC_DIR` to its root only to force one.
- `--list` shows the examples; a bare name such as `wifi_cli` is enough when it
  is unique.
- Release build: `--build <example> -- --config release`.

Output: `sdks/mcuxpresso-sdk/<version>/build/<debug|release>/`, named after the
example (`.elf`, `.bin`, `.hex`).

## Flash and log

`--flash` programs the `.hex` through J-Link (`pylink-square` from the venv and
SEGGER J-Link software). To use the EVK's MCU-Link with NXP's tools instead,
run `west flash -r linkserver` in the SDK folder. `--log` opens the console at
115200 baud.

Recovery over the serial boot ROM (`blhost`) is described in
[mcuxpresso/iris-w10/recovery-tool](../../mcuxpresso/iris-w10/recovery-tool).

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
| Example missing after `--clone` | It is outside the board-only fetch: `python scripts/iris_w10_build.py clone --full` |
| Stale build | `--clean --build <example>` |
