#!/usr/bin/env python3
"""
🧠 CereBloom - Script de Lancement Optimisé
Lance l'application avec vérifications préalables
"""

import sys
import os
import asyncio
import uvicorn
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.insert(0, str(Path(__file__).parent))

def print_banner():
    """Affiche la bannière CereBloom"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    🧠 CEREBLOOM v2.0.0                      ║
    ║                                                              ║
    ║        Application de Segmentation de Tumeurs Cérébrales    ║
    ║                  avec Modèle U-Net Kaggle                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_critical_files():
    """Vérifie les fichiers critiques"""
    print("🔍 Vérification des fichiers critiques...")
    
    critical_files = [
        "cerebloom_main.py",
        "config/settings.py",
        "config/database.py",
        "services/ai_segmentation_service.py",
        "routers/ai_segmentation_router.py"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        return False
    
    print("✅ Tous les fichiers critiques sont présents")
    return True

def check_model():
    """Vérifie la présence du modèle"""
    print("\n🧠 Vérification du modèle U-Net...")
    
    model_path = Path("models/my_model.h5")
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Modèle trouvé: {size_mb:.1f} MB")
        return True
    else:
        print("  ⚠️  Modèle non trouvé - Fonctionnement en mode simulation")
        print("     💡 Placez votre my_model.h5 dans models/ pour activer l'IA")
        return False

def setup_environment():
    """Configure l'environnement"""
    print("\n⚙️  Configuration de l'environnement...")
    
    # Créer les dossiers nécessaires
    directories = [
        "uploads/medical_images",
        "uploads/segmentation_results",
        "uploads/reports",
        "temp",
        "logs",
        "static",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("  ✅ Dossiers créés")
    
    # Variables d'environnement
    os.environ.setdefault("PYTHONPATH", str(Path.cwd()))
    print("  ✅ Variables d'environnement configurées")

def test_imports():
    """Test des imports critiques"""
    print("\n📦 Test des imports critiques...")
    
    try:
        # Test FastAPI
        import fastapi
        print(f"  ✅ FastAPI {fastapi.__version__}")
        
        # Test TensorFlow
        import tensorflow as tf
        print(f"  ✅ TensorFlow {tf.__version__}")
        
        # Test des modules CereBloom
        from config.settings import settings
        print("  ✅ Configuration CereBloom")
        
        from services.ai_segmentation_service import AISegmentationService
        print("  ✅ Service de segmentation IA")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        print("     💡 Exécutez: pip install -r requirements_cerebloom.txt")
        return False

async def test_database():
    """Test de la base de données"""
    print("\n🗄️  Test de la base de données...")
    
    try:
        from config.database import init_database, get_database
        
        # Initialisation de la base de données
        await init_database()
        print("  ✅ Base de données initialisée")
        
        # Test de connexion
        async for db in get_database():
            print("  ✅ Connexion à la base de données réussie")
            break
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur base de données: {e}")
        return False

def show_startup_info():
    """Affiche les informations de démarrage"""
    print("\n" + "="*60)
    print("🚀 CEREBLOOM PRÊT À DÉMARRER")
    print("="*60)
    print("📍 URLs importantes:")
    print("   • API: http://localhost:8000")
    print("   • Documentation Swagger: http://localhost:8000/docs")
    print("   • Redoc: http://localhost:8000/redoc")
    print("   • Health Check: http://localhost:8000/health")
    print("\n🔐 Endpoints principaux:")
    print("   • Authentification: /api/v1/auth/")
    print("   • Patients: /api/v1/patients/")
    print("   • Images médicales: /api/v1/images/")
    print("   • 🧠 Segmentation IA: /api/v1/segmentation/")
    print("\n👥 Compte admin par défaut:")
    print("   • Email: admin@cerebloom.com")
    print("   • Mot de passe: admin123")
    print("   ⚠️  Changez ce mot de passe en production !")
    print("\n" + "="*60)

async def main():
    """Fonction principale de lancement"""
    print_banner()
    
    # Vérifications préalables
    checks = [
        ("Fichiers critiques", check_critical_files),
        ("Modèle U-Net", check_model),
        ("Environnement", lambda: (setup_environment(), True)[1]),
        ("Imports", test_imports)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ Échec de la vérification: {check_name}")
            print("🛑 Arrêt du lancement")
            return False
    
    # Test asynchrone de la base de données
    if not await test_database():
        print("\n❌ Échec du test de base de données")
        print("🛑 Arrêt du lancement")
        return False
    
    show_startup_info()
    
    # Lancement du serveur
    print("🚀 Lancement du serveur CereBloom...")
    print("   Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        # Configuration Uvicorn
        config = uvicorn.Config(
            "cerebloom_main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt de CereBloom...")
        print("👋 Au revoir !")
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt forcé")
        sys.exit(0)
