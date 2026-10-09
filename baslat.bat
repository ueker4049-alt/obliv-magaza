@echo off
echo OblivWear Magaza ve Canli Yayin Baslatiliyor...
start "Flask Magaza" py app.py
timeout /t 2 >nul
start "Cloudflare Tunel" /D "%~dp0" "%~dp0cloudflared.exe" tunnel --config "%~dp0config.yml" run
echo Magazaniz https://oblivwear.com.tr adresinde canliya alindi!
