@echo off
echo ========================================
echo Installation Simple des Dependances
echo ========================================

echo.
echo Installation des packages avec pip...
pip install fastapi uvicorn "pydantic[email]" email-validator

echo.
echo Verification de l'installation...
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import uvicorn; print('✅ Uvicorn OK')"
python -c "import pydantic; print('✅ Pydantic OK')"

echo.
echo ========================================
echo Installation terminee!
echo ========================================
echo.
echo Pour demarrer l'API:
echo python main_patients_api.py
echo.
echo Documentation: http://localhost:8001/docs
echo ========================================

pause
