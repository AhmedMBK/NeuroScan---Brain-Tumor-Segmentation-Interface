# Script PowerShell pour démarrer l'API de gestion des patients

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Démarrage de l'API de Gestion des Patients" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Vérification de l'environnement..." -ForegroundColor Yellow

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé" -ForegroundColor Red
    exit 1
}

# Vérifier FastAPI
try {
    python -c "import fastapi" 2>&1 | Out-Null
    Write-Host "✅ FastAPI disponible" -ForegroundColor Green
} catch {
    Write-Host "❌ FastAPI non installé. Exécutez d'abord install_patients_api.ps1" -ForegroundColor Red
    exit 1
}

# Vérifier que le fichier principal existe
if (Test-Path "main_patients_api.py") {
    Write-Host "✅ Fichier principal trouvé" -ForegroundColor Green
} else {
    Write-Host "❌ main_patients_api.py non trouvé" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Démarrage du serveur sur le port 8001..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "🌐 API disponible sur: http://localhost:8001" -ForegroundColor Green
Write-Host "📖 Documentation Swagger: http://localhost:8001/docs" -ForegroundColor Green
Write-Host "📚 ReDoc: http://localhost:8001/redoc" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Démarrer l'API
try {
    python main_patients_api.py
} catch {
    Write-Host ""
    Write-Host "❌ Erreur lors du démarrage du serveur" -ForegroundColor Red
    Write-Host "Vérifiez les logs ci-dessus pour plus de détails" -ForegroundColor Yellow
}
