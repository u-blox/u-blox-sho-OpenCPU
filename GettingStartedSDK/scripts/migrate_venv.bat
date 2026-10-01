@echo off
REM Helper script to migrate .venv from repo root to GettingStartedSDK/

setlocal enabledelayedexpansion
REM This script lives in GettingStartedSDK\scripts\.
for %%I in ("%~dp0..") do set "SDK_DIR=%%~fI\"
for %%I in ("%SDK_DIR%..") do set "REPO_ROOT=%%~fI\"
set "OLD_VENV=%REPO_ROOT%.venv"
set "NEW_VENV=%SDK_DIR%.venv"

echo.
echo Virtual Environment Migration Helper
echo.

if exist "%OLD_VENV%" (
    echo Found .venv at repo root: %OLD_VENV%
    echo New location should be: %NEW_VENV%
    echo.
    
    if exist "%NEW_VENV%" (
        echo [WARNING] .venv already exists at GettingStartedSDK/
        echo    Remove the old one at repo root? (y/n)
        set /p choice="    > "
        if /i "!choice!"=="y" (
            rmdir /s /q "%OLD_VENV%"
            echo [OK] Old .venv removed
        ) else (
            echo [WARNING] Skipped. You can manually remove it or run setup_venv.py again.
        )
    ) else (
        echo [INFO] Moving .venv to GettingStartedSDK/
        move "%OLD_VENV%" "%NEW_VENV%"
        echo [OK] Virtual environment moved successfully
        echo.
        echo Next step: Activate from GettingStartedSDK directory
        echo   .venv\Scripts\activate.bat  (Windows CMD)
        echo   .venv\Scripts\Activate.ps1  (Windows PowerShell)
        echo   source .venv/Scripts/activate  (Git Bash)
    )
) else (
    echo [OK] No .venv found at repo root
    echo    Virtual environment is already properly located in:
    echo    %NEW_VENV%
)

echo.
pause
