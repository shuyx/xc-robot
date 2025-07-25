@echo off
chcp 65001 >nul
title Fix Pydantic Settings Dependency
cd /d "%~dp0"

echo ==========================================
echo Installing pydantic-settings
echo ==========================================

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing pydantic-settings...
pip install pydantic-settings

echo Verifying installation...
python -c "import pydantic_settings; print('pydantic-settings installed successfully')"

echo.
pause