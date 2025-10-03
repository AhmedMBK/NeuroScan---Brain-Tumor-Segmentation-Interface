@echo off
echo ========================================
echo Installation Minimale - API Patients
echo ========================================

echo.
echo Installation des packages essentiels...
pip install fastapi uvicorn pydantic

echo.
echo Verification...
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import uvicorn; print('✅ Uvicorn OK')"
python -c "import pydantic; print('✅ Pydantic OK')"

echo.
echo ========================================
echo Installation terminee!
echo ========================================
echo.
echo Pour demarrer l'API:
echo python patients_api_simple.py
echo.
echo Documentation: http://localhost:8001/docs
echo ========================================

pause
