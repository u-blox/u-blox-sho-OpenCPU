# ALMA-W10-W11 (Nordic nRF7120/nRF7120E)

| Part | SoC | Radio | Antenna |
|------|-----|-------|---------|
| ALMA-W101 / W106 | nRF7120 | Wi-Fi 6 (2.4/5 GHz), Bluetooth LE, 802.15.4 | Pin / PCB |
| ALMA-W111 / W116 | nRF7120E | Wi-Fi 6E (2.4/5/6 GHz), Bluetooth LE, 802.15.4 | Pin / PCB |

EVKs: EVK-ALMA-W111 (W101/W111) and EVK-ALMA-W116 (W106/W116). ALMA-W161/W166
are u-connectXpress parts and are not built here.

ALMA-W10-W11 works like [NORA-B20-B21-B22](nora_b20_b21_b22_README.md): same
tools, flags, flashing, nRF Connect for VS Code and Matter. Two things differ:

- nRF7120 support is only in an nRF Connect SDK pre-release, so this target is
  pinned separately and `--clone` fetches its own workspace
  (`C:\ncs\<pre-release>` or `~/ncs/<pre-release>`) next to the one the other
  Nordic targets use. `--doctor` shows the pin.
- There is no `ubx_evkalmaw1` board yet, so builds use Nordic's nRF7120 DK
  board. Pins, antenna path and power rails will not match the EVK; expect a
  devicetree overlay for anything beyond CPU bring-up.

Not verified on hardware yet.

## Quick start

```bash
./ubx-sdk.sh alma-w10-w11 --doctor
./ubx-sdk.sh alma-w10-w11 --clone --install
./ubx-sdk.sh alma-w10-w11 --build hello_world --flash --log
```

| Board target | For |
|--------------|-----|
| `nrf7120dk/nrf7120/cpuapp` | ALMA-W10x (default) |
| `nrf7120dk/nrf7120e/cpuapp` | ALMA-W11x: `--build hello_world -- --board nrf7120dk/nrf7120e/cpuapp` |

Add `/ns` for TF-M, or use `cpuflpr` for the RISC-V coprocessor.

The u-blox RF configuration for this module is pending, so `--rf-config` has
nothing to apply yet and a build is not regulatory compliant.

## MAC address

The u-blox documentation does not describe the ALMA-W1 Wi-Fi or Bluetooth
address yet. `--build bluetooth/beacon --flash --log` prints the Bluetooth
address the firmware uses.
