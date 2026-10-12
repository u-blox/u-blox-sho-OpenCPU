# Python virtual environment

The launchers use `getting-started-sdk/.venv` when it exists and fall back to
the system Python otherwise, so the venv is optional. It holds `west`,
`pyserial`, `pylink-square` (J-Link flashing) and `pytest`.

## Create it

```bash
cd getting-started-sdk
python scripts/setup_venv.py        # or: ubx-sdk.cmd --setup-venv
```

On Windows the venv must come from a python.org or Microsoft Store Python, so it
has `.venv\Scripts\python.exe` (the path `ubx-sdk.cmd` looks for). If the
`python` on PATH is MSYS2/MinGW (`C:\msys64\...`), `setup_venv.py` switches to
`py -3` by itself; psutil, needed by pylink-square, has no MinGW wheels.

Windows and WSL2 each need their own venv; one created on the other side is
ignored by the launcher.

## Activation Instructions

Once setup is complete, activate the venv from the getting-started-sdk directory:

**Windows CMD:**
```cmd
cd getting-started-sdk
.venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
cd getting-started-sdk
.venv\Scripts\Activate.ps1
```

**Git Bash / MSYS2:**
```bash
cd getting-started-sdk
source .venv/Scripts/activate
```

**Linux/macOS/WSL:**
```bash
cd getting-started-sdk
source .venv/bin/activate
```

## Troubleshooting

**"pip not found in venv"** or a broken venv: delete it and create it again.

```bash
cd getting-started-sdk
rm -rf .venv          # PowerShell: Remove-Item -Recurse -Force .venv
python scripts/setup_venv.py
```

**`pylink-square could not be installed`**: the venv was made from MSYS2/MinGW
Python. Delete it and rerun `py -3 scripts\setup_venv.py`.
