---
name: ubx-module-config
description: 'Add or change the u-blox module configuration for a Getting Started SDK target: output power (TX power tables), RF calibration, vendor SDK patches, MAC address read/write, u-blox examples, new part number or variant, new SDK release. Use when: new RF assets from the RF team, a new IRIS/NORA/ALMA part number, re-cutting an ESP-IDF patch, a profile asset path broke, --rf-config / --mac-set / ubx/<example> work.'
argument-hint: '<target> and the change, e.g. "nora-w40 support ESP-IDF 6.3"'
---

# Module configuration (profiles)

Everything here is data in `modules/<target>/profile.json` plus files in the
repository-root asset folder named by the profile's `assets`. Schema:
`modules/README.md`. Rules for editing: `.github/instructions/module-config.instructions.md`.

## Before changing anything

1. Confirm the hardware facts with the u-blox MCP (`u-blox-docs`): part numbers,
   antenna variants, regulatory domains, where the MAC is stored.
2. Run `python scripts/module_config.py <target> variants` and `... status` to
   see the current state.
3. Assets come from u-blox (RF team / application engineering). Never generate
   RF tables or calibration values.

## Add a part number (variant)

1. Add it under `variants` with a `description` and any `vars` the ops use
   (e.g. `rf_para`, `flash_size`).
2. If it needs its own asset, add the file to the asset folder using the
   existing lowercase-hyphen naming.
3. `python -m pytest tests -q` - the asset test expands every op for every variant.

## Add or update RF data

1. Put the file in `<vendor-sdk>/<target>/` at the repository root.
2. Add an op under the right topic:
   - `output_power`: TX power limits, PHY init data
   - `calibration`: Wi-Fi / BT / 802.15.4 calibration
   - `patches`: anything else the SDK needs (flash drivers, build files, hooks)
3. Choose the op: `replace` when the destination must already exist (picks the
   right file per SDK release), `copy` for new files, `copy-tree`,
   `replace-line`, or `patch` (`dir`, `strip`).
4. Gate SDK-specific assets with `sdk_version`. A new SDK release gets a new
   re-cut asset and op; never widen an old range. Add a `warning` when values
   were characterised on a different release.
5. Flip `status` to `ready` only when every variant has real assets.

## New vendor SDK release (example: ESP-IDF patch)

1. Fetch the release into `targets/<target>/sdk/`.
2. Re-cut the patch against it: `ubx_phy_cal_esp_idf_<major>_<minor>.patch`.
3. Add a `patch` op with `sdk_version: ">=X.Y,<X.Y+1"` and extend
   `requires.sdk_version`.
4. Verify for real: `ubx-sdk <target> --variant <PART> --rf-config --build ubx/rf-calibration`,
   then `module_config.py <target> revert`. Record it in `docs/BUILD_TEST_RESULTS.md`.

## MAC address

- `mac.read`: `esptool` or `unsupported`.
- `mac.write.runtime`: lines printed by `--mac-set`, with `{mac}`, `{mac_hex}`,
  `{mac_array}`. Only use APIs found in the vendor SDK headers.
- `mac.write.permanent`: `note`, plus `tool` and `chip` only when a host tool
  can burn it (today `espefuse` for NORA-W40). It must keep its own
  confirmation prompt. OTP addresses programmed by u-blox are never rewritten.

## u-blox examples

- `project`: a complete project in the asset folder (`path`), built in place with
  `--build ubx/<name>`. Set `needs_rf_config: true` if it links against patched SDK code.
- `drop-in`: a single `file` that replaces the same-named file in the vendor
  example `base`; the launcher prints the steps.
- Vendor examples are not listed here; only u-blox or third-party code that
  lives in this repository.

## Done when

- `python -m pytest tests -q` passes (asset existence, topics, MAC parsing).
- `module_config.py <target> apply` then `revert` round-trips on a real SDK.
- `modules/README.md` status table and `docs/<target>_README.md` are updated.
