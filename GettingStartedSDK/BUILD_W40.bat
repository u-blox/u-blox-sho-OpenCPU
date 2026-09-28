@echo off
REM Build script for NORA-W40 (ESP32-C6) hello_world
REM Run this from Windows Command Prompt (cmd.exe)

echo.
echo [INFO] Building NORA-W40 hello_world example
echo [INFO] This is ESP-IDF for ESP32-C6
echo.

cd /d E:\u-blox\u-blox-sho-OpenCPU\GettingStartedSDK\esp-idf\examples\get-started\hello_world

if not exist "CMakeLists.txt" (
    echo [FAIL] Could not find hello_world example
    echo [INFO] Current directory: %cd%
    pause
    exit /b 1
)

echo [INFO] Starting build...
echo.

idf.py build

if %errorlevel% equ 0 (
    echo.
    echo [OK] Build completed successfully!
    echo.
    echo [INFO] Output files:
    dir build\hello_world.elf
    dir build\hello_world.bin
    echo.
    echo [OK] Firmware ready at:
    echo   - build\hello_world.elf
    echo   - build\hello_world.bin
) else (
    echo.
    echo [FAIL] Build failed with error code %errorlevel%
    pause
    exit /b %errorlevel%
)

pause
