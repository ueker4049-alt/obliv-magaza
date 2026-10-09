@echo off
setlocal EnableDelayedExpansion
title OBLIV WEAR - Otomatik Guncelleme
cd /d "%~dp0"

echo.
echo ========================================================
echo        OBLIV WEAR // OTOMATIK GUNCELLEME SISTEMI
echo ========================================================
echo.

echo [*] Tum degisiklikler taranip ekleniyor...
git add -A

echo [*] Guncelleme paketi olusturuluyor...
set "commit_msg=Site Guncellemesi: %date% %time%"
git commit -m "%commit_msg%" >nul 2>&1

echo.
echo [*] Canli sunucuya gonderiliyor...
git push origin main

if errorlevel 1 (
    echo.
    echo ========================================================
    echo  [!] HATA: Guncelleme gonderilemedi!
    echo      Internet baglantinizi kontrol ediniz.
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo  [+] TEBRIKLER! GUNCELLEMELER BASARIYLA SITE YE GITTI!
    echo  [+] oblivwear.com.tr 1-2 dakika icinde otomatik yenilenir.
    echo ========================================================
)

echo.
echo Pencereyi kapatmak icin herhangi bir tusa basiniz...
pause >nul
