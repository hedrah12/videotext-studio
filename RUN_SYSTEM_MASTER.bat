@echo off
setlocal EnableDelayedExpansion
title VideoText Studio v1.0 - Ekstraksi Subtitle dan Deteksi Typo (Kelompok 4)
color 0b

:: Masuk ke direktori root script
cd /d "%~dp0"

:: Jalankan pembersihan file sampah di background via python
python -c "import os, shutil, glob; [os.remove(f) for f in ['parse_tdd.py','read_docx.py','docx_content.txt','tdd_dump.txt','run_konversi_docx.bat','convert_to_docx.py','html_reporter.py','unified_pipeline.py','INTEGRATED_SYSTEM_ARCHITECTURE.md'] if os.path.isfile(f)]; shutil.rmtree('output_unified', ignore_errors=True); [os.remove(f) for f in glob.glob('~$*.docx')]" 2>nul

:MENU
cls
echo ===============================================================================
echo        VIDEOTEXT STUDIO v1.0 - SISTEM TERPADU OCR DAN TYPO QA
echo     Proyek Capstone: Computer Vision (OCR) + Natural Language Processing
echo ===============================================================================
echo.
echo   [0] Buka Web Studio (React Frontend dan Python Backend di Browser)
echo   [1] Jalankan CLI Pembaca Subtitle Video (video_subtitle_reader.py)
echo   [2] Jalankan Pemeriksaan Typo Subtitle (typo_checker.py)
echo   [3] Jalankan Analisis Video Sampel 'salah.mp4' (Uji Cepat)
echo   [4] Buka Dokumen SRS dan TDD Kelompok 4
echo   [5] Bersihkan File Sementara dan Cache
echo   [6] Keluar
echo.
echo ===============================================================================
set /p PILIHAN="Pilih menu [0-6]: "

if "%PILIHAN%"=="0" goto WEB_STUDIO
if "%PILIHAN%"=="1" goto PROSES_CLI
if "%PILIHAN%"=="2" goto TYPO_CLI
if "%PILIHAN%"=="3" goto UJI_CEPAT
if "%PILIHAN%"=="4" goto BUKA_DOKUMEN
if "%PILIHAN%"=="5" goto BERSIHKAN
if "%PILIHAN%"=="6" goto KELUAR

echo Pilihan tidak valid, silakan coba lagi.
timeout /t 2 >nul
goto MENU

:WEB_STUDIO
cls
echo ===============================================================================
echo   MEMULAI VIDEOTEXT STUDIO v1.0 (REACT + PYTHON SERVER)
echo ===============================================================================
echo.
cd /d "%~dp0web_app"
call run_web.bat
cd /d "%~dp0"
goto MENU

:PROSES_CLI
cls
echo ===============================================================================
echo   EKSEKUSI CLI: EKSTRAKSI SUBTITLE VIDEO (OPENCV + RAPIDOCR)
echo ===============================================================================
echo.
echo Petunjuk: Anda dapat mengetik nama file (misal: test (1).mp4) atau drag-and-drop file video ke sini.
echo.
set /p VID_PATH="Masukkan nama/path file video: "

:: Bersihkan tanda kutip jika user drag-and-drop file ke terminal
set VID_PATH=!VID_PATH:"=!
set VID_PATH=!VID_PATH:'=!

:: Resolusi cerdas lokasi file video
set TARGET_VIDEO=
if exist "!VID_PATH!" (
    set TARGET_VIDEO=!VID_PATH!
) else if exist "%~dp0!VID_PATH!" (
    set TARGET_VIDEO=%~dp0!VID_PATH!
) else if exist "%~dp0videotext\Video\!VID_PATH!" (
    set TARGET_VIDEO=%~dp0videotext\Video\!VID_PATH!
) else if exist "%~dp0videotext\!VID_PATH!" (
    set TARGET_VIDEO=%~dp0videotext\!VID_PATH!
)

if "!TARGET_VIDEO!"=="" (
    echo.
    echo [ERROR] Berkas video '!VID_PATH!' tidak ditemukan!
    echo Pastikan nama file benar atau drag-and-drop file video langsung ke jendela ini.
    echo.
    pause
    goto MENU
)

echo.
echo ===============================================================================
echo [INFO] Menemukan file: "!TARGET_VIDEO!"
echo Memulai analisis OCR dan deteksi typo...
echo ===============================================================================
echo.
python "%~dp0videotext\video_subtitle_reader.py" "!TARGET_VIDEO!" --check-typos -o "%~dp0videotext\output"
echo.
pause
goto MENU

:TYPO_CLI
cls
echo ===============================================================================
echo   EKSEKUSI CLI: PEMERIKSAAN TYPO SASTRAWI DAN DAMERAU-LEVENSHTEIN
echo ===============================================================================
echo.
set /p TEKS_INPUT="Ketik teks kalimat subtitle untuk diperiksa: "
echo.
python "%~dp0videotext\typo_checker.py" --text "%TEKS_INPUT%"
echo.
pause
goto MENU

:UJI_CEPAT
cls
echo ===============================================================================
echo   UJI CEPAT: MEMPROSES SALAH.MP4 DAN MENDETEKSI TYPO 'ENGANDUNG'
echo ===============================================================================
echo.
python "%~dp0videotext\video_subtitle_reader.py" "%~dp0salah.mp4" --check-typos
echo.
pause
goto MENU

:BUKA_DOKUMEN
cls
echo Membuka dokumen capstone Kelompok 4...
if exist "%~dp0TDD_Kelompok_4.docx" start "" "%~dp0TDD_Kelompok_4.docx"
if exist "%~dp0SRS_Capstone_Kelompok_4_Revisi_Terpadu.docx" start "" "%~dp0SRS_Capstone_Kelompok_4_Revisi_Terpadu.docx"
goto MENU

:BERSIHKAN
cls
echo ===============================================================================
echo   PEMBERSIHAN FILE SEMENTARA DAN CACHE
echo ===============================================================================
echo.
python -c "import os, shutil, glob; [os.remove(f) for f in ['parse_tdd.py','read_docx.py','docx_content.txt','tdd_dump.txt','run_konversi_docx.bat','convert_to_docx.py','html_reporter.py','unified_pipeline.py','INTEGRATED_SYSTEM_ARCHITECTURE.md'] if os.path.isfile(f)]; shutil.rmtree('output_unified', ignore_errors=True); [os.remove(f) for f in glob.glob('~$*.docx')]; [shutil.rmtree(d, ignore_errors=True) for d in ['__pycache__', 'videotext/__pycache__', 'web_app/__pycache__']]" 2>nul
echo [OK] Seluruh file sampah dan cache berhasil dibersihkan!
timeout /t 2 >nul
goto MENU

:KELUAR
cls
echo Terima kasih telah menggunakan VideoText Studio.
timeout /t 2 >nul
exit
