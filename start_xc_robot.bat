@echo off
chcp 65001 >nul
title XC-ROBOT Control System
cd /d "%~dp0"
echo ==========================================
echo XC-ROBOT Control System
echo ==========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check dependencies
echo Checking dependencies...
python -c "import PyQt5; print('PyQt5 OK')" 2>nul || (echo Missing PyQt5 dependency && pause && exit)
python -c "import numpy; print('NumPy OK')" 2>nul || (echo Missing NumPy dependency && pause && exit)

echo.
echo Starting Desktop GUI...
python apps/launchers/start_desktop_gui.py

echo.
echo Program finished
pause