# Script pour lancer backend et frontend en parallèle
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   [START] LANCEMENT DES SERVEURS" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Lancer le backend dans une nouvelle fenêtre PowerShell
Write-Host "[>]  Démarrage du BACKEND (port 8001)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python server.py"

# Attendre 3 secondes
Start-Sleep -Seconds 3

# Lancer le frontend dans une nouvelle fenêtre PowerShell
Write-Host "[>]  Démarrage du FRONTEND (port 3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm start"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "   [OK] SERVEURS EN COURS DE DÉMARRAGE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[URL] Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "[URL] Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Deux fenêtres PowerShell se sont ouvertes" -ForegroundColor Yellow
Write-Host "   - Une pour le backend (Python)" -ForegroundColor Gray
Write-Host "   - Une pour le frontend (React)" -ForegroundColor Gray
Write-Host ""
Write-Host "[KEY] Comptes de test:" -ForegroundColor Yellow
Write-Host "   Influenceur: influencer@test.com / password123" -ForegroundColor Gray
Write-Host "   Merchant: merchant@test.com / password123" -ForegroundColor Gray
Write-Host "   Admin: admin@test.com / password123" -ForegroundColor Gray
Write-Host ""
Write-Host "[WARNING]  Pour arrêter les serveurs:" -ForegroundColor Yellow
Write-Host "   Fermez les deux fenêtres PowerShell ouvertes" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "   [READY] PRÊT À DÉVELOPPER !" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Attendre une touche pour fermer cette fenêtre
Read-Host "Appuyez sur Entrée pour fermer cette fenêtre"
