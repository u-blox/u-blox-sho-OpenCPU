@echo off
REM ========================================================================
REM ubx-matter.cmd -- Matter launcher (Windows), optional layer
REM ========================================================================
REM Separate from ubx-sdk.cmd on purpose: Matter SDKs are several GB and most
REM users never need them. Thin shim -- picks a Python interpreter (shared
REM .venv first) and forwards every argument to scripts\ubx_matter.py.
REM
REM   ubx-matter.cmd --help
REM   ubx-matter.cmd nora-w40 --doctor
REM   ubx-matter.cmd nora-w40 --clone --build light
REM ========================================================================

setlocal

set "SDK_DIR=%~dp0"
set "SDK_DIR=%SDK_DIR:~0,-1%"
set "UBX_PY=%SDK_DIR%\scripts\ubx_matter.py"

if not exist "%UBX_PY%" (
    echo [FAIL] Not found: %UBX_PY%
    exit /b 1
)

REM A Linux venv in the same folder has no Scripts\python.exe, so this test
REM also keeps a WSL-created .venv from being picked up on Windows.
set "PY="
if exist "%SDK_DIR%\.venv\Scripts\python.exe" set "PY=%SDK_DIR%\.venv\Scripts\python.exe"

if not defined PY (
    for %%P in (py.exe) do if not defined PY if not "%%~$PATH:P"=="" set "PY=py -3"
)
if not defined PY (
    for %%P in (python.exe) do if not defined PY if not "%%~$PATH:P"=="" set "PY=python"
)
if not defined PY (
    echo [FAIL] No Python interpreter found.
    echo        Install Python 3.10+ or run: python scripts\setup_venv.py
    exit /b 1
)

%PY% "%UBX_PY%" %*
exit /b %errorlevel%
