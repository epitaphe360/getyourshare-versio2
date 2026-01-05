@echo off
title GetYourShare Launcher
color 0A
echo ===================================================
echo      LANCEMENT DE GETYOURSHARE (CORRECTIF)
echo ===================================================
echo.

echo 1. Nettoyage des processus existants...
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo 2. Demarrage du BACKEND (Port 5000)...
start "BACKEND - GetYourShare" cmd /k "cd backend && .venv\Scripts\activate && python -m uvicorn server:app --reload --port 5000"

echo.
echo 3. Demarrage du FRONTEND (Port 3003)...
echo    (Cela peut prendre quelques secondes...)
start "FRONTEND - GetYourShare" cmd /k "cd frontend && set PORT=3003 && npm start"

echo.
echo 4. Ouverture du navigateur...
timeout /t 5 >nul
start http://localhost:3003

echo.
echo ===================================================
echo      TOUT EST LANCE !
echo ===================================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3003
echo.
echo Ne fermez pas les fenetres noires qui viennent de s'ouvrir.
echo Si le navigateur ne s'ouvre pas, allez sur http://localhost:3003
echo.
pause