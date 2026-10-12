# Getting Started SDK - Copilot instructions

Always-on context for `getting-started-sdk/`. Task procedures are skills in
`.github/skills/`; rules for specific files are in `.github/instructions/`.

## Style

- Concise and technical. No emoji in code, script output or docs.
- Docs stay minimal, yet powerful and useful: a fixed set of documents, each
  fact in one place, launcher commands only. Rules in
  `.github/instructions/docs.instructions.md`.
- Status markers are plain text: `[OK]` `[FAIL]` `[WARNING]` `[INFO]`.
- Chat replies: when a reply or summary is longer than a screen, start it with
  a `TL;DR` of 2-4 lines: what changed, whether it works, and anything the
  user must decide or do. Never leave an open question or a required action
  only at the bottom.

## What this is

One launcher, `ubx-sdk`, fetches the vendor SDK, applies the u-blox RF
configuration, builds, flashes and logs for six u-blox Open CPU module
families. An optional second launcher, `ubx-matter`, builds the vendors' own
Matter examples on the same silicon.

| Target | Open CPU parts | SoC | Vendor SDK | Board target |
|--------|----------------|-----|------------|--------------|
| `iris-w10` | IRIS-W10x | NXP RW612/RW610 | MCUXpresso (west) | `rdrw612bga` |
| `nora-w30` | NORA-W30x | Realtek RTL8720DF | Ameba-D (Linux/WSL2 only) | - |
| `nora-w40` | NORA-W40x | Espressif ESP32-C6 | ESP-IDF | `esp32c6` |
| `nora-w50-w51` | NORA-W50x/W51x | TI CC3501E/CC3551E | SimpleLink Wi-Fi | `LP_EM_CC35X1` |
| `nora-b20-b21-b22` | NORA-B20x/B21x/B22x | Nordic nRF54L15/L10/L05 | nRF Connect SDK | `ubx_evknorab2/nrf54l15/cpuapp` |
| `alma-b20-b21` | ALMA-B20x/B21x | Nordic nRF54LM20A/B | nRF Connect SDK | `nrf54lm20dk/nrf54lm20a/cpuapp` |

The third digit of the part number decides the product line. Only Open CPU
parts are built here. NORA-W36x, W56x, W57x, B26x and B27x are u-connectXpress
(pre-flashed AT-command firmware) and cannot be built from this SDK; `ubx.py`
explains this when someone types one of them.

## Hardware facts come from the u-blox MCP

The workspace configures the `u-blox-docs` MCP server (`.vscode/mcp.json`). Use
its knowledge search for module capabilities, pinout, regulatory limits, part
numbers, OTP/eFuse/UICR layout and application notes. When it disagrees with a
comment in this repository, the MCP wins. Never invent a spec; say so when the
MCP has no data (ALMA-W1, a u-blox ALMA-B20-B21 board).

Fixed facts that were wrong before:
- NORA-W40 is ESP32-C6. ESP32-S3 is NORA-W1/W2, not this SDK.
- ALMA-B20-B21 has no `ubx_evkalmab2` board yet; it builds for Nordic's DK.

## Layout

```
u-blox-sho-OpenCPU/                  repository root
├── esp-idf/nora-w40/                u-blox files only (RF data, patches, example project)
├── mcuxpresso/iris-w10/             u-blox files only (calibration, flash drivers, examples)
├── ameba-rtos-d/nora-w30/           u-blox files only (TX power tables)
├── zephyr/, nrf5-sdk/               u-blox board files
└── getting-started-sdk/             the tooling (workspace root)
    ├── ubx-sdk.cmd/.sh, ubx-matter.cmd/.sh, ubx.code-workspace, README.md
    ├── scripts/                     ubx.py (launcher core), per-target drivers, module_config.py
    ├── modules/<target>/profile.json   what the u-blox configuration is, per target
    ├── modules/<target>/config/     cached paths, RF-config state (gitignored)
    ├── sdks/<vendor>/<version>/     vendor SDK, fetched on demand (gitignored)
    ├── tests/                       hermetic pytest suite
    └── docs/
```

- Repository-root folders are named after an SDK but hold only u-blox files.
  The SDK is never cloned there. Profiles point at them through `assets`;
  nothing is copied into `modules/`.
- Vendor SDKs live only in `sdks/<vendor>/<version>/` (`esp-idf/master`,
  `ameba-rtos-d/main`, ...); `<version>` is the fetched branch or tag, so
  versions sit side by side and the path cached in `build.<host>.json` picks
  one. `scripts/target_paths.py` is the single source of truth. Exceptions: nRF
  Connect SDK in `C:\ncs\<rev>` or `~/ncs/<rev>`, Matter SDKs in
  `~/ubx-matter/<target>` inside WSL2, and any SDK fetched inside WSL2 from a
  `/mnt/<drive>` checkout, which goes to `~/ubx-sdk/sdks/<vendor>/<version>`
  for speed (`UBX_SDKS_DIR` overrides).
