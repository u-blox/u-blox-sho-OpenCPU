# Module configuration

The vendor SDKs ship RF calibration, TX power tables and flash drivers for the
**vendor's own reference board**. Firmware built that way is not regulatory
compliant on a u-blox module. This folder is where the u-blox replacements are
declared, so applying them is one flag instead of a README procedure:

```bash
ubx-sdk <target> --variant <PART> --region <DOMAIN> --rf-config
ubx-sdk <target> --doctor        # reports whether it is applied
ubx-sdk <target> --mac           # reports the MAC / Bluetooth device address
ubx-sdk <target> --mac-set <ADDR> [--burn]   # use another MAC address
ubx-sdk <target> --list          # vendor examples plus the u-blox ones (ubx/...)
ubx-sdk <target> --build ubx/<name>
```

Every target is described by the same five topics:

| Topic | Profile key | Applied by |
|-------|-------------|------------|
| Output power | `output_power` | `--rf-config` |
| Calibration | `calibration` | `--rf-config` |
| SDK patches | `patches` | `--rf-config` |
| MAC address | `mac` | `--mac`, `--mac-set` |
| u-blox examples | `examples` | `--list`, `--build ubx/<name>` |

The assets are **not** stored here. They stay in the per-module folders u-blox
publishes at the repository root, laid out as `<vendor-sdk>/<module>/`
(`mcuxpresso/iris-w10/`, `ameba-rtos-d/nora-w30/`, `esp-idf/nora-w40/`), and
are referenced by path. One copy, one place to update.

## Status per target

| Target | Status | Covers |
|--------|--------|--------|
| `iris-w10` | ready | Wi-Fi TX power limits, Wi-Fi cal, BT/802.15.4 cal, MFlash driver |
| `nora-w30` | ready | TX power limit tables (W301/W306), build-system swap |
| `nora-w40` | ready | `ubx_phy_cal` component + ESP-IDF PHY init patch (IDF 5.1, 5.5 and 6.2) |
| `nora-w50-w51` | pending | No u-blox assets in this repository yet |
| `nora-b20-b21-b22` | pending | BLE needs no cal table; device address + TX power are manual |
| `alma-b20-b21` | pending | Under development |

## Profile schema

One `profile.json` per target, applied by `scripts/module_config.py`.

```jsonc
{
  "schema": 1,
  "target": "nora-w30",
  "label": "NORA-W30 (Realtek RTL8720DF)",
  "status": "ready",                 // "ready" or "pending"
  "assets": "ameba-rtos-d/nora-w30", // repo-root folder holding the u-blox files
  "source": "README.md",
  "requires": { "sdk_version": ">=5.1,<5.2 || >=6.2,<6.3" },
  "variables": { "flash_vendor": "Macronix" },   // defaults, --set overrides
  "variants": {
    "NORA-W301": { "description": "Antenna pin", "vars": { "rf_para": "W301" } }
  },
  "output_power": [ /* ops, see below */ ],
  "calibration":  [ /* ops */ ],
  "patches":      [ /* ops */ ],
  "regulatory": { "api": "...", "domains": { "ETSI": "0x5E" } },
  "mac": {
    "source": "...",
    "read": "esptool" | "unsupported",
    "write": {
      "runtime": [ "uint8_t mac[6] = {mac_array};", "..." ],   // printed by --mac-set
      "permanent": { "tool": "espefuse", "chip": "esp32c6", "note": "..." }
    }
  },
  "examples": [
    { "name": "rf-calibration", "kind": "project", "path": ".", "description": "..." },
    { "name": "read-mac-address", "kind": "drop-in", "file": "example-code/read-mac-address/main.c",
      "base": "wifi_examples/wifi_test_mode" }
  ],
  "manual_steps": [ "..." ],
  "verify": { "log_contains": "..." }
}
```

`--rf-config` applies `output_power`, then `calibration`, then `patches`. The
split is for people reading the profile and the `--doctor` report; all three
are needed for a compliant build.

### MAC address

`--mac-set <ADDR>` checks the address (unicast, not all-zero) and prints the
`runtime` lines with `{mac}`, `{mac_hex}` and `{mac_array}` filled in. That is
an application-side override, reversible by removing it. `--burn` stores the
address permanently and is only honoured when `permanent.tool` names a host
tool (`espefuse` today); the tool asks for its own confirmation.

### u-blox examples

Examples written by u-blox (or third parties) live in the asset folder, not in
the vendor SDK. `--list` shows them as `ubx/<name>`.

- `project`: a complete project at `path` (relative to `assets`), built in place
  with `--build ubx/<name>`. `--flash` and `--log` use the same name.
  `"needs_rf_config": true` refuses the build until `--rf-config` is applied
  (the NORA-W40 project links against the patched ESP-IDF PHY code).
- `drop-in`: a source `file` that replaces the same-named file in the vendor
  example `base`. The launcher prints the steps instead of editing the SDK.

`src` and `patch` paths are relative to the profile's **`assets` folder**. `dst`, `file`
and `dir` are relative to the **vendor SDK root**. Any `{name}` is substituted
from `variables`, the variant's `vars`, and the built-in `{variant}`.
`tests/test_module_config.py` fails if a `src`, `patch` or example of a ready
profile does not exist, for every variant.

### Operations

| Op | Fields | Behaviour |
|----|--------|-----------|
| `copy` | `src`, `dst` | Always copy. Backs up an existing destination. |
| `replace` | `src`, `dst` | Copy **only if** the destination already exists. Lets one profile carry several SDK-version variants and apply the matching one. |
| `copy-tree` | `src`, `dst` | Replace a whole directory. |
| `replace-line` | `file`, `from`, `to` | Single-line edit, e.g. a makefile. |
| `patch` | `patch`, `dir`, `strip` | `patch -p<strip> -d <dir>`. Falls back to `git apply` with repository discovery disabled, so it also works inside a git checkout. |

Any op may also carry:

- `sdk_version` - only run when the detected SDK version matches. Used to pick
  the patch cut for that SDK release. Commas AND clauses, `||` ORs ranges.
- `warning` - printed with the op, e.g. for an asset not yet re-validated.

`manual_steps` entries are plain strings, or `{ "text": ..., "sdk_version": ... }`
to show a step only for the matching SDK release. SDK versions are detected for
NORA-W40 (`esp_idf_version.h`) and IRIS-W10 (`MCUX_VERSION`, as `YY.MM`).

Every op is idempotent: re-running `--rf-config` reports `already applied`
rather than failing or double-patching.

### Backup and revert

Before a vendor file is overwritten it is copied to `<name>.ubx-orig`, and what
was applied is recorded in `modules/<target>/config/rf_config.json` with a
SHA-256 per file. That gives:

- `--doctor` a drift check: a file changed since apply, or a patch that no
  longer reverses cleanly, is reported.
- `module_config.py <target> revert` a clean undo back to the vendor SDK,
  including deleting files `copy` added that the vendor SDK never had.

## Adding a target or a variant

1. Put the assets in `<vendor-sdk>/<target>/` at the repository root.
2. Set `assets` to that folder, add the variant to `modules/<target>/profile.json`
   with any `vars` the ops need, and flip `status` to `ready`.
3. `python scripts/module_config.py <target> variants` to check the part
   numbers resolve, then `apply` and `revert` to check the ops round-trip.

No change to `scripts/ubx.py` or to any per-target driver is needed.
