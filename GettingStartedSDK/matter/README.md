# Matter apps

**Optional.** Matter is a self-contained layer on top of the Getting Started
SDK: its own launcher (`ubx-matter`), its own driver, its own SDKs. If you are
not building Matter you can ignore this folder entirely — the plain `ubx-sdk`
flow never reads it and never downloads anything from here.

Matter application sources for the four Getting Started SDK targets. Same
contract as the plain SDK examples: **nothing large is committed here**. The
Matter SDKs (connectedhomeip, esp-matter, ameba-rtos-matter) are several GB
each and are fetched on demand, so a fresh clone stays small and you only
download the SDK for the module you actually own.

```
matter/
├── IRIS-W10/       NXP RW612 — connectedhomeip examples/*/nxp/rt/rw61x (GN)
├── NORA-W30/       Realtek RTL8720DF — ameba-rtos-matter
├── NORA-W40/       Espressif ESP32-C6 — esp-matter
└── NORA-W50-W51/   TI CC35XX — no public Matter SDK yet
```

The fetched SDKs land in `targets/<TARGET>/sdk/matter/` (gitignored), or
wherever `UBX_MATTER_ROOT` points.

## Usage

Matter has its own launcher, `ubx-matter`, kept separate from the plain SDK
launcher so that users who do not need Matter never see it. Same verbs as
`ubx-sdk`, minus the ones that have no Matter equivalent.

```bash
./ubx-matter.sh nora-w40 --doctor     # prerequisites + SDK state
./ubx-matter.sh nora-w40 --clone      # fetch esp-idf + esp-matter
./ubx-matter.sh nora-w40 --list       # list apps in matter/NORA-W40/
./ubx-matter.sh nora-w40 --build thermometer
```

On Windows, `--clone` / `--install` / `--build` / `--clean` hop into WSL2
automatically: Espressif, NXP and Realtek all require a Linux host for their
Matter toolchains.

### WSL2 and `/mnt/<drive>` paths

esp-matter and connectedhomeip must not be built from a `/mnt/c`-style mount —
the bootstrap is slow and pigweed's symlinks break. Point the SDK checkout at
the WSL filesystem instead:

```bash
export UBX_MATTER_ROOT=~/ubx-matter
./ubx-matter.sh nora-w40 --clone
```

## Adding an app

Create `matter/<TARGET>/<app-name>/` with a `build.sh` (and optionally
`build.cmd`) that accepts these verbs:

| Verb | Meaning |
|------|---------|
| `setup` | One-time SDK/tool install for this app |
| `build` | Build the firmware |
| `clean` | Remove build artifacts |

The driver runs the script with the app folder as the working directory and
exports `UBX_MATTER_SDK_ROOT` pointing at the fetched Matter SDKs.

## SDK versions

| Target | Repositories | Revision |
|--------|--------------|----------|
| IRIS-W10 | `project-chip/connectedhomeip` | `master` |
| NORA-W30 | `Ameba-AIoT/ameba-rtos-d`, `Ameba-AIoT/ameba-rtos-matter` | `master`, `release/v1.5` |
| NORA-W40 | `espressif/esp-idf`, `espressif/esp-matter` | `v5.4.1`, `release/v1.5` |
| NORA-W50/W51 | — | TI has not published a CC35XX Matter SDK |

Reference implementations for these combinations live in the `u-connectMatter`
repository under `companion/` — port from there rather than starting fresh.
