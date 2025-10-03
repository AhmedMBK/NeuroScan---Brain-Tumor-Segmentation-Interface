@echo off
echo ========================================
echo Tests de l'API de Gestion des Patients
echo ========================================

echo.
echo Activation de l'environnement Conda...
call conda activate patients_api

echo.
echo Verification de l'environnement de test...
python -c "import pytest; print('Pytest disponible')"
python -c "import httpx; print('HTTPX disponible')"

echo.
echo ========================================
echo Execution des tests...
echo ========================================

python test_patients_api.py

echo.
echo ========================================
echo Tests termines!
echo ========================================

pause
