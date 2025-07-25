@echo off
chcp 65001 >nul
title XC-ROBOT Web Interface
cd /d "%~dp0"
echo ==========================================
echo XC-ROBOT Web Interface
echo ==========================================

call venv\Scripts\activate.bat
echo Starting Web Server...
python apps/launchers/start_web_dev.py

pause