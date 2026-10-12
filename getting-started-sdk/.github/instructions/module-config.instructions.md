---
description: "Use when editing module profiles (modules/*/profile.json), module_config.py or the u-blox RF assets: output power, calibration, SDK patches, MAC address, u-blox examples."
applyTo: "**/modules/**,**/scripts/module_config.py"
---

# Module configuration profiles

`modules/<target>/profile.json` is data; `scripts/module_config.py` is the only
code that applies it. Schema reference: `modules/README.md`.

## Topics

| Key | Meaning | Applied by |
|-----|---------|------------|
| `output_power` | TX power limit tables, PHY init data | `--rf-config` |
| `calibration` | Wi-Fi / BT / 802.15.4 calibration data | `--rf-config` |
| `patches` | other vendor-SDK changes (flash drivers, build files, PHY hooks) | `--rf-config` |
| `mac` | `read`, `write.runtime` lines, optional `write.permanent` tool | `--mac`, `--mac-set [--burn]` |
| `examples` | u-blox examples, `kind: project` or `drop-in` | `--list`, `--build ubx/<name>` |

`--rf-config` applies `output_power`, `calibration`, `patches` in that order.

## Rules

- `assets` names the repository-root folder (`esp-idf/nora-w40`); `src`,
  `patch`, `source`, example `path`/`file` are relative to it. `dst`, `file`
  (in ops) and `dir` are relative to the vendor SDK root.
- Never copy assets into `modules/`. One copy, at the repository root.
- Ops: `copy`, `replace` (only if the destination exists, which selects the
  SDK-version asset), `copy-tree`, `replace-line`, `patch`. Each must stay
  idempotent and carry earlier `backups` forward, or `revert` breaks.
- Pick an SDK-specific asset with a per-op `sdk_version` (`">=5.1,<5.2 || >=6.2,<6.3"`).
  For a new SDK release add a re-cut asset; do not widen an existing range.
- `status: pending` profiles have no variants and claim nothing. Only flip to
  `ready` when real u-blox assets exist.
- MAC `write.runtime` lines use `{mac}`, `{mac_hex}`, `{mac_array}`. Only list
  APIs confirmed in the vendor SDK headers. `permanent.tool` is set only when a
  host tool exists (today `espefuse`); it must ask for its own confirmation -
  never pass a "do not confirm" flag.
- `needs_rf_config: true` on an example that links against patched SDK code.
- Without `--rf-config` firmware is not regulatory compliant. Never weaken that
  message.
- `tests/test_module_config.py` checks that every asset and example of a ready
  profile exists for every variant; keep it passing.
