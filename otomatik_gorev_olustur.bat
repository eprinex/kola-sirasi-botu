@echo off
chcp 65001 >nul
echo ========================================
echo   WINDOWS GOREV ZAMANLAYICI KURULUMU
echo ========================================
echo.
echo Bu script, her Persembe 18:00'de otomatik calisacak bir gorev olusturacak.
echo.
pause

set SCRIPT_PATH=%~dp0kola_bot.py
set BAT_PATH=%~dp0kola_bot.bat

echo.
echo Gorev olusturuluyor...
echo.

schtasks /create /tn "Kola Sirasi Hatirlatici" /tr "\"%BAT_PATH%\"" /sc weekly /d THU /st 18:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   BASARILI!
    echo ========================================
    echo.
    echo Gorev basariyla olusturuldu!
    echo Her Persembe saat 18:00'de otomatik calisacak.
    echo.
    echo Gorev Zamanlayici'yi acmak icin: taskschd.msc
    echo.
) else (
    echo.
    echo ========================================
    echo   HATA!
    echo ========================================
    echo.
    echo Gorev olusturulamadi. Bu scripti yonetici olarak calistirin.
    echo Sag tik - "Yonetici olarak calistir"
    echo.
)

pause
