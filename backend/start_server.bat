@echo off
REM Script pour démarrer le serveur en arrière-plan
cd /d "c:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2\backend"
start /B python server.py > server_output.log 2>&1
