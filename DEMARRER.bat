@echo off
echo ========================================
echo   LANCEMENT RAPIDE TRACKNOW
echo ========================================
echo.

cd /d "%~dp0"

REM Lancer le script PowerShell
powershell -ExecutionPolicy Bypass -File "%~dp0launch.ps1"

pause
