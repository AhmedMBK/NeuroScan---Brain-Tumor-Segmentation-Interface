@echo off
echo ========================================
echo Demarrage de l'API de Gestion des Patients
echo ========================================

echo.
echo Activation de l'environnement Conda...
call conda activate patients_api

echo.
echo Verification de l'environnement...
python -c "import sys; print('Python version:', sys.version)"
python -c "import fastapi; print('FastAPI pret')"

echo.
echo ========================================
echo Demarrage du serveur sur le port 8001...
echo ========================================
echo.
echo Documentation: http://localhost:8001/docs
echo API: http://localhost:8001
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo ========================================

python main_patients_api.py
