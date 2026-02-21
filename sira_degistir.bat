@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
python sira_degistir.py
echo.
pause
