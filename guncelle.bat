@echo off
chcp 65001 >nul
title OBLIV WEAR - Site Güncelleme
cd /d "%~dp0"

echo.
echo ========================================================
echo        OBLIV WEAR // OTOMATİK GÜNCELLEME SİSTEMİ
echo ========================================================
echo.

echo [*] Tüm dosya değişiklikleri taranıyor ve ekleniyor...
git add -A

git status --porcelain > "%temp%\git_obliv_status.tmp"
for %%R in ("%temp%\git_obliv_status.tmp") do if %%~zR equ 0 (
    echo [i] Yeni bir değişiklik bulunamadı (Zaten en güncel halindesiniz).
    goto push_step
)

echo [*] Güncelleme paketi oluşturuluyor...
set "commit_msg=Guncelleme: %date% %time%"
git commit -m "%commit_msg%"

:push_step
echo.
echo [*] Canlı sunucuya (GitHub & Render) gönderiliyor...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  [+] TEBRİKLER! GÜNCELLEMELER BAŞARIYLA SİTEYE GİTTİ!
    echo  [+] oblivwear.com.tr 1-2 dakika içinde otomatik yenilenecektir.
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo  [!] Güncelleme gönderilirken bir sorun oluştu.
    echo      Lütfen internet bağlantınızı kontrol ediniz.
    echo ========================================================
)

if exist "%temp%\git_obliv_status.tmp" del "%temp%\git_obliv_status.tmp"

echo.
echo Pencereyi kapatmak için herhangi bir tuşa basınız...
pause >nul
