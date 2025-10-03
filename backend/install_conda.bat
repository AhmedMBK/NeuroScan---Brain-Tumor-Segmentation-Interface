@echo off
echo.
echo ============================================================
echo 🧠 CEREBLOOM - Installation avec Conda
echo ============================================================
echo.

REM Vérifier si conda est installé
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Conda n'est pas installé ou pas dans le PATH
    echo.
    echo 💡 Veuillez installer Miniconda ou Anaconda :
    echo    • Miniconda: https://docs.conda.io/en/latest/miniconda.html
    echo    • Anaconda: https://www.anaconda.com/download
    echo.
    echo ⚠️  N'oubliez pas de cocher "Add to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

echo ✅ Conda détecté
conda --version
echo.

REM Créer l'environnement CereBloom
echo 📦 Création de l'environnement CereBloom...
conda env create -f environment.yml

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erreur lors de la création de l'environnement
    echo 💡 Essayez de mettre à jour conda : conda update conda
    pause
    exit /b 1
)

echo.
echo ✅ Environnement CereBloom créé avec succès !
echo.
echo 🚀 Pour activer l'environnement et lancer CereBloom :
echo    conda activate cerebloom
echo    python launch_cerebloom.py
echo.
echo 📍 Ou utilisez le script de lancement automatique :
echo    launch_cerebloom.bat
echo.
pause
