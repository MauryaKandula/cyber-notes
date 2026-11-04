@echo off
title CyberNotes Installer & Setup
echo ========================================================
echo   CyberNotes v2.0.0 - Setup & Desktop Shortcut Creator
echo   Created by Kandula Paul Saketh Maurya (@MauryaKandula)
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Installing Python dependencies (PyQt6)...
python -m pip install -r requirements.txt --quiet

echo [2/3] Creating Desktop Shortcut (CyberNotes.lnk)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$wsh = New-Object -ComObject WScript.Shell; $desk = [Environment]::GetFolderPath('Desktop'); $sc = $wsh.CreateShortcut((Join-Path $desk 'CyberNotes.lnk')); $sc.TargetPath = (Get-Command pythonw.exe).Source; $sc.Arguments = '\"%~dp0cyber_notes.py\"'; $sc.WorkingDirectory = '%~dp0'; $sc.Description = 'CyberNotes - Modern Neon Sticky Notes'; $sc.Save()"

echo [3/3] Launching CyberNotes...
start "" pythonw "%~dp0cyber_notes.py"

echo.
echo Setup complete! CyberNotes is now running on your desktop.
timeout /t 3 >nul
