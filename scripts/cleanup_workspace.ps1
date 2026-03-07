#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Nettoie les fichiers parasites du workspace GetYourShare
    Déplace les scripts de debug, rapports, SQL temporaires vers des dossiers organisés

.USAGE
    cd "c:\Users\samye\OneDrive\Desktop\getyourshare version 6\getyourshare-versio2"
    .\scripts\cleanup_workspace.ps1
#>

$ROOT = Split-Path $PSScriptRoot -Parent
$BACKEND = Join-Path $ROOT "backend"

Write-Host "🧹 Nettoyage workspace GetYourShare..." -ForegroundColor Cyan

# ============================================================
# CRÉER LA STRUCTURE DE DESTINATION
# ============================================================
$dirs = @(
    "docs",
    "docs/audits",
    "docs/guides",
    "docs/migrations_history",
    "scripts/debug",
    "scripts/seed",
    "scripts/check",
    "scripts/apply",
    "backend/scripts/debug",
    "backend/scripts/seed",
    "backend/scripts/check"
)

foreach ($d in $dirs) {
    $path = Join-Path $ROOT $d
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

Write-Host "✅ Structure créée" -ForegroundColor Green

# ============================================================
# DÉPLACER LES FICHIERS .md DE LA RACINE (sauf README.md)
# ============================================================
$mdFilesToKeep = @("README.md", "CHANGELOG.md", "CONTRIBUTING.md", "MIGRATION_COMPLETE.sql")
$mdFiles = Get-ChildItem -Path $ROOT -Filter "*.md" -File |
    Where-Object { $_.Name -notin $mdFilesToKeep }

$mdCount = 0
foreach ($f in $mdFiles) {
    $dest = Join-Path $ROOT "docs" $f.Name
    if (-not (Test-Path $dest)) {
        Move-Item -Path $f.FullName -Destination $dest
        $mdCount++
    }
}
Write-Host "📄 $mdCount fichiers .md déplacés vers docs/" -ForegroundColor Yellow

# ============================================================
# DÉPLACER LES FICHIERS SQL DE LA RACINE (sauf MIGRATION_COMPLETE.sql)
# ============================================================
$sqlFilesToKeep = @("MIGRATION_COMPLETE.sql")
$sqlFiles = Get-ChildItem -Path $ROOT -Filter "*.sql" -File |
    Where-Object { $_.Name -notin $sqlFilesToKeep }

$sqlCount = 0
foreach ($f in $sqlFiles) {
    $dest = Join-Path $ROOT "docs/migrations_history" $f.Name
    if (-not (Test-Path $dest)) {
        Move-Item -Path $f.FullName -Destination $dest
        $sqlCount++
    }
}
Write-Host "🗄️  $sqlCount fichiers .sql déplacés vers docs/migrations_history/" -ForegroundColor Yellow

# ============================================================
# DÉPLACER LES SCRIPTS PYTHON DE RACINE
# ============================================================
$pyRoot = Get-ChildItem -Path $ROOT -Filter "*.py" -File |
    Where-Object { $_.Name -notin @("run_migrations.py", "setup.py") }

$pyRootCount = 0
foreach ($f in $pyRoot) {
    $dest = Join-Path $ROOT "scripts/debug" $f.Name
    if (-not (Test-Path $dest)) {
        Move-Item -Path $f.FullName -Destination $dest
        $pyRootCount++
    }
}
Write-Host "🐍 $pyRootCount scripts Python racine → scripts/debug/" -ForegroundColor Yellow

# ============================================================
# DÉPLACER LES SCRIPTS check_*.py, fix_*.py etc. DU BACKEND
# ============================================================
$patterns = @("check_*.py", "fix_*.py", "apply_*.py", "test_*.py",
              "create_*.py", "add_*.py", "inspect_*.py", "verify_*.py",
              "debug_*.py", "generate_*.py", "seed_*.py", "reset_*.py",
              "update_*.py", "migrate_*.py", "probe_*.py", "run_*.py",
              "setup_*.py", "clean_*.py", "analyze_*.py", "show_*.py",
              "list_*.py", "find_*.py", "get_*.py", "insert_*.py",
              "quick_*.py", "simple_*.py", "force_*.py", "diagnose_*.py",
              "ensure_*.py", "load_*.py", "init_*.py", "enable_*.py",
              "disable_*.py", "watch_*.py", "install_*.py", "remove_*.py",
              "replace_*.py", "extract_*.py", "import_*.py")

$backendScriptCount = 0
foreach ($pattern in $patterns) {
    $files = Get-ChildItem -Path $BACKEND -Filter $pattern -File
    foreach ($f in $files) {
        # Garder les vrais fichiers de l'application
        $keepFiles = @("run.py", "run_server.py", "celery_app.py", "scheduler.py")
        if ($f.Name -in $keepFiles) { continue }

        # Choisir destination selon pattern
        if ($f.Name -match "^seed_|^generate_|^create_test_|^insert_") {
            $destDir = Join-Path $BACKEND "scripts/seed"
        } elseif ($f.Name -match "^check_|^verify_|^inspect_|^analyze_|^diagnose_") {
            $destDir = Join-Path $BACKEND "scripts/check"
        } else {
            $destDir = Join-Path $BACKEND "scripts/debug"
        }

        $dest = Join-Path $destDir $f.Name
        if (-not (Test-Path $dest)) {
            Move-Item -Path $f.FullName -Destination $dest
            $backendScriptCount++
        }
    }
}
Write-Host "🐍 $backendScriptCount scripts backend → backend/scripts/" -ForegroundColor Yellow

# ============================================================
# DÉPLACER LES FICHIERS .txt .log de la RACINE backend
# ============================================================
$txtFiles = Get-ChildItem -Path $BACKEND -Filter "*.txt" -File
$logFiles = Get-ChildItem -Path $BACKEND -Filter "*.log" -File
$miscCount = 0

foreach ($f in ($txtFiles + $logFiles)) {
    $dest = Join-Path $BACKEND "scripts/debug" $f.Name
    if (-not (Test-Path $dest)) {
        Move-Item -Path $f.FullName -Destination $dest
        $miscCount++
    }
}
Write-Host "📋 $miscCount fichiers txt/log déplacés" -ForegroundColor Yellow

# ============================================================
# RÉSUMÉ
# ============================================================
$total = $mdCount + $sqlCount + $pyRootCount + $backendScriptCount + $miscCount

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "✅ Nettoyage terminé — $total fichiers déplacés" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Structure résultante:" -ForegroundColor White
Write-Host "  docs/              → rapports .md et guides"
Write-Host "  docs/migrations_history/ → historique SQL"
Write-Host "  scripts/debug/     → scripts de débogage"
Write-Host "  backend/scripts/   → scripts backend"
Write-Host ""
Write-Host "⚠️  Vérifiez que l'application démarre toujours avant de committer!" -ForegroundColor Yellow
