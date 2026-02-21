@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   KOLA SIRASI BOTU
echo ========================================
echo.
python kola_bot.py
echo.
echo ========================================
echo   Tamamlandı!
echo ========================================
pause
