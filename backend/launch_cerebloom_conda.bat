@echo off
echo 🧠 CereBloom - Lancement avec Conda
echo ====================================

REM Vérification de Conda
where conda >nul 2>&1
if errorlevel 1 (
    echo ❌ Conda n'est pas installé ou pas dans le PATH
    echo Veuillez installer Anaconda ou Miniconda
    pause
    exit /b 1
)

echo 📦 Vérification de l'environnement cerebloom...

REM Vérifier si l'environnement existe
conda info --envs | findstr "cerebloom" >nul 2>&1
if errorlevel 1 (
    echo 🔧 Création de l'environnement cerebloom...
    conda env create -f environment.yml
    if errorlevel 1 (
        echo ❌ Erreur lors de la création de l'environnement
        pause
        exit /b 1
    )
) else (
    echo ✅ Environnement cerebloom trouvé
)

echo 🔄 Activation de l'environnement cerebloom...
call conda activate cerebloom

REM Vérification du modèle IA
if exist "models\my_model.h5" (
    echo ✅ Modèle U-Net trouvé: models\my_model.h5
) else (
    echo ⚠️  ATTENTION: Modèle IA non trouvé dans models\my_model.h5
    echo Le modèle semble être présent, continuons...
)

REM Vérification des dossiers
echo 📁 Vérification des dossiers...
if not exist "uploads" mkdir uploads
if not exist "uploads\medical_images" mkdir uploads\medical_images
if not exist "uploads\segmentation_results" mkdir uploads\segmentation_results
if not exist "uploads\reports" mkdir uploads\reports
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "static" mkdir static

echo 🚀 Démarrage de CereBloom Backend avec Conda...
echo.
echo 📍 L'API sera disponible sur: http://localhost:8000
echo 📖 Documentation Swagger: http://localhost:8000/docs
echo 🔍 ReDoc: http://localhost:8000/redoc
echo.
echo 👤 Compte admin par défaut:
echo    Email: admin@cerebloom.com
echo    Mot de passe: admin123
echo.
echo 🧠 Votre modèle U-Net Kaggle sera chargé automatiquement
echo.
echo ⚠️  Changez le mot de passe admin en production !
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python "C:\Users\DELL\Desktop\cerebloom-classify-87-main\backend\cerebloom_main.py"

echo.
echo 🛑 Serveur arrêté
pause
