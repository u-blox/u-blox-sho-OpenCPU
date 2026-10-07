# VS Code workspace

`ubx.code-workspace` (in `GettingStartedSDK/`) is the only workspace file in
this repository. Open it with:

```bash
code GettingStartedSDK/ubx.code-workspace
```

It is multi-root, so you get both views at once:

| Folder | Path | Use |
|--------|------|-----|
| GettingStartedSDK (Build Scripts & Infrastructure) | `.` | The SDK itself |
| Repository Root (Documentation & Extras) | `..` | Everything else in the repo |

## What it configures

**Python** — `python.defaultInterpreterPath` points at the shared
`GettingStartedSDK/.venv`, and `PYTHONPATH` is set to the SDK folder in all
three integrated-terminal profiles so `scripts/` imports resolve. Create the
venv first if you want it (see [VENV_SETUP.md](VENV_SETUP.md)):

```bash
python scripts/setup_venv.py
```

The launcher works without a venv too, so this is optional.

**Performance** — the multi-GB vendor SDKs are kept out of search, the file
watcher and (for `mcuxpresso-sdk` / `esp-idf`) the explorer:
`targets/*/sdk/**`, `ameba-rtos-d`, `esp-idf`, `mcuxpresso-sdk`, `.venv`.
`.venv` and `ameba-rtos-d` stay visible in the explorer on purpose.

**Extensions** — Python/Pylance, CMake Tools, Cortex-Debug, GitLab Workflow are
recommended on first open.

## Launch configurations

These call the per-target driver scripts directly, not the `ubx-sdk` launcher,
because their purpose is to debug the drivers themselves. For normal work use
the launcher from a terminal instead.

| Configuration | Runs |
|---------------|------|
| Python: IRIS-W1 doctor / clone / build | `scripts/iris_w1_build.py` |
| Python: NORA-W5 build | `scripts/nora_w5_build.py` |
| Python: NORA-W4 clone / build | `scripts/nora_w4_build.py` |
| Python: NORA-W3 build | `scripts/nora_w3_build.py` |
| Python: Setup venv | `scripts/setup_venv.py` |
| Cortex Debug: IRIS-W1 (J-Link / MCU-Link) | RW612 over SWD, port 2331 |
| Cortex Debug: NORA-W5 (XDS110) | JTAG, port 55000 |
| Cortex Debug: NORA-W3 (J-Link) | RTL8721D over SWD, port 2331 |
| Cortex Debug: NORA-W4 (OpenOCD/ESP-Prog) | esp32c6, port 3333 |
| ESP-IDF Monitor: NORA-W4 | `esp-idf/tools/idf.py monitor` |

The Cortex-Debug entries need a running GDB server and a matching `.elf`; they
are starting points, not verified configurations.

IRIS-W1 finds the Arm GNU Toolchain by itself. To force a specific one, add an
`env` block to the configuration:

```json
"env": {
  "ARMGCC_DIR": "/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
}
```

## Copilot context

`GettingStartedSDK/.github/copilot-instructions.md` is picked up automatically
when the SDK folder is in the workspace. It documents the launcher, the target
matrix and the layout rules.

## Troubleshooting

**Wrong interpreter** — Ctrl+Shift+P -> "Python: Select Interpreter" -> pick
`GettingStartedSDK/.venv`. If it is missing, run `python scripts/setup_venv.py`
and reload the window.

**A stray `.venv` at the repository root** — run `scripts/migrate_venv.sh` (or
`.bat`) to move it into `GettingStartedSDK/`.

**Windows vs WSL2 venv** — the two are not interchangeable. The launcher probes
for the right one per host and falls back to system Python, but VS Code's
interpreter setting assumes the Linux layout (`.venv/bin/python`); on Windows
select `.venv\Scripts\python.exe` manually.
