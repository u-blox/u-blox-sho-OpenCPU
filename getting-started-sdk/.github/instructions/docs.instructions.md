---
description: "Use when writing or editing Getting Started SDK documentation (README, docs/*.md, modules/README.md)."
applyTo: "**/docs/*.md,**/README.md"
---

# Documentation

Keep the docs minimal, yet powerful and useful: the fewest words that let a
new user build, flash and log on the first try.

## Set of documents

- `README.md`: what this is, quick start, `--rf-config`, MAC, Matter in brief,
  setup, tests, links. `docs/QUICK_BUILD_REFERENCE.md`: every flag and the first
  build per target. `docs/<target>_README.md`: one per module.
  `docs/matter_README.md`, `docs/SETUP.md`, `docs/BUILD_TEST_RESULTS.md`,
  `docs/TODO.md`, `modules/README.md`. Nothing else.
- Do not add a new doc. Extend the one that owns the topic; if none does, ask.
- Say each fact once, in the doc that owns it, and link to it from elsewhere.
  Never copy a command table or a feature list into a second doc.

## Module guide (`docs/<target>_README.md`)

Aim for under 120 lines, in this order: a facts table (radio, MCU, memory,
parts, SDK, host), Quick start (with `--rf-config`), notes on the flags that
differ for this target, output path, Flash and log, u-blox files or examples,
MAC address, Troubleshooting table. Leave out generic tutorials (installing
Python or Git, using `idf.py`/`west`/`make` by hand, writing your own app, API
lists): link to the vendor docs instead.

## Rules

- No emoji. Status markers `[OK]` `[FAIL]` `[WARNING]` `[INFO]`.
- Show launcher commands (`./ubx-sdk.sh <target> ...`), not driver scripts. A
  driver call is allowed only for something the launcher cannot do yet, and
  says so.
- Every command shown must work as written. Check how `ubx.py` passes it on
  (only `--build` takes options after `--`) before documenting it.
- Use the canonical target keys; never the old short keys or bare series.
- The documented flag order must match `ubx.ACTION_ORDER` in all three places:
  `README.md`, `docs/QUICK_BUILD_REFERENCE.md`, `.github/copilot-instructions.md`.
- Build numbers (sizes, versions, dates) live only in `docs/BUILD_TEST_RESULTS.md`.
- Hardware facts must match the u-blox MCP; do not copy specs from memory.
- Mark anything not yet verified on hardware as such, in one short sentence.
- Any doc that shows `--build` alone must also say that `--rf-config` is needed
  for a regulatory-compliant build.
- When a doc is removed or renamed, update every link to it.
