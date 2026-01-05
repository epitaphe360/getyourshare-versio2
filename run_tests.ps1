# Script de lancement des tests
# Démarre le serveur en arrière-plan et lance les tests

Write-Host "🚀 Démarrage du serveur backend..." -ForegroundColor Green

# Démarrer le serveur en background
$serverJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2\backend"
    python server.py
}

# Attendre que le serveur démarre
Write-Host "⏳ Attente du démarrage du serveur (10 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Vérifier si le serveur est actif
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Serveur actif et prêt" -ForegroundColor Green
} catch {
    Write-Host "❌ Le serveur ne répond pas" -ForegroundColor Red
    Stop-Job $serverJob
    Remove-Job $serverJob
    exit 1
}

# Lancer les tests
Write-Host "`n🧪 Lancement des tests..." -ForegroundColor Cyan
Set-Location "C:\Users\samye\OneDrive\Desktop\getyoursharelivrable\getyourshare-versio2"
python test_api_only.py

# Stopper le serveur
Write-Host "`n🛑 Arrêt du serveur..." -ForegroundColor Yellow
Stop-Job $serverJob
Remove-Job $serverJob

Write-Host "✅ Tests terminés" -ForegroundColor Green
