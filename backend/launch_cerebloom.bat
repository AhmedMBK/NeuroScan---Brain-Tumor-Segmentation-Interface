@echo off
echo.
echo ============================================================
echo 🧠 CEREBLOOM - Lancement avec Conda
echo ============================================================
echo.

REM Vérifier si conda est installé
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Conda n'est pas installé
    echo 💡 Exécutez d'abord install_conda.bat
    pause
    exit /b 1
)

REM Vérifier si l'environnement existe
conda info --envs | findstr "cerebloom" >nul
if %errorlevel% neq 0 (
    echo ❌ Environnement 'cerebloom' non trouvé
    echo 💡 Exécutez d'abord install_conda.bat
    pause
    exit /b 1
)

echo ✅ Activation de l'environnement CereBloom...
call conda activate cerebloom

echo.
echo 🧠 Lancement de CereBloom...
echo 📍 L'application sera disponible sur : http://localhost:8000
echo 📚 Documentation Swagger : http://localhost:8000/docs
echo.
echo ⚠️  Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python launch_cerebloom.py

echo.
echo 👋 CereBloom arrêté
pause
