# Module configuration

The vendor SDKs ship RF calibration, TX power tables and flash drivers for the
**vendor's own reference board**. Firmware built that way is not regulatory
compliant on a u-blox module. This folder is where the u-blox replacements are
declared, so applying them is one flag instead of a README procedure:

```bash
ubx-sdk <target> --variant <PART> --region <DOMAIN> --rf-config
ubx-sdk <target> --doctor        # reports whether it is applied
ubx-sdk <target> --mac           # reports the MAC / Bluetooth device address
```

The assets are **not** stored here. They stay in the per-module folders u-blox
publishes at the repository root (`NORA-W30-OutputPower/`,
`NORA-W40-OutputPower/`, `MCUXpresso/IRIS-W1/sw_config/`) and are referenced by
path. One copy, one place to update.

## Status per target

| Target | Status | Covers |
|--------|--------|--------|
| `iris-w1` | ready | Wi-Fi TX power limits, Wi-Fi cal, BT/802.15.4 cal, MFlash driver |
| `nora-w3` | ready | TX power limit tables (W301/W306), build-system swap |
| `nora-w4` | ready | `ubx_phy_cal` component + ESP-IDF PHY init patch |
| `nora-w5` | pending | No u-blox assets in this repository yet |
| `nora-b2` | pending | BLE needs no cal table; device address + TX power are manual |
| `alma-b2` | pending | Under development |

## Profile schema

One `profile.json` per target, applied by `scripts/module_config.py`.

```jsonc
{
  "schema": 1,
  "target": "nora-w3",
  "label": "NORA-W3 (Realtek RTL8720DF)",
  "status": "ready",                 // "ready" or "pending"
  "requires": { "sdk_version": ">=5.1,<5.2" },
  "variables": { "flash_vendor": "Macronix" },   // defaults, --set overrides
  "variants": {
    "NORA-W301": { "description": "Antenna pin", "vars": { "rf_para": "W301" } }
  },
  "sdk_patch": [ /* ops, see below */ ],
  "regulatory": { "api": "...", "domains": { "ETSI": "0x5E" } },
  "mac": { "source": "...", "read": "esptool" | "unsupported" },
  "manual_steps": [ "..." ],
  "verify": { "log_contains": "..." }
}
```

`src` and `patch` paths are relative to the **repository root**. `dst`, `file`
and `dir` are relative to the **vendor SDK root**. Any `{name}` is substituted
from `variables`, the variant's `vars`, and the built-in `{variant}`.

### Operations

| Op | Fields | Behaviour |
|----|--------|-----------|
| `copy` | `src`, `dst` | Always copy. Backs up an existing destination. |
| `replace` | `src`, `dst` | Copy **only if** the destination already exists. Lets one profile carry several SDK-version variants and apply the matching one. |
| `copy-tree` | `src`, `dst` | Replace a whole directory. |
| `replace-line` | `file`, `from`, `to` | Single-line edit, e.g. a makefile. |
| `patch` | `patch`, `dir`, `strip` | `patch -p<strip> -d <dir>`. Falls back to `git apply`. |

Every op is idempotent: re-running `--rf-config` reports `already applied`
rather than failing or double-patching.

### Backup and revert

Before a vendor file is overwritten it is copied to `<name>.ubx-orig`, and what
was applied is recorded in `targets/<TARGET>/config/rf_config.json` with a
SHA-256 per file. That gives:

- `--doctor` a drift check: a file changed since apply is reported as changed.
- `module_config.py <target> revert` a clean undo back to the vendor SDK.

## Adding a target or a variant

1. Put the assets in the module's folder at the repository root.
2. Add the variant to `modules/<TARGET>/profile.json` with any `vars` the ops
   need, and flip `status` to `ready`.
3. `python scripts/module_config.py <target> variants` to check the part
   numbers resolve, then `apply` and `revert` to check the ops round-trip.

No change to `scripts/ubx.py` or to any per-target driver is needed.
