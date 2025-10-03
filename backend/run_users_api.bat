@echo off
echo ========================================
echo Demarrage de l'API Utilisateurs et Medecins
echo ========================================

echo.
echo Verification de l'environnement...
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import uvicorn; print('✅ Uvicorn OK')"
python -c "import pydantic; print('✅ Pydantic OK')"

echo.
echo ========================================
echo Demarrage du serveur sur le port 8002...
echo ========================================
echo.
echo 🌐 API: http://localhost:8002
echo 📖 Documentation: http://localhost:8002/docs
echo 🔐 Authentification: http://localhost:8002/auth/login
echo.
echo 👥 Comptes de test:
echo    Admin: admin / admin123
echo    Medecin 1: dr.martin / doctor123
echo    Medecin 2: dr.dubois / onco123
echo    Infirmiere: nurse.claire / nurse123
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo ========================================

python main_users_api.py
