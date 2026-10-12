---
name: ubx-add-target
description: 'Add a new u-blox Open CPU module family (target) to the Getting Started SDK, e.g. ALMA-W1 or a new NORA/IRIS series. Use when: a new module needs build, flash, RF configuration or Matter support; wiring a new driver into ubx-sdk; choosing the target key and folders.'
argument-hint: 'module family and SoC, e.g. "ALMA-W10 on nRF54LM20"'
---

# Add a target

## 1. Decide before writing code

- Confirm with the u-blox MCP (`u-blox-docs`): Open CPU part numbers, SoC,
  vendor SDK, EVK and board target. Do not invent anything the MCP lacks.
- Only Open CPU parts. If the series also has u-connectXpress parts (third
  digit 6/7), they stay out and go into `ubx.UCONNECTXPRESS`.
- Target key = every Open CPU sub-series, lowercase, joined by `-`
  (`nora-w50-w51`). Slug for code = key with `_`.
- Same vendor SDK as an existing target? Reuse that driver with
  `Target.driver_args` (as the two Nordic targets share `nordic_ncs_build.py`)
  instead of copying it.

## 2. Wire it in (every list must get the new key)

| File | What to add |
|------|-------------|
| `scripts/ubx.py` | `TARGETS` entry (`script`, `default_example`, `supports`, `linux_only`, `driver_args`); `ALIASES` for obvious spellings; usage text target table |
| `scripts/target_paths.py` | `TARGETS` (slug -> folder), `LEGACY` (use the new names if there is no old one), `ROOT_SDKS` only if the SDK repo name is fixed |
| `scripts/<slug>_build.py` | new driver following `.github/instructions/python-scripts.instructions.md`; clone into `target_paths.vendor_sdk()` / `sdk_dir()` with `check_space()` |
| `scripts/nordic_ncs_build.py` | `TARGETS` entry instead of a new driver, for nRF Connect SDK modules |
| `scripts/module_config.py` | key in `TARGET_KEYS`; SDK detection in `vendor_sdk_root()` if RF assets exist |
| `modules/<key>/profile.json` | start as `status: pending` with `pending_reason`, `mac.source`, `mac.read` |
| `targets/<key>/{sdk,config}/.gitkeep` | folder skeleton |
| `scripts/matter_build.py` | `TARGETS` entry and `scripts/matter_vendor/<slug>.sh`, only if Matter is wanted |

## 3. Assets and docs

- u-blox files go to `<vendor-sdk>/<key>/` at the repository root, never into
  `getting-started-sdk/`. Coordinate the folder with the asset owner.
- `docs/<slug>_README.md`, plus the target tables in `README.md`,
  `docs/QUICK_BUILD_REFERENCE.md`, `.github/copilot-instructions.md` and
  the repository-root `README.md`.

## 4. Tests

- Most tests parametrize over the target tables, so they pick the new key up;
  run `python -m pytest tests -q` and fix what fails.
- Add tests for any new alias, `driver_args`, special `argv_for` translation
  or `supports` restriction.
- Dry-run the launcher: `./ubx-sdk.sh <key> --dry-run --doctor --clone --build`.

## 5. Prove it

`--doctor`, `--clone`, `--build` of the default example on a real host, then
add the result to `docs/BUILD_TEST_RESULTS.md` and any follow-ups to `docs/TODO.md`.
