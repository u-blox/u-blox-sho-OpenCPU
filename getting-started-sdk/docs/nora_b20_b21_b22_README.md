# NORA-B20-B21-B22 (Nordic nRF54L15/L10/L05)

| Part | SoC | NVM | RAM | Antenna | Board target |
|------|-----|-----|-----|---------|--------------|
| NORA-B201 / B206 | nRF54L15 | 1.5 MB | 256 kB | Pin / PCB | `ubx_evknorab2/nrf54l15/cpuapp` (default) |
| NORA-B211 / B216 | nRF54L10 | 1.0 MB | 192 kB | Pin / PCB | `ubx_evknorab2/nrf54l10/cpuapp` |
| NORA-B221 / B226 | nRF54L05 | 0.5 MB | 96 kB | Pin / PCB | `ubx_evknorab2/nrf54l05/cpuapp` |

Bluetooth LE and IEEE 802.15.4 (Thread, Matter, Zigbee). Built with the nRF
Connect SDK (NCS) v3.4.1 on Windows, WSL2, Linux and macOS; the `ubx_evknorab2`
board is upstream in Zephyr and NCS. EVKs: EVK-NORA-B201 and EVK-NORA-B206, both
with an on-board J-Link OB.

NORA-B26x and B27x are u-connectXpress modules and are not built here.

## Quick start

```bash
./ubx-sdk.sh nora-b20-b21-b22 --doctor
./ubx-sdk.sh nora-b20-b21-b22 --clone --install
./ubx-sdk.sh nora-b20-b21-b22 --build hello_world --flash --log
```

- Tools: the quickest route is nRF Connect for Desktop and its Toolchain
  Manager (Zephyr SDK, CMake, Ninja, west, nrfutil). `--doctor` names what is
  missing.
- `--clone` creates the workspace in `C:\ncs\v3.4.1` or `~/ncs/v3.4.1` (about
  15 GB). Existing workspaces (`C:\ncs\*`, `~/ncs*`, `ZEPHYR_BASE`) are found and
  the one with the board is used. Choose one with
  `python scripts/nordic_ncs_build.py nora-b20-b21-b22 use <path>`, or set
  `UBX_NCS_WORKSPACE`.
- Other parts or the RISC-V core: `--build hello_world -- --board ubx_evknorab2/nrf54l10/cpuapp`
  (`/ns` for TF-M, `cpuflpr` for the coprocessor).
- `--list` searches `nrf/samples`, `nrf/applications` and `zephyr/samples`; a
  unique name such as `peripheral_uart` is enough.

The u-blox RF configuration for this module is pending, so `--rf-config` has
nothing to apply yet.

Output: `<workspace>/build/<sample>/<sample>/zephyr/` (`zephyr.elf`, `.hex`, `.bin`).

## Flash and log

`--flash` runs `west flash` with `nrfutil`; pass `-- --runner jlink` for J-Link
and `--flash <SERIAL>` with several probes attached. `--log [PORT]` opens the
console; the EVK exposes several ports, so pass the right one if the first
shows nothing.

## Bluetooth address

u-blox programs no address. The firmware uses the random static address in the
Nordic FICR (`DEVICEADDR`): `--build bluetooth/beacon --flash --log` prints it
("advertising as ...").

## Matter

Matter comes with NCS, so nothing extra is fetched and there is no WSL2 hop:

```bash
./ubx-matter.sh nora-b20-b21-b22 --build light_bulb --flash --log
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Board target not found | The workspace is older than NCS v3; `--clone`, or select another with `use` |
| No toolchain | Install the Zephyr SDK, or set `ZEPHYR_SDK_INSTALL_DIR` |
| `west update` interrupted | Re-run `--clone`; it resumes |
| Serial port not accessible (Linux) | `sudo usermod -aG dialout $USER`, then log in again |
