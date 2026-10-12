---
description: "Use when editing launcher shims or batch/shell scripts: ubx-sdk.cmd/.sh, ubx-matter.cmd/.sh, scripts/*.bat, scripts/*.sh."
applyTo: "**/*.cmd,**/*.bat,**/ubx-*.sh,**/scripts/*.sh"
---

# Launcher shims and batch files

- `.cmd` and `.bat` must be CRLF. Editing tools write LF, and cmd.exe then
  mangles the first characters of each line (`setlocal` -> `tlocal`).
  Re-normalise after every edit and check bytes 9-10 are `0D 0A`.
- Shims stay thin: pick the shared `.venv` (`Scripts/python.exe` on Windows,
  `bin/python` elsewhere, never the other host's), then forward every argument
  to `scripts/ubx_sdk.py` or `scripts/ubx_matter.py`. Logic belongs in `ubx.py`.
- Write `REM ` with a space; `REM/...` is parsed as a switch.
- Labels cannot live inside `if (...)` blocks; jump out to a label instead.
- Commas, semicolons and `=` split cmd arguments; do not rely on them in values.
