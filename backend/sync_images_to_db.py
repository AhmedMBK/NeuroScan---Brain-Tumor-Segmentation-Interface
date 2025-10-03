#!/usr/bin/env python3
"""
🔄 Synchronisation Images vers Base de Données
Script pour ajouter les images physiques dans la base de données
"""

import os
import sys
import asyncio
import uuid
from pathlib import Path
from datetime import datetime

# Imports CereBloom
from config.database import get_database
from models.database_models import MedicalImage, Patient
from sqlalchemy import select

PATIENT_ID = "stringd5f01d3b-b54b-43a2-ba3c-0b12c797affc"

def extract_modality_from_filename(filename):
    """Extrait la modalité du nom de fichier"""
    filename_lower = filename.lower()

    if 'flair' in filename_lower:
        return 'FLAIR'
    elif 't1ce' in filename_lower:
        return 'T1CE'
    elif 't2' in filename_lower:
        return 'T2'
    elif 't1' in filename_lower:
        return 'T1'
    else:
        return 'UNKNOWN'

async def sync_images_to_database():
    """Synchronise les images physiques avec la base de données"""
    print("🔄 SYNCHRONISATION IMAGES → BASE DE DONNÉES")
    print("=" * 60)

    async for db in get_database():
        try:
            # 1. Vérifier/créer le patient
            print(f"👤 Vérification du patient: {PATIENT_ID}")

            result = await db.execute(
                select(Patient).where(Patient.id == PATIENT_ID)
            )
            patient = result.scalar_one_or_none()

            if not patient:
                print("   📝 Création du patient...")
                # Importer les enums nécessaires
                from models.database_models import Gender

                patient = Patient(
                    id=PATIENT_ID,
                    first_name="Test",
                    last_name="Patient",
                    date_of_birth=datetime(1980, 1, 1).date(),
                    gender=Gender.MALE,
                    created_by_user_id="system",
                    created_at=datetime.now()
                )
                db.add(patient)
                await db.commit()
                print("   ✅ Patient créé")
            else:
                print("   ✅ Patient existe")

            # 2. Scanner les images physiques
            images_dir = Path("uploads/medical_images") / PATIENT_ID

            if not images_dir.exists():
                print(f"❌ Dossier d'images non trouvé: {images_dir}")
                return

            image_files = list(images_dir.glob("*.nii*"))
            print(f"📁 {len(image_files)} fichiers d'images trouvés")

            # 3. Vérifier les images déjà en base
            result = await db.execute(
                select(MedicalImage).where(MedicalImage.patient_id == PATIENT_ID)
            )
            existing_images = result.scalars().all()
            existing_paths = {img.file_path for img in existing_images}

            print(f"💾 {len(existing_images)} images déjà en base")

            # 4. Ajouter les nouvelles images
            added_count = 0

            for img_file in image_files:
                file_path_str = str(img_file)

                if file_path_str not in existing_paths:
                    # Extraire les informations
                    modality = extract_modality_from_filename(img_file.name)
                    file_size = img_file.stat().st_size

                    print(f"   📄 Ajout: {img_file.name} ({modality})")

                    # Créer l'entrée en base
                    medical_image = MedicalImage(
                        id=str(uuid.uuid4()),
                        patient_id=PATIENT_ID,
                        uploaded_by_user_id="system",  # Utilisateur système
                        modality=modality,
                        file_path=file_path_str,
                        file_name=img_file.name,
                        file_size=file_size,
                        image_metadata={
                            "synchronized": True,
                            "original_filename": img_file.name,
                            "sync_date": datetime.now().isoformat()
                        },
                        acquisition_date=datetime.now().date(),
                        body_part="BRAIN",
                        notes="Image synchronisée automatiquement",
                        is_processed=False,
                        uploaded_at=datetime.now()
                    )

                    db.add(medical_image)
                    added_count += 1
                else:
                    print(f"   ⏭️ Déjà en base: {img_file.name}")

            # 5. Sauvegarder les changements
            if added_count > 0:
                await db.commit()
                print(f"✅ {added_count} nouvelles images ajoutées en base")
            else:
                print("ℹ️ Aucune nouvelle image à ajouter")

            # 6. Vérification finale
            result = await db.execute(
                select(MedicalImage).where(MedicalImage.patient_id == PATIENT_ID)
            )
            final_images = result.scalars().all()

            print(f"\n📊 RÉSUMÉ:")
            print(f"   📁 Fichiers physiques: {len(image_files)}")
            print(f"   💾 Images en base: {len(final_images)}")
            print(f"   ➕ Ajoutées: {added_count}")

            print(f"\n📋 MODALITÉS DISPONIBLES:")
            modalities = {}
            for img in final_images:
                modality = img.modality
                if modality not in modalities:
                    modalities[modality] = []
                modalities[modality].append(img.file_name)

            for modality, files in modalities.items():
                print(f"   🎯 {modality}: {len(files)} fichier(s)")
                for file in files:
                    print(f"      📄 {file}")

            # Vérifier si prêt pour segmentation
            required_modalities = {"FLAIR", "T1CE"}
            available_modalities = set(modalities.keys())

            if required_modalities.issubset(available_modalities):
                print(f"\n✅ PRÊT POUR SEGMENTATION!")
                print(f"   Modalités requises disponibles: {required_modalities}")
            else:
                missing = required_modalities - available_modalities
                print(f"\n⚠️ Modalités manquantes pour segmentation optimale: {missing}")
                if len(available_modalities) >= 2:
                    print(f"   Segmentation possible avec: {available_modalities}")

            return len(final_images)

        except Exception as e:
            print(f"❌ Erreur lors de la synchronisation: {e}")
            import traceback
            traceback.print_exc()
            return 0

        # Sortir de la boucle après le premier traitement
        break

if __name__ == "__main__":
    print("🔄 CereBloom - Synchronisation Images")

    result_count = asyncio.run(sync_images_to_database())

    if result_count > 0:
        print(f"\n🎉 SYNCHRONISATION RÉUSSIE!")
        print(f"💡 Vous pouvez maintenant lancer les tests de segmentation:")
        print(f"   python test_direct_segmentation.py")
        print(f"   python test_with_loadmodel.py")
    else:
        print(f"\n❌ ÉCHEC DE LA SYNCHRONISATION")
        print(f"💡 Vérifiez que les images sont présentes dans uploads/medical_images/")
