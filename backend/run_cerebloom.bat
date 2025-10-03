@echo off
echo 🧠 CereBloom - Démarrage du Backend
echo =====================================

REM Vérification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python 3.10+ depuis https://python.org
    pause
    exit /b 1
)

REM Création de l'environnement virtuel si nécessaire
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

REM Activation de l'environnement virtuel
echo 🔄 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installation des dépendances
echo 📥 Installation des dépendances...
pip install -r requirements_cerebloom.txt

REM Vérification du modèle IA
if not exist "models\my_model.h5" (
    echo ⚠️  ATTENTION: Modèle IA non trouvé dans models\my_model.h5
    echo Veuillez copier votre modèle U-Net Kaggle dans le dossier models\
    echo.
    echo Voulez-vous continuer sans le modèle ? (o/n)
    set /p continue="Réponse: "
    if /i not "%continue%"=="o" (
        echo Arrêt du démarrage.
        pause
        exit /b 1
    )
)

REM Création des dossiers nécessaires
echo 📁 Création des dossiers...
if not exist "uploads" mkdir uploads
if not exist "uploads\medical_images" mkdir uploads\medical_images
if not exist "uploads\segmentation_results" mkdir uploads\segmentation_results
if not exist "uploads\reports" mkdir uploads\reports
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "static" mkdir static

REM Démarrage de l'application
echo 🚀 Démarrage de CereBloom Backend...
echo.
echo 📍 L'API sera disponible sur: http://localhost:8000
echo 📖 Documentation Swagger: http://localhost:8000/docs
echo 🔍 ReDoc: http://localhost:8000/redoc
echo.
echo 👤 Compte admin par défaut:
echo    Email: admin@cerebloom.com
echo    Mot de passe: admin123
echo.
echo ⚠️  Changez le mot de passe admin en production !
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python cerebloom_main.py

echo.
echo 🛑 Serveur arrêté
pause
