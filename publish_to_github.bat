@echo off
title Publish CyberNotes to GitHub (@MauryaKandula)
echo ========================================================
echo   Publishing CyberNotes to GitHub (MauryaKandula/cyber-notes)
echo ========================================================
echo.

cd /d "%~dp0"

where gh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    gh auth status >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Logging into GitHub CLI...
        gh auth login --web
    )
    echo Creating public repository MauryaKandula/cyber-notes and pushing...
    gh repo create MauryaKandula/cyber-notes --public --source=. --remote=origin --description "Modern, ultra-smooth neon desktop sticky notes application built with PyQt6." --push
) else (
    echo Pushing to origin main...
    git push -u origin main
)

echo.
echo Done! Repository URL: https://github.com/MauryaKandula/cyber-notes
pause
