@echo off
chcp 65001 >nul
title Fix Python Multipart Dependency
cd /d "%~dp0"

echo ==========================================
echo Installing python-multipart
echo ==========================================

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing python-multipart...
pip install python-multipart

echo Verifying installation...
python -c "from multipart import parse_options_header; print('python-multipart installed successfully')"

echo.
pause