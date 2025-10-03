#!/usr/bin/env powershell

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧠 CereBloom - Démarrage avec MLOps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Installation des dépendances MLOps..." -ForegroundColor Yellow
try {
    pip install mlflow==2.8.1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MLflow installé avec succès" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors de l'installation de MLflow" -ForegroundColor Red
        Read-Host "Appuyez sur Entrée pour continuer..."
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors de l'installation de MLflow" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer..."
    exit 1
}

Write-Host ""
Write-Host "🚀 Démarrage de CereBloom avec MLOps..." -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard MLOps sera disponible sur: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🌐 API CereBloom sera disponible sur: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 Documentation API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

python cerebloom_main.py

Write-Host ""
Write-Host "👋 CereBloom arrêté" -ForegroundColor Yellow
Read-Host "Appuyez sur Entrée pour fermer..."
