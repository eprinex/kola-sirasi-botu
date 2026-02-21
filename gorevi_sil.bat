@echo off
chcp 65001 >nul
echo ========================================
echo   GÖREV SİLME
echo ========================================
echo.
echo "Kola Sırası Hatırlatıcı" görevi siliniyor...
echo.

schtasks /delete /tn "Kola Sırası Hatırlatıcı" /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ Görev başarıyla silindi!
) else (
    echo.
    echo ❌ Görev bulunamadı veya silinemedi.
)

echo.
pause
