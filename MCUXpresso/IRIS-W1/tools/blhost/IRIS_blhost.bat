
@echo off

set /p COM_PORT=Enter COM port number (e.g., COM1): 
set /p BLHOST_PATH=Enter path to blhost.exe (e.g., C:\path\to\blhost.exe): 

rem Fill memory
%BLHOST_PATH% -p %COM_PORT% -t 60000 -- fill-memory 0x20001000 0x4 0xC0000008
if %errorlevel% equ 0 (
    echo Fill memory successful.
) else (
    echo Fill memory failed.
    goto :end
)

rem Configure memory
%BLHOST_PATH% -p %COM_PORT% -t 60000 -- configure-memory 0x9 0x20001000
if %errorlevel% equ 0 (
    echo Configure memory successful.
) else (
    echo Configure memory failed.
    goto :end
)

rem Flash erase region
%BLHOST_PATH% -p %COM_PORT% -t 60000 -- flash-erase-region 0x18000400 0x200000
if %errorlevel% equ 0 (
    echo Flash erase region successful.
) else (
    echo Flash erase region failed.
    goto :end
)

echo Done.
goto :eof

:end
echo Failed.
