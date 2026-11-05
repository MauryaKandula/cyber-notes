@echo off
title CyberNotes — Standalone Windows EXE Builder (PUBLISHER Agent)
echo ============================================================================
echo   CYBERNOTES — NATIVE WINDOWS EXECUTABLE BUILDER (CyberNotes.exe)
echo   Author: Kandula Paul Saketh Maurya (@MauryaKandula)
echo ============================================================================
echo.

cd /d "%~dp0"

echo [1/2] Verifying multi-resolution application icon (assets\cybernotes.ico)...
if not exist "assets\cybernotes.ico" (
    if exist "generate_icons.py" (
        C:\Python\python.exe generate_icons.py
    )
)

echo [2/2] Compiling native x64 Windows executable (CyberNotes.exe)...
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:winexe /optimize+ /platform:x64 ^
    /win32icon:"assets\cybernotes.ico" ^
    /out:"CyberNotes.exe" ^
    "CyberNotesHost.cs"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] Native executable built at: %~dp0CyberNotes.exe
) else (
    echo.
    echo [ERROR] Build failed. Check output above.
)
