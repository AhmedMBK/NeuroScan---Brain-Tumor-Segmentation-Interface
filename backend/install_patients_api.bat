@echo off
echo ========================================
echo Installation de l'API de Gestion des Patients
echo ========================================

echo.
echo 1. Initialisation de Conda...
call conda init cmd.exe
call conda init powershell

echo.
echo 2. Creation de l'environnement Conda...
call conda create -n patients_api python=3.11 -y

echo.
echo 3. Activation de l'environnement...
call conda activate patients_api

echo.
echo 4. Installation des dependances avec conda et pip...
call conda install -c conda-forge fastapi uvicorn -y
pip install pydantic[email]==2.5.0
pip install email-validator==2.1.0

echo.
echo 5. Verification de l'installation...
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
python -c "import uvicorn; print('Uvicorn installe avec succes')"
python -c "import pydantic; print('Pydantic version:', pydantic.__version__)"

echo.
echo ========================================
echo Installation terminee avec succes!
echo ========================================
echo.
echo Pour demarrer l'API:
echo 1. conda activate patients_api
echo 2. python main_patients_api.py
echo.
echo Documentation: http://localhost:8001/docs
echo ========================================

pause
