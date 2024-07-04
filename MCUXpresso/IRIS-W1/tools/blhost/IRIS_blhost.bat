@echo off

rem Set common timeout
set TIMEOUT=-t 60000

rem Function to show the main menu and prompt for module variant
:main_menu
echo Please select the module variant:
echo 1. Macrionix_8MB
echo 2. Fieldex_8MB
set /p MODULE_CHOICE=Enter choice (1/2): 

if "%MODULE_CHOICE%" equ "1" (
    set MODULE=Macrionix
) else if "%MODULE_CHOICE%" equ "2" (
    set MODULE=Fieldex
) else (
    echo Invalid choice. Exiting...
    goto :end
)
goto :prompt_inputs

rem Function to prompt for user inputs
:prompt_inputs
set /p COM_PORT=Enter COM port number (e.g., COM1): 
set /p BLHOST_PATH=Enter path to blhost.exe (e.g., C:\path\to\blhost.exe): 
goto :execute

rem Function to perform all steps for Macrionix
:macrionix_steps
echo Starting Macrionix steps...
timeout /t 2

echo Step 1: Filling memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- fill-memory 0x20001000 0x4 0xC0000008
if %errorlevel% neq 0 goto :step_failed

echo Step 1 successful.
timeout /t 1

echo Step 2: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if %errorlevel% neq 0 goto :step_failed

echo Step 2 successful.
timeout /t 1

echo Step 3: Flash erasing region...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x18000400 0x200000
if %errorlevel% neq 0 goto :step_failed

echo Step 3 successful.
timeout /t 2

echo Macrionix steps successful.
timeout /t 4
goto :done

rem Function to perform all steps for Fieldex
:fieldex_steps
echo Starting Fieldex steps...
timeout /t 2

echo Step 1: Writing memory...

echo Please Enter path to FCB_FID.bin
set /p FCB_FID=Enter path to FCB_FID.bin (e.g., C:\path\to\FCB_FID.bin): 

%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x20001000 %FCB_FID%
if %errorlevel% neq 0 goto :step_failed

echo Step 1 successful.
timeout /t 1

echo Step 2: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if %errorlevel% neq 0 goto :step_failed

echo Step 2 successful.
timeout /t 1

echo Step 3: Getting property...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- get-property 0x19 0x9
if %errorlevel% neq 0 goto :step_failed

echo Step 3 successful.
timeout /t 1

echo Step 4: Flash erasing region 0x08000000 0x1000...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x1000
if %errorlevel% neq 0 goto :step_failed

echo Step 4 successful.
timeout /t 1

echo Step 5: Filling memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- fill-memory 0x20001000 0x04 0xf000000f
if %errorlevel% neq 0 goto :step_failed

echo Step 5 successful.
timeout /t 1

echo Step 6: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if %errorlevel% neq 0 goto :step_failed

echo Step 6 successful.
timeout /t 1

echo Step 7: Flash erasing region 0x08000000 0x10000...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x10000
if %errorlevel% neq 0 goto :step_failed

echo Step 7 successful.
timeout /t 1

echo Fieldex steps successful.
timeout /t 4
goto :done

:step_failed
echo Step failed.
goto :end

rem Main script execution
:execute
if /i "%MODULE%" equ "Macrionix" (
    call :macrionix_steps
) else if /i "%MODULE%" equ "Fieldex" (
    call :fieldex_steps
)

:done
echo Done.
goto :eof

:end
echo Failed.
goto :eof
