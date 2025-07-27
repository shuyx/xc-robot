@echo off
chcp 65001 >nul
title XC-ROBOT Web Interface with Test API
cd /d "%~dp0"
echo ==========================================
echo XC-ROBOT Web Interface with Test API
echo ==========================================

call venv\Scripts\activate.bat

echo 启动测试API服务器...
start "XC-ROBOT Test API" cmd /k "python testing/lua_scripts/web_api.py"

echo 等待API服务器启动...
timeout /t 3 /nobreak >nul

echo 启动Web GUI...
python scripts/startup/start_web_gui.py

pause