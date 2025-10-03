@echo off
echo.
echo ========================================
echo 🧠 CereBloom - Démarrage avec MLOps
echo ========================================
echo.

echo 📦 Installation des dépendances MLOps...
pip install mlflow==2.8.1
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation de MLflow
    pause
    exit /b 1
)

echo.
echo ✅ MLflow installé avec succès
echo.

echo 🚀 Démarrage de CereBloom avec MLOps...
echo.
echo 📊 Dashboard MLOps sera disponible sur: http://localhost:5000
echo 🌐 API CereBloom sera disponible sur: http://localhost:8000
echo 📖 Documentation API: http://localhost:8000/docs
echo.

python cerebloom_main.py

echo.
echo 👋 CereBloom arrêté
pause
