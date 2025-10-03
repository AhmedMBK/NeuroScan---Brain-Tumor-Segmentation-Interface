# 🐘 Installation PostgreSQL pour CereBloom
# Script PowerShell pour installer PostgreSQL sur Windows

Write-Host "🧠 CereBloom - Installation PostgreSQL" -ForegroundColor Cyan
Write-Host "=" * 50

# Vérifier si PostgreSQL est déjà installé
$pgPath = Get-Command psql -ErrorAction SilentlyContinue
if ($pgPath) {
    Write-Host "✅ PostgreSQL déjà installé: $($pgPath.Source)" -ForegroundColor Green
    $version = & psql --version
    Write-Host "📋 Version: $version" -ForegroundColor Yellow
} else {
    Write-Host "❌ PostgreSQL non trouvé" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Options d'installation:" -ForegroundColor Yellow
    Write-Host "1. Avec Chocolatey (recommandé):"
    Write-Host "   choco install postgresql"
    Write-Host ""
    Write-Host "2. Avec Scoop:"
    Write-Host "   scoop install postgresql"
    Write-Host ""
    Write-Host "3. Installation manuelle:"
    Write-Host "   https://www.postgresql.org/download/windows/"
    Write-Host ""
    
    $install = Read-Host "Voulez-vous installer avec Chocolatey? (y/n)"
    
    if ($install -eq "y" -or $install -eq "Y") {
        # Vérifier Chocolatey
        $chocoPath = Get-Command choco -ErrorAction SilentlyContinue
        if (-not $chocoPath) {
            Write-Host "❌ Chocolatey non installé" -ForegroundColor Red
            Write-Host "Installez Chocolatey d'abord: https://chocolatey.org/install"
            exit 1
        }
        
        Write-Host "📦 Installation de PostgreSQL..." -ForegroundColor Yellow
        choco install postgresql --confirm
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL installé avec succès!" -ForegroundColor Green
        } else {
            Write-Host "❌ Erreur lors de l'installation" -ForegroundColor Red
            exit 1
        }
    }
}

# Configuration PostgreSQL
Write-Host ""
Write-Host "🔧 Configuration PostgreSQL..." -ForegroundColor Cyan

# Démarrer le service PostgreSQL
Write-Host "🚀 Démarrage du service PostgreSQL..."
try {
    Start-Service postgresql* -ErrorAction Stop
    Write-Host "✅ Service PostgreSQL démarré" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible de démarrer le service automatiquement" -ForegroundColor Yellow
    Write-Host "Démarrez manuellement: services.msc -> postgresql"
}

# Installer les dépendances Python
Write-Host ""
Write-Host "🐍 Installation des dépendances Python..." -ForegroundColor Cyan

Write-Host "📦 Installation d'asyncpg..."
pip install asyncpg

Write-Host "📦 Installation de psycopg2..."
pip install psycopg2-binary

Write-Host ""
Write-Host "✅ Installation terminée!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Yellow
Write-Host "1. Exécutez: python migrate_to_postgresql.py"
Write-Host "2. Suivez les instructions de migration"
Write-Host "3. Redémarrez CereBloom"
Write-Host ""
Write-Host "🔑 Identifiants par défaut PostgreSQL:"
Write-Host "   Utilisateur: postgres"
Write-Host "   Mot de passe: postgres (ou celui défini lors de l'installation)"
