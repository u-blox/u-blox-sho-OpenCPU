---
description: "Use when editing the Getting Started SDK Python scripts or tests: launcher core, per-target drivers, module_config, target_paths, pytest suite."
applyTo: "**/scripts/**/*.py,**/tests/**/*.py"
---

# Python scripts and tests

## Script structure

Every per-target driver (`<target>_build.py`, `nordic_ncs_build.py`) follows:

1. `host_kind()` - `windows`, `wsl` or `linux`
2. `detect_*()` - one function per tool; `cmd_doctor()` reports them all
3. `load_config()` / `save_config()` via `target_paths.resolve_config(TARGET)`
   -> `targets/<target>/config/build.<host>.json`
4. `cmd_doctor`, `cmd_clone`, `cmd_install`, `cmd_list`, `cmd_build`, `cmd_clean`,
   `cmd_flash`, `cmd_log`; `main()` at the bottom returns the command's exit code

## Rules

- Anchor paths to `Path(__file__)`, never `Path.cwd()`. Anything under
  `targets/` comes from `target_paths` (`sdk_dir`, `vendor_sdk`, `config_dir`).
- Return 0 on success and non-zero on failure, and propagate it from `main()`.
  A driver that swallows the return code makes every failure look green.
- Output uses `[OK]` `[FAIL]` `[WARNING]` `[INFO]`; no emoji.
- Use `shutil.which`, never shell out to `which` (absent on cmd.exe/PowerShell).
- Every clone calls `target_paths.check_space()` first; `UBX_SKIP_SPACE_CHECK=1`
  overrides. A full drive once produced misleading compiler errors.
- The launcher runs every subprocess through `ubx.execute(ctx, cmd)` so that
  `--dry-run` covers it. Do not call `subprocess` directly in `ubx.py`.
- Never fetch a vendor SDK into the SDK root; use `target_paths.vendor_sdk()`.
- On Windows, `git apply` inside a git checkout skips every path and exits 0
  unless `GIT_CEILING_DIRECTORIES` is set. `module_config._git_apply()` does
  this; keep it.

## Tests

- Hermetic: no vendor SDK, toolchain, WSL2, network or hardware.
- `conftest.calls` replaces `subprocess.call`; the autouse
  `no_sdk_adoption` fixture stops tests from moving the developer's real SDKs.
  Patch new side effects the same way.
- `tests/test_cli.py` runs the real entry points with `--dry-run`.
- Fake SDK trees go under `tmp_path`; monkeypatch `target_paths.SDK_ROOT` /
  `TARGETS_DIR` or `UBX_MATTER_ROOT`, never write into the repository.
- Shim and drive-letter tests are platform-specific and skip on the other host.
- Every new flag, target, alias, profile field or Matter vendor script gets a test.
