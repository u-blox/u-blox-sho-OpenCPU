# Matter (optional)

Matter is a self-contained layer on top of the Getting Started SDK, with its own
launcher (`ubx-matter`) and its own SDKs. If you are not building Matter you can
ignore it entirely; the plain `ubx-sdk` flow never touches it.

This layer adds **no u-blox application code**. It fetches each vendor's Matter
SDK and lists and builds only the examples that SDK ships. What you can build
therefore differs per target; `--list` is the source of truth.

```bash
./ubx-matter.sh nora-w4 --doctor     # prerequisites + SDK state
./ubx-matter.sh nora-w4 --clone      # fetch the vendor Matter SDK
./ubx-matter.sh nora-w4 --install    # one-time setup: submodules, bootstrap, tools
./ubx-matter.sh nora-w4 --list       # the vendor's Matter examples
./ubx-matter.sh nora-w4 --build light
```

`--build` without a name builds the target's default example. Anything after
`--` goes to the vendor build: GN args for TI, `idf.py` options for Espressif.

| Target | Examples come from | Default | `--build` |
|--------|--------------------|---------|-----------|
| IRIS-W1 | `connectedhomeip/examples/*/nxp/rt/rw61x` | `lighting-app` | listed only |
| NORA-W3 | `ameba-rtos-matter/examples/*` | `light` | listed only |
| NORA-W4 | `esp-matter/examples/*` | `light` | yes |
| NORA-W5 | `ti-matter/examples/*/ti/cc35xx` | `lighting-app` | yes |
| NORA-B2, ALMA-B2 | `nrf/samples/matter/*` (NCS) | `light_bulb` | yes, plus `--flash`/`--log` |

A light is the one example every vendor ships, so it is the one to use when
comparing targets.

The per-vendor setup and build steps live in `scripts/matter_vendor/<target>.sh`
(`setup`, `build <example-dir>`, `clean <example-dir>`). Wiring up IRIS-W1 or
NORA-W3 means adding a script there and setting `vendor_script` in
`scripts/matter_build.py`.

## Where the SDKs go

The vendor Matter toolchains are Linux-only, so on Windows every `ubx-matter`
action for these four targets hops into WSL2. The SDKs are cloned to
`~/ubx-matter/<TARGET>` inside WSL2, because connectedhomeip and esp-matter must
not be built from a `/mnt/<drive>` path. Set `UBX_MATTER_ROOT` to use another
location; the launcher forwards it into WSL2.

NORA-W5 runs in the `Ubuntu-22.04` distro because TI supports nothing else. The
other targets use your default distro. Override with `UBX_WSL_DISTRO`.

NORA-B2 and ALMA-B2 get Matter from the nRF Connect SDK itself, so `--clone`
fetches the same NCS workspace `ubx-sdk` uses and they build natively on Windows.

## SDK versions

| Target | Repositories | Revision |
|--------|--------------|----------|
| IRIS-W1 | `NXP/matter` | `v1.6.0.0.1` |
| NORA-W3 | `Ameba-AIoT/ameba-rtos-d`, `Ameba-AIoT/ameba-rtos-matter` | `master`, `release/v1.5` |
| NORA-W4 | `espressif/esp-idf`, `espressif/esp-matter` | `v5.5.5`, `release/v1.5` |
| NORA-W5 | `TexasInstruments/matter` | `matter-v1.5-ti-1.1` |

All four are `project-chip/connectedhomeip` forks maintained by the silicon
vendor, each pinned to a tagged release so a clone is reproducible.

### NORA-W4 (ESP32-C6)

`--install` installs the ESP-IDF tools for esp32c6, fetches only the esp32 and
linux connectedhomeip submodules and runs the esp-matter bootstrap.

The u-blox PHY calibration is not applied by `ubx-matter`; without it the
firmware runs on Espressif's default RF data and is **not regulatory
compliant**. Apply it to the Matter ESP-IDF checkout (inside WSL2):

```bash
python3 scripts/module_config.py nora-w4 apply --variant NORA-W401 --region ETSI \
    --sdk ~/ubx-matter/NORA-W4/esp-idf
```

`module_config.py nora-w4 revert` undoes it. One target keeps one applied state,
so revert the plain SDK first if it is applied there.

### NORA-W5 (TI CC3551E)

`matter-v1.5-ti-1.1` is TI's GA Matter release, Matter 1.5 platform-certified
for CC35xx, targeting CC3551E on the LP-EM-CC35X1 LaunchPad. TI ships one CC35xx
example: `lighting-app`.

- Host: **Ubuntu 22.04 only**. Matter 1.5's Python tooling needs Python 3.11,
  which 22.04 lacks; `--install` uses `python3.11` from the deadsnakes PPA.
- Install these yourself under `~/ti` inside WSL2 (TI downloads):
  - SysConfig 1.26.3 for Linux - ti.com/tool/SYSCONFIG
  - SimpleLink Wi-Fi Toolbox 4.2.4 for Linux - ti.com/tool/SIMPLELINK-WIFI-TOOLBOX
  Or point `TI_SYSCONFIG_ROOT` / `TI_WIFI_TOOLBOX_ROOT` at them.
- `--install` checks out only the cc35xx and linux submodules, bootstraps the
  Matter environment, downloads Arm GNU Toolchain 12.3.rel1 into `~/ti` and
  builds the SimpleLink Wi-Fi SDK libraries.
- Flash with the Wi-Fi Toolbox programmer using `out/debug/tool_settings.json`.
- Known limitation: no multi-image OTA. Known issue MATTER-456: a spurious
  Wi-Fi disconnect can occur on boot once the device is commissioned.

Newer `-ea` (early access) tags exist upstream; this project pins the GA tag.
