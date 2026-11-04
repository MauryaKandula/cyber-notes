@echo off
title CyberNotes v2.1.0 Installer & Setup
echo ========================================================
echo   CyberNotes v2.1.0 - Setup & Windows Shortcut Creator
echo   Created by Kandula Paul Saketh Maurya (@MauryaKandula)
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/4] Installing Python dependencies (PyQt6)...
python -m pip install -r requirements.txt --quiet

echo [2/4] Creating Desktop Shortcut (CyberNotes.lnk) with official icon...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$wsh = New-Object -ComObject WScript.Shell; $desk = [Environment]::GetFolderPath('Desktop'); $sc = $wsh.CreateShortcut((Join-Path $desk 'CyberNotes.lnk')); $sc.TargetPath = (Get-Command pythonw.exe).Source; $sc.Arguments = '\"%~dp0cyber_notes.py\"'; $sc.WorkingDirectory = '%~dp0'; $sc.IconLocation = '%~dp0assets\cybernotes.ico,0'; $sc.Description = 'CyberNotes - Modern Neon Sticky Notes for Windows'; $sc.Save()"

echo [3/4] Creating Start Menu Shortcut (CyberNotes.lnk) with official icon...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$wsh = New-Object -ComObject WScript.Shell; $sm = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\CyberNotes.lnk'; $sc = $wsh.CreateShortcut($sm); $sc.TargetPath = (Get-Command pythonw.exe).Source; $sc.Arguments = '\"%~dp0cyber_notes.py\"'; $sc.WorkingDirectory = '%~dp0'; $sc.IconLocation = '%~dp0assets\cybernotes.ico,0'; $sc.Description = 'CyberNotes - Modern Neon Sticky Notes for Windows'; $sc.Save()"

echo [4/4] Launching CyberNotes...
start "" pythonw "%~dp0cyber_notes.py"

echo.
echo Setup complete! CyberNotes v2.1.0 is now running on your desktop.
timeout /t 3 >nul
