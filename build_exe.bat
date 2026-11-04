@echo off
title CyberNotes — Standalone Windows EXE Builder (PUBLISHER Agent)
echo ============================================================================
echo   CYBERNOTES — STANDALONE WINDOWS EXECUTABLE BUILDER
echo   Author: Kandula Paul Saketh Maurya (@MauryaKandula)
echo ============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking PyInstaller installation...
C:\Python\python.exe -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    C:\Python\python.exe -m pip install pyinstaller --quiet
)

echo [2/3] Verifying multi-resolution application icon (assets\cybernotes.ico)...
if not exist "assets\cybernotes.ico" (
    if exist "generate_icons.py" (
        C:\Python\python.exe generate_icons.py
    )
)

echo [3/3] Building standalone Windows executable (dist\CyberNotes.exe)...
C:\Python\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name "CyberNotes" ^
    --icon "assets\cybernotes.ico" ^
    --version-file "version_info.txt" ^
    --add-data "assets;assets" ^
    "cyber_notes.py"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] Standalone executable built at: %~dp0dist\CyberNotes.exe
) else (
    echo.
    echo [ERROR] PyInstaller build failed. Check output above.
)
