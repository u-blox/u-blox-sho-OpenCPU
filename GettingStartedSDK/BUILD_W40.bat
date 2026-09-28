@echo off
REM Build script for NORA-W40 (ESP32-C6) hello_world
REM Run this from Windows Command Prompt (cmd.exe) - NOT Git Bash

setlocal

set IDF_PATH=E:\u-blox\u-blox-sho-OpenCPU\GettingStartedSDK\esp-idf
set PROJECT_DIR=%IDF_PATH%\examples\get-started\hello_world

echo.
echo [INFO] Building NORA-W40 hello_world example (ESP32-C6)
echo [INFO] IDF_PATH : %IDF_PATH%
echo [INFO] Project  : %PROJECT_DIR%
echo.

if not exist "%PROJECT_DIR%\CMakeLists.txt" (
    echo [FAIL] Could not find hello_world example at %PROJECT_DIR%
    exit /b 1
)

REM ESP-IDF refuses to run when launched from an MSYS2/Git Bash environment
set MSYSTEM=
set MSYSTEM_CHOST=
set MSYSTEM_PREFIX=
set PYTHONHOME=
set PYTHONPATH=

REM Use a clean PATH: MSYS2's Python cannot create a valid Windows venv for ESP-IDF
set PY_ROOT=C:\Users\cmag\AppData\Local\Python\pythoncore-3.14-64
if not exist "%PY_ROOT%\python.exe" (
    echo [FAIL] System Python not found at %PY_ROOT%
    exit /b 1
)

REM ESP-IDF's installer requires git on PATH
set GIT_DIR_CANDIDATE=
for %%D in (
    "C:\Program Files\Git\cmd"
    "C:\Program Files (x86)\Git\cmd"
    "%LOCALAPPDATA%\Programs\Git\cmd"
    "C:\msys64\usr\bin"
    "C:\msys64\mingw64\bin"
) do if not defined GIT_DIR_CANDIDATE if exist "%%~D\git.exe" set GIT_DIR_CANDIDATE=%%~D

if not defined GIT_DIR_CANDIDATE (
    echo [FAIL] git.exe not found in any known location
    echo [INFO] Install Git for Windows or add it to one of the searched folders
    exit /b 1
)
echo [INFO] Using git from: %GIT_DIR_CANDIDATE%

set PATH=%PY_ROOT%;%PY_ROOT%\Scripts;%GIT_DIR_CANDIDATE%;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SystemRoot%\System32\WindowsPowerShell\v1.0

if not exist "%USERPROFILE%\.espressif\python_env\idf6.2_py3.14_env\Scripts\python.exe" (
    echo [INFO] ESP-IDF Python environment missing - running install.bat ^(this takes a few minutes^)
    call "%IDF_PATH%\install.bat" esp32c6
    if errorlevel 1 (
        echo [FAIL] install.bat failed
        exit /b 1
    )
)

echo [INFO] Setting up ESP-IDF environment...
call "%IDF_PATH%\export.bat"
if errorlevel 1 (
    echo [FAIL] export.bat failed
    exit /b 1
)

cd /d "%PROJECT_DIR%"

echo.
echo [INFO] Selecting target esp32c6...
call idf.py set-target esp32c6
if errorlevel 1 (
    echo [FAIL] set-target failed
    exit /b 1
)

echo.
echo [INFO] Starting build...
call idf.py build
if errorlevel 1 (
    echo [FAIL] Build failed
    exit /b 1
)

echo.
echo [OK] Build completed successfully
echo.
echo [INFO] Output files:
dir "%PROJECT_DIR%\build\hello_world.elf"
dir "%PROJECT_DIR%\build\hello_world.bin"

endlocal
