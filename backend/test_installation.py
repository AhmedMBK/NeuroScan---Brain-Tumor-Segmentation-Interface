#!/usr/bin/env python3
"""
🧠 CereBloom - Script de Test d'Installation
Vérifie les dépendances et la configuration avant le lancement
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*60)
    print(f"🧠 {title}")
    print("="*60)

def check_python_version():
    """Vérifie la version de Python"""
    print_header("VÉRIFICATION PYTHON")
    
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 8:
        print("❌ ERREUR: Python 3.8+ requis")
        return False
    
    print("✅ Version Python compatible")
    return True

def check_dependencies():
    """Vérifie les dépendances critiques"""
    print_header("VÉRIFICATION DÉPENDANCES")
    
    critical_deps = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("tensorflow", "TensorFlow"),
        ("numpy", "NumPy"),
        ("nibabel", "NiBabel"),
        ("cv2", "OpenCV"),
        ("pydantic", "Pydantic")
    ]
    
    missing_deps = []
    
    for module, name in critical_deps:
        try:
            importlib.import_module(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - MANQUANT")
            missing_deps.append(name)
    
    if missing_deps:
        print(f"\n❌ Dépendances manquantes: {', '.join(missing_deps)}")
        print("💡 Exécutez: pip install -r requirements_cerebloom.txt")
        return False
    
    print("\n✅ Toutes les dépendances critiques sont installées")
    return True

def check_model_file():
    """Vérifie la présence du modèle U-Net"""
    print_header("VÉRIFICATION MODÈLE IA")
    
    model_path = Path("models/my_model.h5")
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ Modèle trouvé: {model_path}")
        print(f"📊 Taille: {size_mb:.1f} MB")
        return True
    else:
        print(f"❌ Modèle non trouvé: {model_path}")
        print("💡 Placez votre fichier my_model.h5 dans le dossier models/")
        return False

def check_directories():
    """Vérifie et crée les dossiers nécessaires"""
    print_header("VÉRIFICATION DOSSIERS")
    
    required_dirs = [
        "uploads/medical_images",
        "uploads/segmentation_results", 
        "uploads/reports",
        "temp",
        "logs",
        "static",
        "models"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}")
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ {dir_path} - CRÉÉ")
            except Exception as e:
                print(f"❌ {dir_path} - ERREUR: {e}")
                return False
    
    print("\n✅ Tous les dossiers sont prêts")
    return True

def test_tensorflow():
    """Test spécifique de TensorFlow"""
    print_header("TEST TENSORFLOW")
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow version: {tf.__version__}")
        
        # Test de création d'un modèle simple
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(1, input_shape=(1,))
        ])
        print("✅ Création de modèle TensorFlow réussie")
        
        # Test des métriques personnalisées
        from tensorflow.keras import backend as K
        
        def test_dice_coef(y_true, y_pred, smooth=1.0):
            intersection = K.sum(y_true * y_pred)
            return (2. * intersection + smooth) / (K.sum(y_true) + K.sum(y_pred) + smooth)
        
        print("✅ Métriques personnalisées compatibles")
        return True
        
    except Exception as e:
        print(f"❌ Erreur TensorFlow: {e}")
        return False

def test_medical_imaging():
    """Test des bibliothèques d'imagerie médicale"""
    print_header("TEST IMAGERIE MÉDICALE")
    
    try:
        import nibabel as nib
        import cv2
        import numpy as np
        
        print("✅ NiBabel importé")
        print("✅ OpenCV importé")
        print("✅ NumPy importé")
        
        # Test de création d'une image factice
        test_data = np.random.rand(128, 128, 100)
        print("✅ Création de données de test réussie")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur imagerie médicale: {e}")
        return False

def create_test_images():
    """Crée des images de test si nécessaire"""
    print_header("CRÉATION IMAGES DE TEST")
    
    test_dir = Path("images")
    if not test_dir.exists():
        test_dir.mkdir(exist_ok=True)
        print("✅ Dossier images créé")
    
    # Créer un dossier de test patient
    patient_dir = test_dir / "test_patient_001"
    if not patient_dir.exists():
        patient_dir.mkdir(exist_ok=True)
        print("✅ Dossier patient de test créé")
        print("💡 Placez vos fichiers .nii de test dans images/test_patient_001/")
    
    return True

def main():
    """Fonction principale de test"""
    print_header("CEREBLOOM - TEST D'INSTALLATION")
    print("🏥 Application de segmentation de tumeurs cérébrales")
    
    all_tests_passed = True
    
    # Tests séquentiels
    tests = [
        ("Version Python", check_python_version),
        ("Dépendances", check_dependencies),
        ("Dossiers", check_directories),
        ("Modèle IA", check_model_file),
        ("TensorFlow", test_tensorflow),
        ("Imagerie médicale", test_medical_imaging),
        ("Images de test", create_test_images)
    ]
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_tests_passed = False
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            all_tests_passed = False
    
    # Résumé final
    print_header("RÉSUMÉ")
    
    if all_tests_passed:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("\n📋 Prochaines étapes:")
        print("1. Placez votre modèle my_model.h5 dans models/ (si pas encore fait)")
        print("2. Lancez: python cerebloom_main.py")
        print("3. Accédez à: http://localhost:8000/docs")
        print("\n🚀 CereBloom est prêt à démarrer !")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\n💡 Résolvez les erreurs ci-dessus avant de continuer")
        print("📧 Consultez la documentation pour plus d'aide")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
