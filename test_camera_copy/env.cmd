@echo off
REM Windows环境配置脚本
REM 为Orbbec SDK设置正确的环境变量

REM 获取当前目录
set CURR_DIR=%~dp0
set CURR_DIR=%CURR_DIR:~0,-1%

REM 设置Python路径
set PYTHONPATH=%CURR_DIR%;%PYTHONPATH%

REM 设置DLL搜索路径
set PATH=%CURR_DIR%\sdk\lib\win_x64;%CURR_DIR%\sdk\lib\win_x64\extensions\depthengine;%CURR_DIR%\sdk\lib\win_x64\extensions\filters;%CURR_DIR%\sdk\lib\win_x64\extensions\firmwareupdater;%CURR_DIR%\sdk\lib\win_x64\extensions\frameprocessor;%PATH%

echo Orbbec SDK Windows环境已配置
echo PYTHONPATH: %PYTHONPATH%
echo 当前目录: %CURR_DIR%
echo DLL路径已添加到PATH

REM 启动PowerShell会话
powershell.exe