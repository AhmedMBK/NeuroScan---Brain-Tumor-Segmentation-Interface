# Script PowerShell pour installer l'API de gestion des patients

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation de l'API de Gestion des Patients" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "1. Vérification de Python..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Veuillez installer Python 3.11+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Vérification de pip..." -ForegroundColor Yellow

try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ Pip trouvé: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Pip non trouvé" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. Installation des dépendances..." -ForegroundColor Yellow

$packages = @("fastapi", "uvicorn[standard]", "pydantic[email]", "email-validator")

foreach ($package in $packages) {
    Write-Host "Installation de $package..." -ForegroundColor Blue
    try {
        pip install $package
        Write-Host "✅ $package installé" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erreur lors de l'installation de $package" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "4. Vérification de l'installation..." -ForegroundColor Yellow

$verifications = @(
    @{Module="fastapi"; Command="import fastapi; print('FastAPI version:', fastapi.__version__)"},
    @{Module="uvicorn"; Command="import uvicorn; print('Uvicorn installé avec succès')"},
    @{Module="pydantic"; Command="import pydantic; print('Pydantic version:', pydantic.__version__)"}
)

foreach ($verification in $verifications) {
    try {
        $result = python -c $verification.Command 2>&1
        Write-Host "✅ $($verification.Module): $result" -ForegroundColor Green
    } catch {
        Write-Host "❌ Problème avec $($verification.Module)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation terminée!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Pour démarrer l'API:" -ForegroundColor Yellow
Write-Host "python main_patients_api.py" -ForegroundColor White

Write-Host ""
Write-Host "Documentation Swagger UI:" -ForegroundColor Yellow
Write-Host "http://localhost:8001/docs" -ForegroundColor White

Write-Host ""
Write-Host "Appuyez sur une touche pour continuer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
