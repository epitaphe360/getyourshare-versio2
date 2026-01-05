# LANCEMENT RAPIDE - Ports standard 5000 et 3000
# Usage: .\launch.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LANCEMENT TRACKNOW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Liberer les ports
Write-Host "Nettoyage des ports..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 5000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 3000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Start-Sleep -Seconds 1

# Backend
Write-Host "Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python server.py" -WindowStyle Normal

Start-Sleep -Seconds 4

# Frontend  
Write-Host "Frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start" -WindowStyle Normal

Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
