@echo off
title CyberNotes v2.1.0 — Official Windows Setup
echo ============================================================================
echo   CYBERNOTES v2.1.0 — OFFICIAL WINDOWS SETUP
echo   Created by Kandula Paul Saketh Maurya (@MauryaKandula)
echo ============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python & PyQt6 runtime dependencies...
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python -m pip install -r requirements.txt --quiet
) else (
    if exist "C:\Python\python.exe" (
        "C:\Python\python.exe" -m pip install -r requirements.txt --quiet
    )
)

echo [2/3] Creating Desktop, Start Menu & Windows Startup shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$Wsh = New-Object -ComObject WScript.Shell; $Dir = '%~dp0'.TrimEnd('\'); $Exe = Join-Path $Dir 'CyberNotes.exe'; $Ico = Join-Path $Dir 'assets\cybernotes.ico'; foreach ($Dst in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'), [Environment]::GetFolderPath('Startup'))) { $Lnk = $Wsh.CreateShortcut((Join-Path $Dst 'CyberNotes.lnk')); $Lnk.TargetPath = $Exe; if ($Dst -eq [Environment]::GetFolderPath('Startup')) { $Lnk.Arguments = '--startup' }; $Lnk.WorkingDirectory = $Dir; $Lnk.IconLocation = \"$Ico,0\"; $Lnk.Description = 'CyberNotes — Modern Neon Sticky Notes'; $Lnk.Save() }"

echo [3/3] Launching CyberNotes...
start "" "%~dp0CyberNotes.exe"

echo.
echo [SUCCESS] CyberNotes is installed and running!
timeout /t 3 >nul
