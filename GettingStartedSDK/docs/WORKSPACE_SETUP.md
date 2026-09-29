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
| Python: IRIS-W10 doctor / clone / build | `scripts/iris_w10_build.py` |
| Python: NORA-W50/W51 build | `scripts/nora_w50_w51_build.py` |
| Python: NORA-W40 clone / build | `scripts/nora_w40_build.py` |
| Python: NORA-W30 build | `scripts/nora_w30_build.py` |
| Python: Setup venv | `scripts/setup_venv.py` |
| Cortex Debug: IRIS-W10 (J-Link / MCU-Link) | RW612 over SWD, port 2331 |
| Cortex Debug: NORA-W50/W51 (XDS110) | JTAG, port 55000 |
| Cortex Debug: NORA-W30 (J-Link) | RTL8721D over SWD, port 2331 |
| Cortex Debug: NORA-W40 (OpenOCD/ESP-Prog) | esp32c6, port 3333 |
| ESP-IDF Monitor: NORA-W40 | `esp-idf/tools/idf.py monitor` |

The Cortex-Debug entries need a running GDB server and a matching `.elf`; they
are starting points, not verified configurations.

IRIS-W10 additionally needs `ARMGCC_DIR` in the environment. Set it in your
shell before launching VS Code, or add an `env` block to the configuration:

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

**Wrong interpreter** — Ctrl+Shift+P → "Python: Select Interpreter" → pick
`GettingStartedSDK/.venv`. If it is missing, run `python scripts/setup_venv.py`
and reload the window.

**A stray `.venv` at the repository root** — run `scripts/migrate_venv.sh` (or
`.bat`) to move it into `GettingStartedSDK/`.

**Windows vs WSL2 venv** — the two are not interchangeable. The launcher probes
for the right one per host and falls back to system Python, but VS Code's
interpreter setting assumes the Linux layout (`.venv/bin/python`); on Windows
select `.venv\Scripts\python.exe` manually.
