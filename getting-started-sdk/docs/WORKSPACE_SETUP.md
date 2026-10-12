# VS Code workspace

`ubx.code-workspace` (in `getting-started-sdk/`) is the only workspace file in
this repository. Open it with:

```bash
code getting-started-sdk/ubx.code-workspace
```

It is multi-root, so you get both views at once:

| Folder | Path | Use |
|--------|------|-----|
| getting-started-sdk | `.` | The SDK itself |
| Repository Root (u-blox assets) | `..` | Asset folders and the rest of the repo; the nested `getting-started-sdk` is hidden there |

## What it configures

**Python** — `python.defaultInterpreterPath` points at the shared
`getting-started-sdk/.venv`, and `PYTHONPATH` is set to the SDK folder in all
three integrated-terminal profiles so `scripts/` imports resolve. Create the
venv first if you want it (see [VENV_SETUP.md](VENV_SETUP.md)):

```bash
python scripts/setup_venv.py
```

The launcher works without a venv too, so this is optional.

**Performance** — the multi-GB vendor SDKs under `sdks/` are kept out
of search and the file watcher. `.venv` stays visible on purpose. CMake Tools
does not configure on open; the drivers run CMake themselves.

**Extensions** — Python/Pylance, CMake Tools, Cortex-Debug, GitLab Workflow are
recommended on first open.

## Launch configurations

These call the per-target driver scripts directly, not the `ubx-sdk` launcher,
because their purpose is to debug the drivers themselves. For normal work use
the launcher from a terminal instead.

| Configuration | Runs |
|---------------|------|
| Python: IRIS-W10 doctor / clone / build | `scripts/iris_w10_build.py` |
| Python: NORA-W50-W51 build | `scripts/nora_w50_w51_build.py` |
| Python: NORA-W40 clone / build | `scripts/nora_w40_build.py` |
| Python: NORA-W30 build | `scripts/nora_w30_build.py` |
| Python: Setup venv | `scripts/setup_venv.py` |
| Cortex Debug: IRIS-W10 (J-Link / MCU-Link) | RW612 over SWD, port 2331 |
| Cortex Debug: NORA-W50-W51 (XDS110) | JTAG, port 55000 |
| Cortex Debug: NORA-W30 (J-Link) | RTL8721D over SWD, port 2331 |
| Cortex Debug: NORA-W40 (OpenOCD/ESP-Prog) | esp32c6, port 3333 |
| ESP-IDF Monitor: NORA-W40 | `sdks/esp-idf/master/tools/idf.py monitor` |

The Cortex-Debug entries need a running GDB server and a matching `.elf`; they
are starting points, not verified configurations.

IRIS-W10 finds the Arm GNU Toolchain by itself. To force a specific one, add an
`env` block to the configuration:

```json
"env": {
  "ARMGCC_DIR": "/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
}
```

## Copilot context

Opening `ubx.code-workspace` gives Copilot everything below automatically.
Opening only the repository root does not, because it lives in this folder.

| File | Loaded |
|------|--------|
| `.github/copilot-instructions.md` | Every request: targets, layout, naming, launcher rules |
| `.github/instructions/*.instructions.md` | When matching files are in play: Python scripts/tests, profiles, Matter, shims, docs |
| `.github/skills/ubx-build-flash/` | Building, flashing, troubleshooting a target |
| `.github/skills/ubx-module-config/` | Output power, calibration, patches, MAC, u-blox examples |
| `.github/skills/ubx-add-target/` | Adding a new module family |
| `.vscode/mcp.json` | `u-blox-docs` MCP server: u-blox product documentation search |

Skills also appear as `/ubx-build-flash` etc. in chat. Start the MCP server
once from the MCP view (or when chat asks) so hardware questions are answered
from u-blox documentation. `tests/test_copilot_files.py` keeps the frontmatter
valid and the documented flag order in sync with the launcher.

## Troubleshooting

**Wrong interpreter** — Ctrl+Shift+P -> "Python: Select Interpreter" -> pick
`getting-started-sdk/.venv`. If it is missing, run `python scripts/setup_venv.py`
and reload the window.

**Windows vs WSL2 venv** — the two are not interchangeable. The workspace
points VS Code at the Windows one (`.venv\Scripts\python.exe`); the launcher
picks the right one per host and falls back to system Python.
