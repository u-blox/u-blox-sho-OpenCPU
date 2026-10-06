# Matter apps

**Optional.** Matter is a self-contained layer on top of the Getting Started
SDK, with its own launcher (`ubx-matter`) and its own SDKs. If you are not
building Matter you can ignore this folder entirely — the plain `ubx-sdk` flow
never reads it and never downloads anything from here.

This folder holds Matter application sources for the four vendor-SDK targets.
Same contract as the plain SDK examples: **nothing large is committed here**.
The Matter SDKs (connectedhomeip, esp-matter, ameba-rtos-matter) are several GB
each and are fetched on demand, so a fresh clone stays small and you only
download the SDK for the module you actually own.

```
matter/
├── IRIS-W1/       NXP RW612 — NXP/matter examples/*/nxp/rt/rw61x (GN)
├── NORA-W3/       Realtek RTL8720DF — ameba-rtos-matter
├── NORA-W4/       Espressif ESP32-C6 — esp-matter
└── NORA-W5/        TI CC3551E — TexasInstruments/matter
```

**NORA-B2 and ALMA-B2 have no folder here, by design.** Matter ships inside the
nRF Connect SDK, so there is no second SDK to fetch and no app sources to keep
in this repo. `ubx-matter` still drives them — it just routes to the NCS driver,
so `--clone` fetches the same workspace `ubx-sdk` uses:

```bash
./ubx-matter.sh nora-b2 --list       # shows the nrf/samples/matter apps
./ubx-matter.sh nora-b2 --build light_bulb --flash --log
```

Because NCS builds natively on Windows, these two never hop into WSL2.

The fetched SDKs land in `targets/<TARGET>/sdk/matter/` (gitignored), or
wherever `UBX_MATTER_ROOT` points.

> **Status:**
>
> | Target | App | State |
> |--------|-----|-------|
> | NORA-W4 | `thermometer` | Ported from `u-connectMatter` `companion/endnode/nora-w40-thermometer` |
> | NORA-W3 | - | Upstream port (`nora-w30-thermometer`) still in progress |
> | IRIS-W1, NORA-W5 | - | No reference app yet |
>
> Thermometer (Matter Temperature Sensor, device type `0x0302`, DS18B20 on
> 1-Wire) is the common app across targets, so the same device can be
> compared on every SoC.

### NORA-W4 thermometer

```bash
./ubx-matter.sh nora-w4 --clone                      # esp-idf v5.5.5 + esp-matter
./ubx-matter.sh nora-w4 --install                    # IDF tools, esp32 submodules, pigweed
./ubx-matter.sh nora-w4 --build thermometer          # Thread SED, DS18B20 on GPIO15
./ubx-matter.sh nora-w4 --build thermometer -- --wifi --clickboard
```

Build options: `--wifi` (Matter over Wi-Fi instead of Thread), `--clickboard`
(DS2482 I2C 1-Wire Click on MikroBUS 1) or `--hvac` (SCD41 Air Quality Sensor).
Images land in `matter/NORA-W4/thermometer/images/`.

The Matter SDK pins ESP-IDF 5.5.5. The u-blox PHY calibration is not applied by
`ubx-matter`; without it the firmware runs on Espressif's default RF data and is
**not regulatory compliant**. Apply it to the Matter ESP-IDF checkout (inside WSL2):

```bash
python3 scripts/module_config.py nora-w4 apply --variant NORA-W401 --region ETSI \
    --sdk "$UBX_MATTER_ROOT/NORA-W4/esp-idf"
```

`module_config.py nora-w4 revert` undoes it. One target keeps one applied state, so
revert the plain SDK first if it is applied there.

## Usage

Matter has its own launcher, `ubx-matter`, kept separate from the plain SDK
launcher so that users who do not need Matter never see it. Same verbs as
`ubx-sdk`, minus the ones that have no Matter equivalent.

```bash
./ubx-matter.sh nora-w4 --doctor     # prerequisites + SDK state
./ubx-matter.sh nora-w4 --clone      # fetch esp-idf + esp-matter
./ubx-matter.sh nora-w4 --list       # list apps in matter/NORA-W4/
./ubx-matter.sh nora-w4 --build thermometer
```

On Windows, `--clone` / `--install` / `--build` / `--clean` hop into WSL2
automatically: Espressif, NXP, Realtek and TI all require a Linux host for
their Matter toolchains. TI additionally supports only Ubuntu 22.04.

### WSL2 and `/mnt/<drive>` paths

esp-matter and connectedhomeip must not be built from a `/mnt/c`-style mount —
the bootstrap is slow and pigweed's symlinks break. Point the SDK checkout at
the WSL filesystem instead:

```bash
export UBX_MATTER_ROOT=~/ubx-matter
./ubx-matter.sh nora-w4 --clone
```

From Windows, `set UBX_MATTER_ROOT=~/ubx-matter` before `ubx-matter.cmd`; the
launcher forwards it into WSL2. An existing ESP-IDF / esp-matter checkout can be
reused by symlinking it as `$UBX_MATTER_ROOT/NORA-W4/esp-idf` and `.../esp-matter`.

## Adding an app

Create `matter/<TARGET>/<app-name>/` with a `build.sh` (and optionally
`build.cmd`) that accepts these verbs:

| Verb | Meaning |
|------|---------|
| `setup` | One-time SDK/tool install for this app |
| `build` | Build the firmware |
| `clean` | Remove build artifacts |

The driver runs the script with the app folder as the working directory and
exports `UBX_MATTER_SDK_ROOT` pointing at the fetched Matter SDKs. Anything
after `--` on the launcher line is appended to `build`.

## SDK versions

| Target | Repositories | Revision |
|--------|--------------|----------|
| IRIS-W1 | `NXP/matter` | `v1.6.0.0.1` |
| NORA-W3 | `Ameba-AIoT/ameba-rtos-d`, `Ameba-AIoT/ameba-rtos-matter` | `master`, `release/v1.5` |
| NORA-W4 | `espressif/esp-idf`, `espressif/esp-matter` | `v5.5.5`, `release/v1.5` |
| NORA-W5 | `TexasInstruments/matter` | `matter-v1.5-ti-1.1` |

All four are `project-chip/connectedhomeip` forks maintained by the silicon
vendor; each is pinned to a tagged release rather than a moving branch so a
clone is reproducible.

### NORA-W5 (TI CC3551E)

`matter-v1.5-ti-1.1` is TI's first general-availability Matter release and is
Matter 1.5 platform-certified for CC35xx. It targets CC3551E on the
LP-EM-CC35X1 launchpad — the same board the plain SDK driver builds for.

- Host: **Ubuntu 22.04 only** (other distributions are unsupported by TI).
- Toolchain: Arm GNU Toolchain 12.3.rel1, CMake 3.21.3.
- Known limitation: no multi-image OTA (Wi-Fi firmware and bootloader
  containers cannot be updated over the air).
- Known issue MATTER-456: a spurious Wi-Fi disconnect can occur on boot once
  the device is commissioned.

Newer `-ea` (early access) tags exist upstream; this project deliberately
pins the GA tag.

Reference implementations for these combinations live in the `u-connectMatter`
repository under `companion/` — port from there rather than starting fresh.
