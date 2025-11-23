# Nettoyage processus
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Aller dans backend
Set-Location "$PSScriptRoot\backend"

# Lancer serveur
Write-Host "Backend demarre sur http://localhost:5000" -ForegroundColor Green
python server.py
