---
description: "Use when writing or editing Getting Started SDK documentation (README, docs/*.md, modules/README.md)."
applyTo: "**/docs/*.md,**/README.md"
---

# Documentation

- No emoji. Status markers `[OK]` `[FAIL]` `[WARNING]` `[INFO]`.
- Show launcher commands (`./ubx-sdk.sh <target> ...`), not driver scripts.
- Use the canonical target keys; never the old short keys or bare series.
- The documented flag order must match `ubx.ACTION_ORDER` in all three places:
  `README.md`, `docs/QUICK_BUILD_REFERENCE.md`, `.github/copilot-instructions.md`.
- Build numbers (sizes, versions, dates) live only in `docs/BUILD_TEST_RESULTS.md`.
- Hardware facts must match the u-blox MCP; do not copy specs from memory.
- New docs go in `docs/`; never add files to the SDK root or repository root.
- Any doc that shows `--build` alone must also say that `--rf-config` is needed
  for a regulatory-compliant build.
