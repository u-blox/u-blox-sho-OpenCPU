---
description: "Use when editing the Matter layer: ubx-matter launcher, matter_build.py, matter_vendor scripts, Matter docs."
applyTo: "**/scripts/matter_build.py,**/scripts/matter_vendor/**,**/ubx-matter.*,**/docs/matter_README.md"
---

# Matter layer

- Separate launcher on purpose: `ubx-sdk --help` lists no Matter flags and
  `ubx-sdk <target> --matter` fails with a pointer to `ubx-matter`.
  `ubx_matter.py` calls `ubx.main(matter=True)`.
- Vendor examples only. No u-blox Matter application code and no `matter/`
  folder; custom apps live in u-connectMatter.
- Vendor-SDK targets (IRIS-W10, NORA-W30, NORA-W40, NORA-W50-W51) are
  Linux-only. Every action, including `--doctor` and `--list`, hops into WSL2.
  SDKs go to `~/ubx-matter/<target>` inside WSL2 (`UBX_MATTER_ROOT` overrides),
  never under `/mnt/<drive>`.
- NORA-W50-W51 hops into the `Ubuntu-22.04` distro (`Target.matter_wsl_distro`,
  `UBX_WSL_DISTRO` overrides). TI Matter needs Python 3.11 and user-installed
  SysConfig and Wi-Fi Toolbox under `~/ti`.
- The Nordic targets get Matter from `nrf/samples/matter/*` in the same NCS
  workspace, are routed to `nordic_ncs_build.py`, and never hop.
- Pins are tagged releases, not moving branches; the table is in
  `docs/matter_README.md`.
- `matter_build.py` lists `MatterTarget.examples`; building goes through
  `scripts/matter_vendor/<target>.sh setup|build <dir>|clean <dir>`. A target
  without that script is list-only.
- `--rf-config` does not cover the Matter SDK checkout automatically; use
  `module_config.py <target> apply --sdk <path>`.
