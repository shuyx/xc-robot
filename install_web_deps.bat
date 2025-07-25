@echo off
chcp 65001 >nul
title Install XC-ROBOT Web Dependencies
cd /d "%~dp0"

echo ==========================================
echo Installing XC-ROBOT Web Dependencies
echo ==========================================

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing web dependencies...
pip install -r requirements/web.txt

echo.
echo Web dependencies installation completed!
echo You can now run: start_web_interface.bat
echo.
pause