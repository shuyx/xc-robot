@echo off
echo 启动XC-ROBOT GUI...
echo 使用虚拟环境Python: %~dp0venv\Scripts\python.exe

cd /d "%~dp0"
venv\Scripts\python.exe start_gui.py

pause