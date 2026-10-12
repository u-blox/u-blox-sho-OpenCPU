# Setup: Python venv and VS Code

Both are optional. The launchers run with any Python 3.10+.

## Python venv

The launchers use `getting-started-sdk/.venv` when it exists. It holds `west`,
`pyserial`, `pylink-square` (J-Link flashing), `pytest` and `pytest-cov`.

```bash
cd getting-started-sdk
python scripts/setup_venv.py        # or: ubx-sdk.cmd --setup-venv
```

- Windows needs a python.org or Microsoft Store Python, so the venv has
  `.venv\Scripts\python.exe`. If `python` on PATH is MSYS2/MinGW, `setup_venv.py`
  switches to `py -3` by itself.
- Windows and WSL2 each need their own venv; the launcher ignores one made on
  the other side.
- Broken venv, or `pylink-square could not be installed`: delete `.venv` and
  run `py -3 scripts\setup_venv.py` (Windows) or `python3 scripts/setup_venv.py`.

Activate it only for your own shell; the launchers do not need it:
`.venv\Scripts\activate.bat` (cmd), `.venv\Scripts\Activate.ps1` (PowerShell),
`source .venv/bin/activate` (Linux, WSL2, macOS).

## VS Code workspace

```bash
code getting-started-sdk/ubx.code-workspace
```

It opens two roots: the SDK, and the repository root with the u-blox asset
folders. It points Python at `.venv`, keeps `sdks/` out of search and the file
watcher, and recommends Python, Cortex-Debug and the vendor
extensions (nRF Connect, MCUXpresso, ESP-IDF).

The Python launch configurations run the build scripts directly, to debug
them; use the launcher for normal work. "Cortex Debug: NORA-W30 KM4 attach"
attaches to a board flashed with `--flash` and needs `arm-none-eabi-gdb` on the
Windows `PATH`; it has not been verified on hardware yet.

### Vendor extensions

An SDK fetched by the launcher can also be built and debugged in the vendor's
own extension; the module guides say what to open (IRIS-W10, NORA-W40,
NORA-B20-B21-B22, ALMA-B20-B21). Run `--rf-config` once first: it writes the
u-blox RF data into the SDK tree, so extension builds pick it up. An extension
build on an SDK without it is not regulatory compliant. The extension workflow
has not been verified on hardware yet.

NORA-W50-W51 uses TI's Code Composer Studio instead of a VS Code extension
([nora_w50_w51_README.md](nora_w50_w51_README.md#code-composer-studio)).
NORA-W30 has no vendor IDE and stays on the launcher.

If the interpreter is wrong: Ctrl+Shift+P, "Python: Select Interpreter", pick
`getting-started-sdk/.venv`.

## Copilot context

Opening `ubx.code-workspace` loads this automatically:

| File | Loaded |
|------|--------|
| `.github/copilot-instructions.md` | Every request: targets, layout, naming, launcher rules |
| `.github/instructions/*.instructions.md` | When matching files are edited: Python, profiles, Matter, shims, docs |
| `.github/skills/` | `/ubx-build-flash`, `/ubx-module-config`, `/ubx-add-target` |
| `.vscode/mcp.json` | `u-blox-docs` MCP server for u-blox product documentation |
