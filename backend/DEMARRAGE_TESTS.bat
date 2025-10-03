@echo off
echo ========================================
echo TESTS SWAGGER - API UTILISATEURS
echo ========================================

echo.
echo 🚀 Demarrage de l'API...
start /B python main_users_api.py

echo.
echo ⏳ Attente du demarrage du serveur...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 🌐 API PRETE POUR LES TESTS !
echo ========================================

echo.
echo 📖 Documentation Swagger: 
echo    http://localhost:8002/docs
echo.
echo 🔐 Comptes de test disponibles:
echo    Admin:      admin / admin123
echo    Medecin 1:  dr.martin / doctor123  
echo    Medecin 2:  dr.dubois / onco123
echo    Infirmiere: nurse.claire / nurse123
echo.
echo 📋 Guide de test:
echo    1. Ouvrir http://localhost:8002/docs
echo    2. Tester GET /health
echo    3. Se connecter avec POST /auth/login
echo    4. Copier le token et cliquer "Authorize"
echo    5. Tester les autres endpoints
echo.
echo 📄 Scripts de body complets:
echo    Voir le fichier: EXEMPLES_TESTS_SWAGGER.md
echo.
echo ========================================

echo.
echo Appuyez sur une touche pour ouvrir Swagger...
pause >nul

start http://localhost:8002/docs

echo.
echo ========================================
echo Interface Swagger ouverte !
echo ========================================
echo.
echo Pour arreter l'API: Ctrl+C dans cette fenetre
echo.

pause
