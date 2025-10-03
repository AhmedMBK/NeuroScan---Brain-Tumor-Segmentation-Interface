#!/usr/bin/env python3
"""
🧪 Test Simple - Diagnostic CereBloom
"""

import os
import sys
from pathlib import Path

print("🧠 CereBloom - Test Simple")
print("=" * 40)

# 1. Vérifier le répertoire
print(f"📁 Répertoire: {os.getcwd()}")
print(f"📄 Fichiers Python: {list(Path('.').glob('*.py'))[:5]}")

# 2. Tester les imports de base
print("\n📦 Test des imports:")
try:
    import numpy as np
    print("   ✅ numpy")
except ImportError as e:
    print(f"   ❌ numpy: {e}")

try:
    import nibabel as nib
    print("   ✅ nibabel")
except ImportError as e:
    print(f"   ❌ nibabel: {e}")

try:
    import asyncio
    print("   ✅ asyncio")
except ImportError as e:
    print(f"   ❌ asyncio: {e}")

try:
    from sqlalchemy import select
    print("   ✅ sqlalchemy")
except ImportError as e:
    print(f"   ❌ sqlalchemy: {e}")

# 3. Tester les imports CereBloom
print("\n🧠 Test des imports CereBloom:")
try:
    from config.database import get_database
    print("   ✅ config.database")
except ImportError as e:
    print(f"   ❌ config.database: {e}")

try:
    from models.database_models import MedicalImage
    print("   ✅ models.database_models")
except ImportError as e:
    print(f"   ❌ models.database_models: {e}")

# 4. Vérifier la base de données
print("\n💾 Test de la base de données:")
db_file = Path("cerebloom.db")
if db_file.exists():
    size_mb = db_file.stat().st_size / (1024 * 1024)
    print(f"   ✅ Base de données: {size_mb:.2f} MB")
else:
    print("   ❌ Base de données non trouvée")

# 5. Vérifier les images
print("\n📁 Test des images:")
patient_id = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"
images_dir = Path("uploads/medical_images") / patient_id

if images_dir.exists():
    image_files = list(images_dir.glob("*.nii*"))
    print(f"   ✅ Dossier images: {len(image_files)} fichiers")
    for img_file in image_files[:3]:
        size_mb = img_file.stat().st_size / (1024 * 1024)
        print(f"      📄 {img_file.name} ({size_mb:.1f} MB)")
else:
    print(f"   ❌ Dossier images non trouvé: {images_dir}")

# 6. Test simple de connexion base de données
print("\n🔗 Test de connexion base de données:")
try:
    import asyncio
    from config.database import get_database
    from models.database_models import MedicalImage
    from sqlalchemy import select
    
    async def test_db():
        async for db in get_database():
            try:
                result = await db.execute(select(MedicalImage))
                images = result.scalars().all()
                print(f"   ✅ Connexion DB réussie: {len(images)} images trouvées")
                
                # Afficher quelques images
                for img in images[:3]:
                    print(f"      📄 {img.modality}: {img.file_name}")
                
                return len(images)
            except Exception as e:
                print(f"   ❌ Erreur requête DB: {e}")
                return 0
            break
    
    # Lancer le test async
    image_count = asyncio.run(test_db())
    
    if image_count > 0:
        print(f"\n✅ DIAGNOSTIC RÉUSSI - {image_count} images disponibles")
        print("🚀 Vous pouvez lancer les tests de segmentation")
    else:
        print("\n❌ PROBLÈME - Aucune image trouvée")
        print("💡 Uploadez d'abord des images via l'API")
        
except Exception as e:
    print(f"   ❌ Erreur test DB: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Test terminé!")
