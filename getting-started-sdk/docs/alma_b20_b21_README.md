# ALMA-B20-B21 (Nordic nRF54LM20A/B)

| Part | SoC | Antenna |
|------|-----|---------|
| ALMA-B201 / B206 | nRF54LM20A | Pin / PCB |
| ALMA-B211 / B216 | nRF54LM20B (adds the Axon NPU) | Pin / PCB |

ALMA-B20-B21 works like [NORA-B20-B21-B22](nora_b20_b21_b22_README.md): same
nRF Connect SDK workspace, tools, flags, flashing and Matter. Only the board
differs.

u-blox has not published an `ubx_evkalmab2` board yet, so builds use Nordic's
nRF54LM20 DK board. Pins, antenna path and power rails will not match an
ALMA-B20-B21 design; expect a devicetree overlay for anything beyond CPU
bring-up.

## Quick start

```bash
./ubx-sdk.sh alma-b20-b21 --doctor
./ubx-sdk.sh alma-b20-b21 --clone --install
./ubx-sdk.sh alma-b20-b21 --build hello_world --flash --log
```

| Board target | For |
|--------------|-----|
| `nrf54lm20dk/nrf54lm20a/cpuapp` | ALMA-B20x (default) |
| `nrf54lm20dk/nrf54lm20b/cpuapp` | ALMA-B21x: `--build hello_world -- --board nrf54lm20dk/nrf54lm20b/cpuapp` |

Add `/ns` for TF-M, or use `cpuflpr` for the RISC-V coprocessor. The Axon NPU
toolchain comes from Nordic and is not driven by this SDK.

The u-blox RF configuration for this module is pending, so `--rf-config` has
nothing to apply yet.

## Bluetooth address

As on NORA-B2, u-blox programs no address; the firmware uses the random static
address in the Nordic FICR (`DEVICEADDR`). `--build bluetooth/beacon --flash --log`
prints it.
