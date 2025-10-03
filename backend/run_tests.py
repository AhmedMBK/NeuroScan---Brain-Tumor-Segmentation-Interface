#!/usr/bin/env python3
"""
🧪 Lanceur de Tests CereBloom
Script pour lancer facilement les tests de segmentation
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Vérifie les dépendances"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = [
        "numpy", "nibabel", "scipy", "sqlalchemy", "aiosqlite"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package}")
    
    if missing:
        print(f"\n📦 Installation des packages manquants: {missing}")
        for package in missing:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    return len(missing) == 0

def check_images():
    """Vérifie la présence des images"""
    print("\n📁 Vérification des images...")
    
    patient_id = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"
    images_dir = Path("uploads/medical_images") / patient_id
    
    if not images_dir.exists():
        print(f"❌ Dossier d'images non trouvé: {images_dir}")
        return False
    
    image_files = list(images_dir.glob("*.nii*"))
    print(f"   📄 {len(image_files)} fichiers trouvés:")
    
    for img_file in image_files:
        size_mb = img_file.stat().st_size / (1024 * 1024)
        print(f"      {img_file.name} ({size_mb:.1f} MB)")
    
    return len(image_files) >= 2

def run_test(test_script):
    """Lance un test spécifique"""
    print(f"\n🚀 Lancement de {test_script}")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, test_script
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_script} terminé avec succès")
        else:
            print(f"❌ {test_script} a échoué (code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement de {test_script}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧠 CEREBLOOM - LANCEUR DE TESTS")
    print("=" * 50)
    
    # Vérifier le répertoire de travail
    if not Path("cerebloom_main.py").exists():
        print("❌ Veuillez lancer ce script depuis le dossier backend/")
        return
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("❌ Problème avec les dépendances")
        return
    
    # Vérifier les images
    if not check_images():
        print("❌ Images non disponibles")
        print("💡 Uploadez d'abord des images via l'API ou Swagger")
        return
    
    # Menu de choix
    print("\n🎯 CHOISISSEZ UN TEST:")
    print("1. Test direct de segmentation (simulation)")
    print("2. Test avec loadmodel.py (votre modèle)")
    print("3. Les deux tests")
    print("0. Quitter")
    
    try:
        choice = input("\nVotre choix (0-3): ").strip()
        
        if choice == "0":
            print("👋 Au revoir!")
            return
        
        elif choice == "1":
            print("\n🧪 Test direct de segmentation...")
            run_test("test_direct_segmentation.py")
        
        elif choice == "2":
            print("\n🧪 Test avec loadmodel.py...")
            run_test("test_with_loadmodel.py")
        
        elif choice == "3":
            print("\n🧪 Lancement des deux tests...")
            print("\n--- TEST 1: Segmentation directe ---")
            run_test("test_direct_segmentation.py")
            
            print("\n--- TEST 2: Avec loadmodel.py ---")
            run_test("test_with_loadmodel.py")
        
        else:
            print("❌ Choix invalide")
            return
        
        # Afficher les résultats
        results_dir = Path("uploads/segmentation_results")
        if results_dir.exists():
            result_folders = list(results_dir.glob("*"))
            if result_folders:
                print(f"\n📁 RÉSULTATS DISPONIBLES ({len(result_folders)} dossiers):")
                for folder in sorted(result_folders, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                    files = list(folder.glob("*"))
                    print(f"   📂 {folder.name} ({len(files)} fichiers)")
                    for file in files:
                        size_kb = file.stat().st_size / 1024
                        print(f"      📄 {file.name} ({size_kb:.1f} KB)")
        
        print(f"\n🎉 Tests terminés!")
        print(f"📁 Consultez les résultats dans: uploads/segmentation_results/")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()
