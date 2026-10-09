@echo off

rem Set common timeout
set TIMEOUT=-t 60000

rem Function to show the main menu and prompt for module variant
:main_menu
echo Please select the module variant:
echo 1. Macronix_8MB
echo 2. Fidelix_8MB
echo 3. Fidelix_16MB
set /p MODULE_CHOICE=Enter choice (1/2/3):

if "%MODULE_CHOICE%"=="1" (
    set MODULE=Macronix
) else if "%MODULE_CHOICE%"=="2" (
    set MODULE=Fidelix
) else if "%MODULE_CHOICE%"=="3" (
    set MODULE=Fidelix_16MB
) else (
    echo [ERROR] Invalid choice. Please select 1, 2, or 3.
    echo.
    goto :main_menu
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
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 2: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 3: Flash erasing region...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x18000400 0x200000
if errorlevel 1 goto :step_failed
timeout /t 2

rem New Step: Prompt for application .bin location
set /p APP_BIN=Enter path to application .bin (e.g., hello_world.bin/wifi_cli.bin, C:\path\to\hello_world.bin):

echo Step 4: Writing application .bin to memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x18000400 %APP_BIN%
if errorlevel 1 goto :step_failed
timeout /t 1

echo Macronix steps successful.
timeout /t 5

goto :done

rem ---------------FIDELIX PART-----------------


rem Function to perform all steps for Fidelix
:fidelix_steps
echo Starting Fidelix steps...
timeout /t 2

rem Step 1: Writing FCB_FID.bin to memory
set /p FCB_FID=Enter path to FCB_FID.bin (e.g., C:\path\to\FCB_FID.bin):
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x20001000 %FCB_FID%
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 2: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 3: Getting property...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- get-property 0x19 0x9
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 4: Flash erasing region 0x08000000
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x1000
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 5: Filling memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- fill-memory 0x20001000 0x04 0xf000000f
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 6: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 7: Flash erasing region 0x08000000
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x10000
if errorlevel 1 goto :step_failed
timeout /t 1

rem New Step: Prompt for application .bin location
set /p F_APP_BIN=Enter path to application .bin (e.g., hello_world.bin/wifi_cli.bin, C:\path\to\hello_world.bin):

echo Step 8: Writing application .bin to memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x08000000 %F_APP_BIN%
if errorlevel 1 goto :step_failed
timeout /t 3

echo End of Fidelix .
timeout /t 1

goto :done

rem Function to perform all steps for Fidelix 16MB
:fidelix_16mb_steps
echo Starting Fidelix 16MB steps...
timeout /t 2

rem Step 1: Writing FCB_FID.bin to memory
set /p FCB_FID_16=Enter path to FCB_FID.bin (e.g., C:\path\to\FCB_FID.bin):
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x20001000 %FCB_FID_16%
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 2: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 3: Getting property...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- get-property 0x19 0x9
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 4: Flash erasing region 0x08000000 (16MB size)
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x8000
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 5: Filling memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- fill-memory 0x20001000 0x04 0xf000000f
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 6: Configuring memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- configure-memory 0x9 0x20001000
if errorlevel 1 goto :step_failed
timeout /t 1

echo Step 7: Flash erasing region 0x08000000
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- flash-erase-region 0x08000000 0x10000
if errorlevel 1 goto :step_failed
timeout /t 1

rem New Step: Prompt for application .bin location
set /p F_APP_BIN_16=Enter path to application .bin (e.g., hello_world.bin/wifi_cli.bin, C:\path\to\hello_world.bin):

echo Step 8: Writing application .bin to memory...
%BLHOST_PATH% -p %COM_PORT% %TIMEOUT% -- write-memory 0x08000000 %F_APP_BIN_16%
if errorlevel 1 goto :step_failed
timeout /t 3

echo End of Fidelix 16MB.
timeout /t 1

goto :done

rem Main script execution
:execute
if /i "%MODULE%" equ "Macronix" (
    call :macronix_steps
) else if /i "%MODULE%" equ "Fidelix" (
    call :fidelix_steps
) else if /i "%MODULE%" equ "Fidelix_16MB" (
    call :fidelix_16mb_steps
)

:done
echo End
echo.
pause
goto :eof

rem Handle failed steps
:step_failed
echo.
echo Error occurred. Exiting...
echo.
pause
goto :eof

rem End of script
:end
echo Script terminated.
echo.
pause
