@echo off
REM Build script for NORA-W30 (Realtek RTL8720DF) using WSL2
REM Run this from Windows Command Prompt (cmd.exe)
REM Requires WSL2 with Ubuntu-24.04

echo.
echo [INFO] Building NORA-W30 hello_world example using WSL2
echo [INFO] This uses Realtek Ameba-D SDK
echo [INFO] WSL2 distribution: Ubuntu-24.04
echo.

set SDK_PATH=E:\u-blox\u-blox-sho-OpenCPU\GettingStartedSDK

if not exist "%SDK_PATH%\ameba-rtos-d" (
    echo [FAIL] Could not find ameba-rtos-d SDK
    echo [INFO] Expected at: %SDK_PATH%\ameba-rtos-d
    pause
    exit /b 1
)

echo [INFO] Starting build in WSL2...
echo [INFO] This may take 5-15 minutes on first build (toolchain download)
echo.

REM Call WSL2 to run the build
wsl -d Ubuntu-24.04 bash -c "cd /mnt/e/u-blox/u-blox-sho-OpenCPU/GettingStartedSDK/ameba-rtos-d/project/realtek_amebaD_va0_example/GCC-RELEASE/project_hp && make all"

if %errorlevel% equ 0 (
    echo.
    echo [OK] Build completed successfully in WSL2!
    echo.
    echo [INFO] Firmware files should be in:
    echo   %SDK_PATH%\ameba-rtos-d\project\realtek_amebaD_va0_example\GCC-RELEASE\project_hp\asdk\image\
    echo.
    echo [INFO] Main core firmware: km4_image2_all.bin
    echo [INFO] Low-power core firmware: km0_image2_all.bin
) else (
    echo.
    echo [FAIL] Build failed with error code %errorlevel%
    echo [INFO] See output above for details
    pause
    exit /b %errorlevel%
)

pause
