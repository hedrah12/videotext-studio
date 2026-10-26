@echo off
setlocal EnableDelayedExpansion
title VideoText Studio v1.0 - Full-Stack React dan Python Server
color 0b

cd /d "%~dp0"

echo ==============================================================================
echo        VIDEOTEXT STUDIO v1.0 - REACT FRONTEND DAN PYTHON BACKEND
echo   Sistem Ekstraksi Subtitle Video (OCR) dan Deteksi Typo (NLP) - Kelompok 4
echo ==============================================================================
echo.
echo [1/2] Memeriksa lingkungan Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak terdeteksi di PATH sistem!
    echo Silakan install Python 3.9+ atau pastikan 'Add Python to PATH' dicentang.
    pause
    exit /b 1
)

echo [2/2] Membuka Browser Otomatis ke http://localhost:5000 ...
start "" http://localhost:5000

echo.
echo ==============================================================================
echo Server sedang berjalan pada port 5000...
echo Jangan tutup jendela terminal ini selama Anda menggunakan web studio!
echo ==============================================================================
echo.

python server.py

pause
