# Script de lancement rapide et stable des serveurs Frontend et Backend
# Utilisation: .\start-servers.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LANCEMENT DES SERVEURS TRACKNOW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Definir le repertoire racine
$RootDir = $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$VenvPath = Join-Path $RootDir ".venv\Scripts\python.exe"

# Fonction pour arreter les processus sur un port
function Stop-PortProcess {
    param([int]$Port)
    
    $tcp = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($tcp) {
        Write-Host "ATTENTION - Arret du processus existant sur le port $Port..." -ForegroundColor Yellow
        Stop-Process -Id $tcp.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Write-Host "OK - Port $Port libere" -ForegroundColor Green
    }
}

# Fonction pour verifier si un port est en ecoute
function Test-PortListening {
    param([int]$Port, [int]$MaxAttempts = 30)
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

# Nettoyer les ports
Write-Host "Verification des ports..." -ForegroundColor White
Stop-PortProcess -Port 5000
Stop-PortProcess -Port 3000
Write-Host ""

# Lancer le Backend
Write-Host "Lancement du Backend (Python FastAPI - Port 5000)..." -ForegroundColor Cyan

$BackendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$BackendDir'; & '$VenvPath' server.py"
) -WindowStyle Normal -PassThru

Write-Host "Attente du demarrage du backend..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

if (Test-PortListening -Port 5000 -MaxAttempts 20) {
    Write-Host "OK - Backend demarre avec succes sur http://localhost:5000" -ForegroundColor Green
} else {
    Write-Host "ATTENTION - Le backend tarde a demarrer, verifiez la fenetre PowerShell..." -ForegroundColor Yellow
}

Write-Host ""

# Lancer le Frontend
Write-Host "Lancement du Frontend (React - Port 3000)..." -ForegroundColor Cyan

$FrontendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$FrontendDir'; npm start"
) -WindowStyle Normal -PassThru

Write-Host "Attente du demarrage du frontend..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

if (Test-PortListening -Port 3000 -MaxAttempts 40) {
    Write-Host "OK - Frontend demarre avec succes sur http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "ATTENTION - Le frontend tarde a demarrer, verifiez la fenetre PowerShell..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SERVEURS LANCES" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Les serveurs tournent dans des fenetres PowerShell separees" -ForegroundColor Gray
Write-Host "Fermez ces fenetres pour arreter les serveurs" -ForegroundColor Gray
Write-Host ""

# Afficher l'etat des connexions
Write-Host "Etat des ports:" -ForegroundColor Cyan
Get-NetTCPConnection -LocalPort 5000,3000 -ErrorAction SilentlyContinue | 
    Select-Object LocalPort, State | 
    Format-Table -AutoSize

Write-Host "Script termine - Les serveurs sont operationnels" -ForegroundColor Green
Write-Host ""
