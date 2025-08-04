@echo off
REM Windows environment configuration script for Orbbec SDK
REM Fixed encoding version

REM Get current directory
set CURR_DIR=%~dp0
set CURR_DIR=%CURR_DIR:~0,-1%

REM Set Python path
set PYTHONPATH=%CURR_DIR%;%PYTHONPATH%

REM Set DLL search paths
set PATH=%CURR_DIR%\sdk\lib\win_x64;%CURR_DIR%\sdk\lib\win_x64\extensions\depthengine;%CURR_DIR%\sdk\lib\win_x64\extensions\filters;%CURR_DIR%\sdk\lib\win_x64\extensions\firmwareupdater;%CURR_DIR%\sdk\lib\win_x64\extensions\frameprocessor;%PATH%

echo Orbbec SDK Windows environment configured
echo PYTHONPATH: %PYTHONPATH%
echo Current directory: %CURR_DIR%
echo DLL paths added to PATH

REM Start PowerShell session
powershell.exe