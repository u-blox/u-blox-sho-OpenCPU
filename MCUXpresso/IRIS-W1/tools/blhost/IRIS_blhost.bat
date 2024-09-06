@echo off

rem Set common timeout
set TIMEOUT=-t 60000

rem Function to show the main menu and prompt for module variant
:main_menu
echo Please select the module variant:
echo 1. Macronix_8MB
echo 2. Fidelix_8MB
set /p MODULE_CHOICE=Enter choice (1/2): 

if "%MODULE_CHOICE%" equ "1" (
    set MODULE=Macronix
) else if "%MODULE_CHOICE%" equ "2" (
    set MODULE=Fidelix
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

rem Function to perform all steps for Macronix
:macronix_steps
echo Starting Macronix steps...
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

echo Step 3: Flash erasing region for FW .bin...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08400000 0x1DFFFF
if %errorlevel% neq 0 goto :step_failed

echo Step 3 successful.
timeout /t 2

set /p M_FW_BIN=Enter path to FW .bin (applicable on radio FW if not please press Enter to continue) (e.g., C:\path\to\rw612XX_wifi_aXX.bin): 

if not "%M_FW_BIN%"=="" (
    echo Step 4: Writing FW .bin to memory...
    timeout /t 2
    "%BLHOST_PATH%" -p %COM_PORT% %TIMEOUT% -- write-memory 0x08400000 "%M_FW_BIN%"

    if %errorlevel% neq 0 goto :step_failed

    echo Step 4 successful.
) else (
    echo No firmware binary path provided. Skipping blhost execution.
    timeout /t 2
)

echo Step 5: Flash erasing region...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x3FFFFF
if %errorlevel% neq 0 goto :step_failed

echo Step 5 successful.
timeout /t 2

rem New Step: Prompt for application .bin location
set /p APP_BIN=Enter path to application .bin (e.g., hello_world.bin/wifi_cli.bin, C:\path\to\hello_world.bin): 

echo Step 6: Writing application .bin to memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x08000000 %APP_BIN%
if %errorlevel% neq 0 goto :step_failed

echo Step 6 successful.
timeout /t 1

echo Macronix steps successful.
timeout /t 5

goto :done

rem Function to perform all steps for Fidelix
:fidelix_steps
echo Starting Fidelix steps...
timeout /t 2

rem Step 1: Writing FCB_FID.bin to memory
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

echo Step 4: Flash erasing region 0x08000000 
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x3FFFFF
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

echo Step 7: Flash erasing region 0x08400000 
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08400000 0x1DFFFF
if %errorlevel% neq 0 goto :step_failed

echo Step 7 successful.
timeout /t 1

set /p F_FW_BIN=Enter path to FW .bin (e.g., C:\path\to\rw612XX_aXX.bin): 

if not "%F_FW_BIN%"=="" (
    echo Step 8: Writing FW .bin to memory...
    timeout /t 2
    "%BLHOST_PATH%" -p %COM_PORT% %TIMEOUT% -- write-memory 0x08400000 "%F_FW_BIN%"

    if %errorlevel% neq 0 goto :step_failed

    echo Step 8 successful.
) else (
    echo No firmware binary path provided. Skipping blhost execution.
    timeout /t 2
)


echo Step 9: Flash erasing region 0x08000000 
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x3FFFFF
if %errorlevel% neq 0 goto :step_failed

echo Step 9 successful.
timeout /t 1


rem New Step: Prompt for application .bin location
set /p F_APP_BIN=Enter path to application .bin (e.g., hello_world.bin/wifi_cli.bin, C:\path\to\hello_world.bin): 

echo Step 10: Writing application .bin to memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x08000000 %F_APP_BIN%
if %errorlevel% neq 0 goto :step_failed

echo Step 10 successful.
timeout /t 3

echo End of Fidelix .
timeout /t 1

goto :done

rem Main script execution
:execute
if /i "%MODULE%" equ "Macronix" (
    call :macronix_steps
) else if /i "%MODULE%" equ "Fidelix" (
    call :fidelix_steps
)

:done
echo End
goto :eof

rem Handle failed steps
:step_failed
echo An error occurred. Exiting...
goto :done

rem End of script
:end
echo Script terminated.
