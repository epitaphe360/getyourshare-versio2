# Script de démarrage pour le frontend React

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   DEMARRAGE FRONTEND REACT" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Aller dans le dossier frontend
Set-Location "$PSScriptRoot\frontend"

Write-Host " Dossier: $PWD" -ForegroundColor Cyan
Write-Host ""

# Vérifier que node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host " [WARNING] node_modules manquant - Installation des dépendances..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

Write-Host " [OK] Dépendances prêtes" -ForegroundColor Green
Write-Host ""

Write-Host " [START] Lancement du serveur React..." -ForegroundColor Green
Write-Host "   URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Mode: Development (hot reload activé)" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   Le navigateur va s'ouvrir automatiquement" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Lancer React
npm start

Write-Host ""
Write-Host " [STOP] Serveur arrêté" -ForegroundColor Red