- Only `README.md`, `.gitattributes`, `.gitlab-ci.yml` and
  `.github/workflows/` may sit at the
  repository root besides the asset folders. The SDK root holds only the two
  launcher pairs, `ubx.code-workspace`, `README.md` and the folders above.

## Naming

- Target keys list every Open CPU sub-series: `iris-w10`, `nora-w30`,
  `nora-w40`, `nora-w50-w51`, `nora-b20-b21-b22`, `alma-b20-b21`. The same key
  names `modules/`, asset folders and `~/ubx-matter/`. Python and
  doc file names use `_` (`nora_w50_w51_build.py`).
- Never use a bare series (`nora-w3`, `nora-b2`) as a target key or alias; it
  also covers u-connectXpress parts. `ubx.py` rejects them.
- Never add a `nora-w1` target: NORA-W1 is an ESP32 module outside this SDK.
- Do not rename EVK names (`EVK-IRIS-W1`), u-blox URLs or Zephyr board ids.
- Shared by both launchers: plain `ubx` (`ubx.py`); layer-specific: suffixed
  (`ubx-sdk.*`, `ubx-matter.*`).

## Launcher behaviour

- Suggest `ubx-sdk.cmd <target> ...` (Windows) or `./ubx-sdk.sh <target> ...`,
  not `python scripts/<driver>.py`. Drivers are run directly only to debug them.
- Flags combine and always run in this order: `--doctor` `--clone` `--install`
  `--build-sdk` `--rf-config` `--list` `--clean` `--build` `--flash` `--mac-set`
  `--mac` `--log`. Everything after `--` goes verbatim to the driver's build
  step (`--build` only). A failing `--doctor` does not stop `--clone`/`--install`.
- `--rf-config`, `--mac-set`, `--mac` and the u-blox examples (`ubx/<name>`)
  are driven by `modules/<target>/profile.json` through `module_config.py`.
  Supporting a new part number, asset or example is a profile edit, never a
  per-target branch in `ubx.py` or a driver.
- Firmware built without `--rf-config` uses the vendor's reference-board RF
  data and is not regulatory compliant on a u-blox module. Never describe a
  plain `--build` as production-ready.
- NORA-W30 and all vendor-SDK Matter actions hop into WSL2 automatically.
  The Nordic targets build natively on Windows and never hop. When a WSL2 run
  fails, suggest restarting WSL2 from an Administrator prompt:
  `net stop vmcompute` then `net start vmcompute`.
- Matter is a separate launcher with vendor examples only; no u-blox Matter
  application code lives here.

## Working rules

- Build, flash, clean and log only through the launcher (`ubx-sdk.cmd` /
  `./ubx-sdk.sh`), also when testing on real hardware. No manual `make`,
  `west`, `idf.py`, `wsl ... python scripts/<driver>.py`, file deletion in
  `sdks/` or hand-written flash commands. When the launcher cannot do a step or
  does it wrong, fix the launcher or driver (with a test), then rerun it.

- Tests: `python -m pytest tests -q` from the SDK root. Hermetic: no SDK,
  toolchain, WSL2 or hardware. Add a test with every new flag, target, alias,
  profile field or Matter vendor script. CI runs it on Python 3.10 and 3.14,
  on Linux (GitLab) and Linux + Windows (GitHub Actions on the mirror).
- Lint: `ruff check --isolated --target-version py310 --select E4,E7,E9,F scripts tests`
  and `shellcheck -S warning ubx-*.sh scripts/matter_vendor/*.sh` must pass; both
  run in CI with the same pinned rules. Keep the commands identical in
  `.gitlab-ci.yml`, the GitHub workflow and `README.md`.
- `.cmd` and `.bat` files must stay CRLF; editing tools write LF. Re-normalise
  after every edit.
- `docs/BUILD_TEST_RESULTS.md` is the only record of real builds. Update it
  after a build; do not copy its numbers elsewhere.
- Open work is tracked in `docs/TODO.md`.

## Where to look

| Task | Start here |
|------|------------|
| Build, flash, log, troubleshoot a target | skill `ubx-build-flash` |
| RF calibration, TX power, SDK patches, MAC, u-blox examples, new part number | skill `ubx-module-config`, `modules/README.md` |
| Add a new module family / target | skill `ubx-add-target` |
| Matter | `docs/matter_README.md` |
| Per-module detail | `docs/<target>_README.md` |
| Flag cheat sheet | `docs/QUICK_BUILD_REFERENCE.md` |
